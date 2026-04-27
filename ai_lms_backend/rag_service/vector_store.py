import os
from pathlib import Path

from docx import Document
from langchain_chroma import Chroma
from langchain_chroma.vectorstores import logger
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from threading import Lock


class VectorStoreService:
    def __init__(self):
        self.vectorstore = None
        self.retriever = None
        self.embedding = None
        self._initialized = False
        self._lock = Lock()

    def initialize(self, force_reload=False):
        if self._initialized and not force_reload:
            return

        with self._lock:
            if self._initialized and not force_reload:
                return

            try:
                raw_text = self._read_document()
                documents = self._split_document(raw_text)
                self.embedding = self._init_embedding()
                self.vectorstore = self._init_vectorstore(documents)

                self.retriever = self.vectorstore.as_retriever(
                    search_kwargs={"k": 2}
                )

                self._initialized = True
                logger.info("✅ 向量存储初始化完成（仅一次）")

            except Exception as e:
                logger.error(f"向量存储初始化失败: {e}")
                raise

    def _read_document(self) -> str:
        """读取docx文档"""
        current_dir = Path(__file__).resolve().parent
        file_path = os.path.join(current_dir, 'data', 'DataSource.docx')

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文档不存在: {file_path}")

        document = Document(file_path)
        text = "\n".join([para.text for para in document.paragraphs])
        return text

    def _split_document(self, text: str):
        """分割文档"""
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=2048,
            chunk_overlap=50
        )
        return text_splitter.create_documents([text])

    def _init_embedding(self):
        """初始化嵌入模型"""
        try:
            embedding = OllamaEmbeddings(model="bge-m3")
            logger.info("嵌入模型加载成功")
            return embedding
        except Exception as e:
            logger.error(f"嵌入模型加载失败: {e}")
            raise

    def _init_vectorstore(self, documents):
        """初始化向量数据库"""
        persist_dir = os.path.join(
            Path(__file__).resolve().parent.parent,
            "chroma_db"
        )
        # 🆕 添加调试信息
        logger.info(f"向量库路径: {persist_dir}")
        logger.info(f"路径存在: {os.path.exists(persist_dir)}")

        if os.path.exists(persist_dir):
            logger.info(f"目录内容: {os.listdir(persist_dir)}")
            logger.info(f"是空目录: {not os.listdir(persist_dir)}")

        if not os.path.exists(persist_dir) or not os.listdir(persist_dir):
            # 创建新的向量数据库
            vectorstore = Chroma.from_documents(
                documents=documents,
                embedding=self.embedding,
                persist_directory=persist_dir,
            )
            logger.info(f"创建新的向量数据库: {persist_dir}")
        else:
            # 加载现有向量数据库
            vectorstore = Chroma(
                persist_directory=persist_dir,
                embedding_function=self.embedding
            )
            logger.info(f"加载现有向量数据库: {persist_dir}")

        return vectorstore

    def get_retriever(self):
        """获取检索器"""
        if self.retriever is None:
            self.initialize()
        return self.retriever