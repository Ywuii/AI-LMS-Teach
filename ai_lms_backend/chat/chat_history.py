# chat_history.py
from typing import List, Optional
from django.db import transaction
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage

from .models import ChatSession


class DjangoChatMessageHistory(BaseChatMessageHistory):
    """
    基于Django单表的聊天历史存储
    兼容RunnableWithMessageHistory
    """

    def __init__(self, session_id: str, **kwargs):
        self.session_id = session_id
        self.model_name = kwargs.get("model_name", "qwen3:4b")
        parsed_user_id = self._extract_user_id_from_session(session_id)
        print(f"从session_id解析的user_id: {parsed_user_id}")

        # 获取或创建会话
        with transaction.atomic():
            try:
                # 尝试获取现有会话
                self.chat_session = ChatSession.objects.get(session_id=session_id)
                # 检查会话是否已有标题
                if self.chat_session.title:
                    self.auto_title_attempted = True

                if parsed_user_id and not self.chat_session.user:
                    from django.contrib.auth import get_user_model
                    User = get_user_model()
                    try:
                        user = User.objects.get(id=parsed_user_id)
                        self.chat_session.user = user
                        self.chat_session.save()
                    except User.DoesNotExist:
                        pass

            except ChatSession.DoesNotExist:
                # 创建新会话
                user = None
                if parsed_user_id:
                    from django.contrib.auth import get_user_model
                    User = get_user_model()
                    try:
                        user = User.objects.get(id=parsed_user_id)
                    except User.DoesNotExist:
                        pass

                # 获取其他参数
                title = kwargs.get("title", "")

                if not title:
                    self.auto_title_attempted = False
                else:
                    self.auto_title_attempted = True

                self.chat_session = ChatSession.objects.create(
                    session_id=session_id,
                    user=user,
                    model_name=self.model_name,
                    title=title
                )

    @property
    def messages(self) -> List[BaseMessage]:
        """获取所有消息（实现BaseChatMessageHistory接口）"""
        return self.chat_session.to_langchain_messages()

    def add_message(self, message: BaseMessage) -> None:
        """添加消息（实现BaseChatMessageHistory接口）"""
        # 确定消息类型
        if isinstance(message, HumanMessage):
            msg_type = "human"
        elif isinstance(message, AIMessage):
            msg_type = "ai"
        elif isinstance(message, SystemMessage):
            msg_type = "system"
        else:
            msg_type = "human"

        # 检查并设置标题
        self._check_and_set_title(message.content, msg_type)

        # 构建消息数据
        msg_data = {
            "content": message.content,
            "additional_kwargs": message.additional_kwargs
        }

        # 添加到会话历史
        self.chat_session.add_message(msg_type, msg_data)

    def add_user_message(self, content: str, **kwargs) -> None:
        """添加快捷方法：用户消息"""
        from django.utils import timezone
        self.chat_session.add_human_message(content, **kwargs)

    def add_ai_message(self, content: str, **kwargs) -> None:
        """添加快捷方法：AI消息"""
        from django.utils import timezone
        self.chat_session.add_ai_message(content, **kwargs)

    def clear(self) -> None:
        """清空历史（实现BaseChatMessageHistory接口）"""
        self.chat_session.clear_history()

    def get_messages_count(self) -> int:
        """获取消息数量"""
        return self.chat_session.get_messages_count()

    def get_session_info(self) -> dict:
        """获取会话信息"""
        return {
            'session_id': self.chat_session.session_id,
            'user': self.chat_session.user.username if self.chat_session.user else None,
            'title': self.chat_session.title,
            'model_name': self.chat_session.model_name,
            'message_count': self.get_messages_count(),
            'created_at': self.chat_session.created_at.isoformat(),
            'updated_at': self.chat_session.updated_at.isoformat(),
        }

    def _check_and_set_title(self, content: str, msg_type: str):
        """检查并设置标题（仅在首次用户消息时）"""
        if (not self.auto_title_attempted and
                not self.chat_session.title and
                msg_type == "human"):

            from django.utils import timezone
            # 截取前50个字符作为标题
            title = content[:50]
            if len(content) > 50:
                title += "..."

            # 更新标题
            self.chat_session.title = title
            self.chat_session.save(update_fields=['title', 'updated_at'])
            self.auto_title_attempted = True
            return True
        return False

    def _extract_user_id_from_session(self, session_id: str) -> Optional[int]:
        """
        从session_id解析user_id

        支持格式:
        1. "user_{user_id}_{uuid}"  - 你的格式
        2. "{user_id}_{uuid}"       - 简洁格式
        3. "chat_{user_id}_{uuid}"  - 备用格式
        """
        if not session_id:
            return None

        print(f"正在解析session_id: {session_id}")

        # 移除可能的协议前缀
        if session_id.startswith(('user_', 'chat_')):
            # 格式: "user_123_uuid" 或 "chat_123_uuid"
            parts = session_id.split('_')
            if len(parts) >= 2:
                try:
                    user_id = int(parts[1])
                    print(f"解析成功: 从 '{parts[0]}_{parts[1]}_...' 得到 user_id={user_id}")
                    return user_id
                except (ValueError, IndexError):
                    pass

        # 格式: "123_uuid" (直接以数字开头)
        import re
        match = re.match(r'^(\d+)_', session_id)
        if match:
            try:
                user_id = int(match.group(1))
                print(f"解析成功: 从数字前缀得到 user_id={user_id}")
                return user_id
            except ValueError:
                pass

        print(f"无法从session_id解析user_id: {session_id}")
        return None