# utils/stream_utils.py
import json
import asyncio
from typing import AsyncGenerator, Dict, Any
from django.http import StreamingHttpResponse, JsonResponse
import time


class StreamResponseBuilder:
    """流式响应构建器"""

    @staticmethod
    def build_stream_response(stream_generator: AsyncGenerator, content_type='text/event-stream'):
        """构建流式响应"""
        response = StreamingHttpResponse(
            stream_generator,
            content_type=content_type,
        )
        response['Cache-Control'] = 'no-cache'
        response['X-Accel-Buffering'] = 'no'  # 禁用nginx缓冲
        return response

    @staticmethod
    def format_sse_event(data: Dict[str, Any], event_type: str = "message") -> str:
        """格式化SSE事件"""
        event_str = f"event: {event_type}\n"
        data_str = json.dumps(data, ensure_ascii=False)
        event_str += f"data: {data_str}\n\n"
        return event_str

    @staticmethod
    def format_error_event(error_message: str, error_code: str = "error") -> str:
        """格式化错误事件"""
        return StreamResponseBuilder.format_sse_event({
            "type": "error",
            "content": error_message,
            "code": error_code
        })