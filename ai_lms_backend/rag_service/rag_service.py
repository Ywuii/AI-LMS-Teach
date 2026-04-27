# api/services/rag_service.py
from .triple_extractor_spacy import TripleExtractorSpacy
from .vector_store import VectorStoreService
from .knowledge_graph import KnowledgeGraphService
from .rag_kg_chain import build_rag_kg_chain, ask_question, ask_question_stream, format_docs, format_docs_with_limit
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class RAGService:
    """RAG问答服务（主服务类）"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            self.vector_store = VectorStoreService()
            self.kg_service = KnowledgeGraphService()
            self.rag_chain = None
            self._initialized = False

    def initialize(self):
        """初始化RAG服务（懒加载）"""
        if self._initialized:
            return

        logger.info("初始化RAG服务...")

        try:
            # 1. 初始化向量存储
            self.vector_store.initialize()

            # 2. 初始化知识图谱
            self.kg_service.initialize()

            # 3. 构建RAG链
            self.rag_chain = build_rag_kg_chain()

            self.kg = self.kg_service.get_kg()

            self.tes = TripleExtractorSpacy(self.kg)

            self._initialized = True
            logger.info("RAG服务初始化完成")

        except Exception as e:
            logger.error(f"RAG服务初始化失败: {e}")
            # 可以根据业务需求决定是否抛出异常
            # 如果某些组件初始化失败，可以提供降级服务

    def query(self, question: str, config: Dict[str, Any] = None) -> Dict[str, Any]:

        if not self._initialized:
            self.initialize()

        try:
            # 获取组件
            retriever = self.vector_store.get_retriever()

            if not retriever or not self.kg:
                raise ValueError("向量存储或知识图谱未初始化")

            print(config)
            answer_text = ask_question(self.rag_chain, retriever, self.kg, config, question)

            return {
                "answer": str(answer_text) if answer_text else "无回答",
                "success": True
            }

        except Exception as e:
            logger.error(f"RAG查询失败: {e}")
            return {
                "answer": f"抱歉，处理问题时发生错误: {str(e)}",
                "success": False,
                "error": str(e)
            }

    def query_stream(self, question: str, config: Dict[str, Any] = None) -> Dict[str, Any]:

        if not self._initialized:
            self.initialize()

        try:
            # 获取组件
            retriever = self.vector_store.get_retriever()
            kg = self.kg_service.get_kg()


            if not retriever or not kg:
                raise ValueError("向量存储或知识图谱未初始化")

            return ask_question_stream(self.rag_chain, retriever, kg, self.tes, config, question)

        except Exception as e:
            logger.error(f"RAG查询失败: {e}")
            return {
                "answer": f"抱歉，处理问题时发生错误: {str(e)}",
                "success": False,
                "error": str(e)
            }

    def is_ready(self) -> bool:
        """检查服务是否就绪"""
        return self._initialized

    # api/services/rag_service.py

    def retrieve_kg(self, question: str, domain: str = "general") -> List[Dict[str, Any]]:
        """
        仅从知识图谱检索
        """
        if not self._initialized:
            self.initialize()

        entities_in_question = self.tes.named_entity_recognition(question)

        kg_contexts = []
        for ent in entities_in_question:
            relations = self.kg.query_relations_agent(ent, domain=domain)
            if relations:
                kg_contexts.append(
                    f"{ent} 的相关关系有：{', '.join(relations)}"
                )

        return kg_contexts

    def retrieve_vector(self, question: str) -> List[Dict[str, Any]]:
        retriever = self.vector_store.get_retriever()
        rag_docs = retriever.invoke(question)
        rag_context = format_docs_with_limit(rag_docs)
        return [{"content": rag_context, "metadata": {}}]
