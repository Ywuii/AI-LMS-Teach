from typing import Dict, Any, Type

from experts.agents.code_review_agent import CodeReviewAgent
from experts.agents.lesson_plan_agent import LessonPlanAgent
from experts.services.llm_provider import LLMProvider
from rag_service.rag_service import RAGService

from experts.agents.question_agent import QuestionAgent



class AgentService:
    """
    专家智能体统一调度服务
    """

    def __init__(self):
        self.llm = LLMProvider.get_llm()
        self.rag_service = RAGService()

    # -----------------------------
    # 统一执行入口
    # -----------------------------
    def run_agent(
        self,
        agent_type: str,
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        agent_type:
            - question
            - lesson_plan
            - code_review
        """
        agent_cls = self._get_agent(agent_type)
        agent = agent_cls(
            rag_service=self.rag_service,
            llm=self.llm
        )

        result = agent.run(input_data)
        return result

    # -----------------------------
    # Agent 注册表
    # -----------------------------
    def _get_agent(self, agent_type: str) -> Type:
        registry = {
            "question": QuestionAgent,
            "lesson_plan": LessonPlanAgent,
            "code_review": CodeReviewAgent,
        }

        if agent_type not in registry:
            raise ValueError(f"不支持的专家智能体类型: {agent_type}")

        return registry[agent_type]

    # -----------------------------
    # 快捷方法（可选）
    # -----------------------------
    def generate_question(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        return self.run_agent("question", input_data)

    def generate_lesson_plan(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        return self.run_agent("lesson_plan", input_data)

    def code_review(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        return self.run_agent("code_review", input_data)