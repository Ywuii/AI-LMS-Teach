import json
import logging
import time
import uuid

from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.http import require_POST, require_GET

from chat.models import ChatSession
from utils.decorators import token_auth_required

logger = logging.getLogger(__name__)

# 全局RAG服务实例
_rag_service = None


def get_rag_service():
    """获取RAG服务实例（单例模式）"""
    global _rag_service
    if _rag_service is None:
        try:
            from rag_service.rag_service import RAGService
            _rag_service = RAGService()
            _rag_service.initialize()
            logger.info("RAG服务初始化完成")
        except Exception as e:
            logger.error(f"RAG服务初始化失败: {e}")
            _rag_service = None
    return _rag_service

# 阻塞模式
@token_auth_required
@require_POST
def chat_ask(request):
    """聊天问答接口（Token认证版）"""
    print(f"收到请求，用户: {request.user.id}")

    try:
        # 解析请求
        data = json.loads(request.body)
        question = data.get('question', '').strip()
        session_id = data.get('session_id', '').strip()
        if not question:
            return JsonResponse({'error': '问题不能为空', 'success': False}, status=400)

        if not session_id:
            session_id = f"user_{request.user.id}_{uuid.uuid4()}"
            print(f"创建新的会话ID: {session_id}")

        # 获取RAG服务
        rag_service = get_rag_service()
        if rag_service is None:
            return JsonResponse({'error': 'RAG服务未就绪', 'success': False}, status=503)

        # 构建config参数
        config = {
            "configurable": {
                "session_id": session_id,
            }
        }

        # 执行查询
        # 根据RAGService的设计，这里需要传入config参数
        result = rag_service.query(question=question, config=config)

        # 返回结果
        if result.get('success'):
            return JsonResponse({
                'session_id': session_id,
                'answer': result.get('answer', ''),
                'success': True
            })
        else:
            return JsonResponse({
                'session_id': session_id,
                'error': result.get('error', '查询失败'),
                'answer': result.get('answer', ''),
                'success': False
            })

    except json.JSONDecodeError:
        return JsonResponse({'error': '请求格式错误', 'success': False}, status=400)
    except TypeError as e:
        # 如果参数不匹配，可能是旧版RAGService
        logger.warning(f"参数不匹配，尝试旧版调用: {e}")

        # 回退到旧版调用
        result = rag_service.query(question=question, config=config)

        if result.get('success'):
            return JsonResponse({
                'session_id': session_id,
                'answer': result.get('answer', ''),
                'success': True
            })
        else:
            return JsonResponse({
                'session_id': session_id,
                'error': result.get('error', '查询失败'),
                'answer': result.get('answer', ''),
                'success': False
            })
    except Exception as e:
        logger.error(f"接口异常: {e}", exc_info=True)
        return JsonResponse({'error': f'服务器错误: {str(e)}', 'success': False}, status=500)

# 流式输出
@token_auth_required
@require_POST
def chat_stream(request):
    """
    真正的流式聊天问答接口
    使用 RAGService.query_stream() 方法
    """
    print(f"[真实流式接口] 收到请求，用户: {request.user.username}")

    def generate():
        try:
            # 解析请求
            data = json.loads(request.body)
            question = data.get('question', '').strip()
            session_id = data.get('session_id', '').strip()

            if not question:
                yield format_sse_event({
                    "type": "error",
                    "content": "问题不能为空"
                })
                return

            if not session_id:
                import uuid
                session_id = f"user_{request.user.id}_{uuid.uuid4().hex[:8]}"
                print(f"[真实流式接口] 创建会话ID: {session_id}")

            # 发送开始事件
            yield format_sse_event({
                "type": "start",
                "session_id": session_id,
                "question": question[:100],
                "timestamp": time.time()
            })

            # 获取RAG服务
            rag_service = get_rag_service()

            if not rag_service.is_ready():
                rag_service.initialize()

            # 构建config
            config = {"configurable": {"session_id": session_id}}

            print(f"[真实流式接口] 开始流式生成...")

            # 真正的流式查询
            full_answer = ""
            token_count = 0

            try:
                for token in rag_service.query_stream(
                        question=question,
                        config=config
                ):
                    # 发送token事件
                    yield format_sse_event({
                        "type": "token",
                        "token": token,
                        "index": token_count
                    })

                    full_answer += token
                    token_count += 1

                    # 每10个token打印一次进度
                    if token_count % 10 == 0:
                        print(f"[真实流式接口] 已生成 {token_count} 个token")

                print(f"[真实流式接口] 流式生成完成，总token数: {token_count}")

                # 发送完成事件
                yield format_sse_event({
                    "type": "complete",
                    "full_answer": full_answer,
                    "total_tokens": token_count,
                    "timestamp": time.time()
                })

            except Exception as e:
                logger.error(f"流式生成过程中出错: {e}")
                # 即使出错，也发送已生成的部分
                if full_answer:
                    yield format_sse_event({
                        "type": "complete",
                        "full_answer": full_answer,
                        "partial": True,
                        "error": str(e),
                        "timestamp": time.time()
                    })
                else:
                    yield format_sse_event({
                        "type": "error",
                        "content": f"生成回答时出错: {str(e)}"
                    })

            # 发送结束事件
            yield format_sse_event({
                "type": "end",
                "timestamp": time.time()
            })

        except json.JSONDecodeError:
            yield format_sse_event({
                "type": "error",
                "content": "请求格式错误"
            })
        except Exception as e:
            logger.error(f"流式接口异常: {e}", exc_info=True)
            yield format_sse_event({
                "type": "error",
                "content": f"服务器错误: {str(e)}"
            })
        finally:
            # 确保流关闭
            yield "data: [DONE]\n\n"

    return StreamingHttpResponse(
        generate(),
        content_type='text/event-stream'
    )

@token_auth_required
@require_GET
def chat_session_list(request):
    user = request.user
    sessions = ChatSession.objects.filter(
        user=user,
    ).order_by("-updated_at")

    return JsonResponse({
        "sessions": [
            {
                "session_id": s.session_id,
                "title": s.title,
                "updated_at": s.updated_at.isoformat()
            }
            for s in sessions
        ]
    })

@token_auth_required
@require_GET
def chat_history(request, session_id):
    from .chat_history import DjangoChatMessageHistory
    from langchain_core.messages import HumanMessage, AIMessage

    history = DjangoChatMessageHistory(session_id=session_id)
    messages = history.messages

    data = []

    for m in messages:
        # 从 content dict 中取真实文本
        text = ""
        if isinstance(m.content, dict):
            text = m.content.get("content", "")
        else:
            text = str(m.content)

        data.append({
            "role": "user" if isinstance(m, HumanMessage) else "ai",
            "content": text,
            "timestamp": m.timestamp.isoformat() if hasattr(m, "timestamp") else None
        })

    return JsonResponse({"messages": data})

def format_sse_event(data: dict) -> str:
    """格式化SSE事件"""
    data_str = json.dumps(data, ensure_ascii=False)
    return f"data: {data_str}\n\n"