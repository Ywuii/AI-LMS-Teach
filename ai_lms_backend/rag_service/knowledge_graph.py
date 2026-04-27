import os

from .neo4jKG import neo4jKG
import logging

logger = logging.getLogger(__name__)


class KnowledgeGraphService:
    """知识图谱服务（单例）"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.kg = None
        self._initialized = False

    def initialize(self):
        """初始化知识图谱"""
        if self._initialized and self.kg is not None:
            return

        try:
            # 从环境变量或配置读取
            uri = os.getenv("NEO4J_URI", "neo4j://localhost:7687")
            username = os.getenv("NEO4J_USERNAME", "neo4j")
            password = os.getenv("NEO4J_PASSWORD", "79113865Xie")

            self.kg = neo4jKG(uri, username, password)
            self._initialized = True
            logger.info("知识图谱连接成功")

        except Exception as e:
            logger.error(f"知识图谱初始化失败: {e}")
            # 可以根据需要决定是否抛出异常
            # 有些场景下知识图谱是可选的

    def get_kg(self):
        """获取知识图谱实例"""
        if self.kg is None:
            self.initialize()
        return self.kg