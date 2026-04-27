# system/views.py
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response

class AsyncRouteViewSet(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        routes = [
            # ===== AI 总入口 =====
            {
                "id": 1,
                "parent": 0,
                "path": "/ai",
                "component": "layout",
                "meta": {"title": "AI 接口管理", "icon": "ep:cpu"}
            },

            # ===== 原有测试路由 =====
            {
                "id": 2,
                "parent": 1,
                "path": "/ai/test",
                "component": "test",
                "meta": {"title": "AI接口调用测试"}
            },
            {
                "id": 3,
                "parent": 1,
                "path": "/ai/block",
                "component": "chat",
                "meta": {"title": "问答接口阻塞调用"}
            },
            {
                "id": 4,
                "parent": 1,
                "path": "/ai/stream",
                "component": "chat_stream",
                "meta": {"title": "问答接口流式调用"}
            },

            # ===== 教学智能体（你已有）=====
            {
                "id": 5,
                "parent": 0,
                "path": "/teaching",
                "component": "layout",
                "meta": {"title": "教学智能体", "icon": "ep:school"}
            },

            {
                "id": 6,
                "parent": 5,
                "path": "/ai/qa",
                "component": "qa",
                "meta": {
                    "title": "在线学习助手",
                    "icon": "ep:chat-dot-round",
                    "agentId": "agent1"
                }
            },

            {
                "id": 7,
                "parent": 5,
                "path": "/ai/exam",
                "component": "exam",
                "meta": {
                    "title": "习题生成专家",
                    "icon": "ep:chat-dot-round",
                    "agentId": "agent3"
                }
            },

            {
                "id": 8,
                "parent": 5,
                "path": "/ai/plan",
                "component": "plan",
                "meta": {
                    "title": "教案设计专家",
                    "icon": "ep:chat-dot-round",
                    "agentId": "agent4"
                }
            },

            {
                "id": 9,
                "parent": 5,
                "path": "/ai/evaluation",
                "component": "evaluation",
                "meta": {
                    "title": "代码评测专家",
                    "icon": "ep:chat-dot-round",
                    "agentId": "agent5"
                }
            },
        ]

        return Response({
            "success": True,
            "msg": "success",
            "data": routes
        })