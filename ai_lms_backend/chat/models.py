# models.py
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.conf import settings
import uuid
from django.utils import timezone
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage


class ChatSession(models.Model):
    """
    聊天会话表 - 单表存储所有信息
    使用JSON字段存储消息历史，同时支持RunnableWithMessageHistory
    """
    MESSAGE_TYPES = [
        ('human', '用户消息'),
        ('ai', 'AI回复'),
        ('system', '系统消息'),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="唯一ID"
    )

    # 会话ID字段，用于RunnableWithMessageHistory兼容
    session_id = models.CharField(
        max_length=255,
        db_index=True,
        null=True,
        verbose_name="会话ID"
    )

    # 关联Django内置的User模型
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='chat_sessions',
        verbose_name="用户",
        db_index=True,


        null=True,
        blank=True
    )

    # 会话标题
    title = models.CharField(
        max_length=200,
        blank=True,
        default="",
        verbose_name="会话标题"
    )

    # 模型名称
    model_name = models.CharField(
        max_length=100,
        blank=True,
        default="qwen3:4b",
        verbose_name="模型名称"
    )

    # 聊天历史 - 使用JSON存储LangChain消息
    # 格式: [{"type": "human|ai|system", "content": "消息内容", "timestamp": "...", ...}, ...]
    chat_history = models.JSONField(
        default=list,
        verbose_name="聊天历史",
        encoder=DjangoJSONEncoder
    )

    # 会话元数据
    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="元数据"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="创建时间"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="最后更新时间"
    )

    class Meta:
        db_table = 'chat_session'
        verbose_name = '聊天会话'
        verbose_name_plural = '聊天会话管理'
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['user', 'updated_at']),
            models.Index(fields=['session_id']),
        ]

    def __str__(self):
        username = self.user.username if self.user else "匿名用户"
        return f"{username}的会话: {self.title or '无标题'}"

    def save(self, *args, **kwargs):
        # 如果是新会话且没有标题，使用第一条消息作为标题
        is_new = self._state.adding
        if is_new and not self.title and self.chat_history:
            first_msg = self.chat_history[0] if isinstance(self.chat_history, list) else None
            if first_msg and 'content' in first_msg:
                content = first_msg.get('content', '')
                if isinstance(content, dict):
                    content = content.get('content', '')
                self.title = content[:50] + "..." if len(content) > 50 else content
        super().save(*args, **kwargs)

    def get_messages_count(self):
        """获取消息数量"""
        if isinstance(self.chat_history, list):
            return len(self.chat_history)
        return 0

    def get_last_message(self):
        """获取最后一条消息"""
        if isinstance(self.chat_history, list) and self.chat_history:
            return self.chat_history[-1]
        return None

    def get_short_last_message(self, max_length=50):
        """获取最后一条消息的简短版本"""
        last_msg = self.get_last_message()
        if not last_msg:
            return ""

        content = last_msg.get('content', '')
        if isinstance(content, dict):
            content = content.get('content', '')

        if len(content) > max_length:
            return content[:max_length] + "..."
        return content

    def add_message(self, message_type, content, **kwargs):
        """添加消息（内部使用）"""
        if not isinstance(self.chat_history, list):
            self.chat_history = []

        message = {
            "id": str(uuid.uuid4()),
            "type": message_type,
            "content": content,
            "timestamp": timezone.now().isoformat(),
            **kwargs
        }

        self.chat_history.append(message)
        self.save(update_fields=['chat_history', 'updated_at'])
        return message

    def add_human_message(self, content, **kwargs):
        """添加用户消息"""
        return self.add_message("human", content, **kwargs)

    def add_ai_message(self, content, **kwargs):
        """添加AI回复"""
        return self.add_message("ai", content, **kwargs)

    def add_system_message(self, content, **kwargs):
        """添加系统消息"""
        return self.add_message("system", content, **kwargs)

    def clear_history(self):
        """清空历史记录"""
        self.chat_history = []
        self.save(update_fields=['chat_history', 'updated_at'])

    def to_langchain_messages(self):
        """将存储的消息转换为LangChain消息对象"""
        messages = []

        # 修正：从 chat_history 字段读取
        history_data = self.chat_history

        if not isinstance(history_data, list):
            return messages

        for msg_data in history_data:
            if not isinstance(msg_data, dict):
                continue

            msg_type = msg_data.get('type', '').lower()
            content_data = msg_data.get('content', {})

            # 处理 content 字段
            if isinstance(content_data, dict):
                # 格式: {"content": "消息内容", "additional_kwargs": {}}
                content = content_data.get('content', '')
                additional_kwargs = content_data.get('additional_kwargs', {})
            else:
                # 如果 content 是字符串
                content = str(content_data)
                additional_kwargs = {}

            # 创建对应的 LangChain 消息对象
            if msg_type == 'human':
                from langchain_core.messages import HumanMessage
                message = HumanMessage(content=content, additional_kwargs=additional_kwargs)
            elif msg_type == 'ai':
                from langchain_core.messages import AIMessage
                message = AIMessage(content=content, additional_kwargs=additional_kwargs)
            elif msg_type == 'system':
                from langchain_core.messages import SystemMessage
                message = SystemMessage(content=content, additional_kwargs=additional_kwargs)
            else:
                # 默认视为 human 消息
                from langchain_core.messages import HumanMessage
                message = HumanMessage(content=content, additional_kwargs=additional_kwargs)

            messages.append(message)

        return messages

    def from_langchain_messages(self, messages):
        """从LangChain消息列表更新历史"""
        self.chat_history = []

        for msg in messages:
            if isinstance(msg, HumanMessage):
                msg_type = "human"
            elif isinstance(msg, AIMessage):
                msg_type = "ai"
            elif isinstance(msg, SystemMessage):
                msg_type = "system"
            else:
                msg_type = "human"

            message = {
                "id": str(uuid.uuid4()),
                "type": msg_type,
                "content": {
                    "content": msg.content,
                    "additional_kwargs": msg.additional_kwargs
                },
                "timestamp": timezone.now().isoformat()
            }
            self.chat_history.append(message)

        self.save(update_fields=['chat_history', 'updated_at'])

    @classmethod
    def get_or_create_by_session_id(cls, session_id, user=None, **kwargs):
        """根据session_id获取或创建会话"""
        try:
            session = cls.objects.get(session_id=session_id)
            # 检查用户权限
            if user and session.user and session.user != user:
                raise PermissionError(f"会话{session_id}不属于用户{user.username}")
            return session, False
        except cls.DoesNotExist:
            # 创建新会话
            session = cls(
                session_id=session_id,
                user=user,
                **kwargs
            )
            session.save()
            return session, True