from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate

from .base_agent import BaseExpertAgent
from typing import Dict, Any

from ..prompts.code_review_prompt import CODE_REVIEW_SYSTEM_PROMPT
from ..schemas.code_review_schema import CodeReviewOutput


class CodeReviewAgent(BaseExpertAgent):

    def __init__(self, rag_service, llm):
        super().__init__(rag_service)
        self.llm = llm

    def run(self, input_data: Dict[str, Any]) -> CodeReviewOutput:
        # 1. 构建 Prompt（无需 RAG）
        prompt = ChatPromptTemplate.from_messages([
            ("system", CODE_REVIEW_SYSTEM_PROMPT),
            ("human", "{student_code}")
        ])

        parser = JsonOutputParser(pydantic_object=CodeReviewOutput)

        # 2. 执行 LLM
        chain = (
                prompt
                | self.llm
                | parser
        )

        result = chain.invoke({
            "student_code": input_data["student_code"]
        })

        return result