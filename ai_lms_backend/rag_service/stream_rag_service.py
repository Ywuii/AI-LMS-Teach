# api/services/stream_rag_service.py
import asyncio
import time
from typing import AsyncGenerator, Dict, Any, Optional
from langchain.callbacks.base import AsyncCallbackHandler
from langchain.schema import LLMResult
import logging

logger = logging.getLogger(__name__)


class StreamingCallbackHandler(AsyncCallbackHandler):
    """流式回调处理器"""

    def __init__(self, queue: asyncio.Queue):
        self.queue = queue
        self.complete = False

    async def on_llm_new_token(self, token: str, **kwargs) -> None:
        """当LLM生成新token时调用"""
        await self.queue.put({
            "type": "token",
            "token": token,
            "timestamp": time.time()
        })

    async def on_llm_end(self, response: LLMResult, **kwargs) -> None:
        """当LLM完成时调用"""
        self.complete = True
        await self.queue.put({
            "type": "complete",
            "timestamp": time.time()
        })

    async def on_llm_error(self, error: Exception, **kwargs) -> None:
        """当LLM出错时调用"""
        await self.queue.put({
            "type": "error",
            "error": str(error),
            "timestamp": time.time()
        })


class StreamRAGService:
    """流式RAG服务"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initializFed'):
            from .rag_service import RAGService
            self.rag_service = RAGService()
            self._initialized = False

    async def query_stream(
            self,
            question: str,
            session_id: str,
            user_id: int,
            config: Optional[Dict[str, Any]] = None
    ) -> AsyncGenerator[str, None]:
        """
        流式查询RAG服务

        Args:
            question: 用户问题
            session_id: 会话ID
            user_id: 用户ID
            config: 配置参数

        Yields:
            SSE格式的流式响应
        """
        from utils.stream_utils import StreamResponseBuilder

        try:
            # 初始化服务
            if not self._initialized:
                self.rag_service.initialize()
                self._initialized = True

            # 发送开始事件
            yield StreamResponseBuilder.format_sse_event({
                "type": "start",
                "session_id": session_id,
                "question": question,
                "timestamp": time.time()
            })

            # 创建回调队列
            queue = asyncio.Queue()
            callback_handler = StreamingCallbackHandler(queue)

            # 这里需要修改你的RAG链以支持流式输出
            # 假设你有一个支持回调的链
            from .rag_kg_chain import build_stream_rag_kg_chain

            # 构建流式链
            stream_chain = build_stream_rag_kg_chain(callbacks=[callback_handler])

            # 启动查询任务
            query_task = asyncio.create_task(
                self._execute_query(
                    stream_chain,
                    question,
                    session_id,
                    user_id,
                    config
                )
            )

            # 流式输出
            while not callback_handler.complete:
                try:
                    # 等待token或超时
                    data = await asyncio.wait_for(queue.get(), timeout=30.0)

                    if data["type"] == "token":
                        yield StreamResponseBuilder.format_sse_event({
                            "type": "token",
                            "content": data["token"],
                            "timestamp": data["timestamp"]
                        })
                    elif data["type"] == "complete":
                        yield StreamResponseBuilder.format_sse_event({
                            "type": "complete",
                            "timestamp": data["timestamp"]
                        })
                        break
                    elif data["type"] == "error":
                        yield StreamResponseBuilder.format_error_event(
                            data["error"],
                            "stream_error"
                        )
                        break

                except asyncio.TimeoutError:
                    yield StreamResponseBuilder.format_sse_event({
                        "type": "timeout",
                        "timestamp": time.time()
                    })
                    break

            # 等待查询任务完成
            try:
                await query_task
            except Exception as e:
                logger.error(f"查询任务异常: {e}")

            # 发送结束事件
            yield StreamResponseBuilder.format_sse_event({
                "type": "end",
                "timestamp": time.time()
            })

        except Exception as e:
            logger.error(f"流式查询异常: {e}")
            yield StreamResponseBuilder.format_error_event(str(e))

    async def _execute_query(
            self,
            chain,
            question: str,
            session_id: str,
            user_id: int,
            config: Optional[Dict[str, Any]]
    ):
        """执行查询任务"""
        try:
            # 获取必要的组件
            retriever = self.rag_service.vector_store.get_retriever()
            kg = self.rag_service.kg_service.get_kg()

            if not retriever or not kg:
                raise ValueError("向量存储或知识图谱未初始化")

            # 这里调用你的流式链
            # 需要根据你的实际链结构调整
            result = await chain.ainvoke({
                "question": question,
                "session_id": session_id,
                "user_id": user_id,
                "config": config or {}
            })

            return result

        except Exception as e:
            logger.error(f"执行查询时出错: {e}")
            raise