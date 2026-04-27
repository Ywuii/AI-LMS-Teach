from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate

from .base_agent import BaseExpertAgent
from typing import Dict, Any

from ..prompts.question_prompt import QUESTION_SYSTEM_PROMPT
from ..schemas.question_schema import QuestionOutput
from ..tools.rag_tool import RAGTool


class QuestionAgent(BaseExpertAgent):

    def __init__(self, rag_service, llm):
        super().__init__(rag_service)
        self.llm = llm
        self.rag_tool = RAGTool(rag_service)

    def run(self, input_data: Dict[str, Any]) -> QuestionOutput:
        # 1. 从 RAG 检索相关知识
        context = self.rag_tool.retrieve(
            question=input_data["knowledge_point"],
            domain="question"
        )
        print(f"检索得到的结果{context}")
        # 2. 构建 Prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", QUESTION_SYSTEM_PROMPT),
            ("human", "{context}")
        ])
        parser = JsonOutputParser(pydantic_object=QuestionOutput)

        # 3. 执行 LLM
        chain = (
                prompt
                | self.llm
                | parser
        )
        result = chain.invoke({
            "chapter": input_data["chapter"],
            "knowledge_type": input_data["knowledge_type"],
            "knowledge_point": input_data["knowledge_point"],
            "question_type": input_data.get("question_type", "选择题"),
            "question_count": input_data.get("question_count", 1),
            "difficulty": input_data["difficulty"],
            "use_kg": input_data.get("use_kg", True),
            "use_rag": input_data.get("use_rag", True),
            "include_answer": input_data.get("include_answer", True),
            "include_explanation": input_data.get("include_explanation", True),
            "output_format": "json",
            "context": context
        })

        # 4. 结构化输出
        return result