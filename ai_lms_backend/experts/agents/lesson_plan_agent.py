from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

from .base_agent import BaseExpertAgent
from typing import Dict, Any

from ..prompts.lesson_plan_prompt import LESSON_PLAN_SYSTEM_PROMPT
from ..schemas.lesson_plan_schema import LessonPlanOutput
from ..tools.rag_tool import RAGTool


class LessonPlanAgent(BaseExpertAgent):

    def __init__(self, rag_service, llm):
        super().__init__(rag_service)
        self.llm = llm
        self.rag_tool = RAGTool(rag_service)

    def run(self, input_data: Dict[str, Any]) -> LessonPlanOutput:
        # 1️⃣ RAG 检索
        context = self.rag_tool.retrieve(
            question=f"{input_data['chapter']} {input_data['section_title']}",
            domain="lesson_plan"
        )

        print("[LessonPlanAgent] RAG 上下文：", context)

        # 2️⃣ Prompt（✅ 明确变量注入）
        prompt = ChatPromptTemplate.from_messages([
            ("system", LESSON_PLAN_SYSTEM_PROMPT),
            ("human", """
                以下是与本次教案生成相关的参考资料：
                {context}
                
                请严格按照系统提示词中的 JSON 规范生成教案。
            """)
        ])

        # 3️⃣ 输出解析器
        parser = JsonOutputParser(pydantic_object=LessonPlanOutput)

        # 4️⃣ Chain（✅ 正确传参）
        chain = (
                prompt
                | self.llm
                | parser
        )

        result: LessonPlanOutput = chain.invoke({
            "chapter": input_data["chapter"],
            "section_title": input_data["section_title"],
            "student_level": input_data.get("student_level", "入门"),
            "class_hours": input_data.get("class_hours", 90),
            "teaching_style": input_data.get("teaching_style", "案例驱动"),
            "context": context
        })

        return result