# chat/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login, logout

from utils.serializers import LoginSerializer


class LoginView(APIView):
    """用户登录API"""
    permission_classes = [AllowAny]  # 允许所有人访问

    def post(self, request):
        # 1. 验证数据
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': '数据格式错误',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        # 2. 验证用户
        user = authenticate(request, username=username, password=password)

        if user is None:
            return Response({
                'success': False,
                'message': '用户名或密码错误'
            }, status=status.HTTP_401_UNAUTHORIZED)

        if not user.is_active:
            return Response({
                'success': False,
                'message': '账户已被禁用'
            }, status=status.HTTP_403_FORBIDDEN)

        # 3. 登录（创建Session）
        login(request, user)

        # 4. Token管理：删除旧的，创建新的
        Token.objects.filter(user=user).delete()  # 删除旧Token
        token = Token.objects.create(user=user)  # 创建新Token
        print("发送token:"+token.key)        # 5. 返回响应
        return Response({
            'success': True,
            'message': '登录成功',
            'token': token.key,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        })


class LogoutView(APIView):
    """用户登出API"""
    permission_classes = [IsAuthenticated]  # 需要登录

    def post(self, request):
        try:
            # 1. 删除用户的Token
            Token.objects.filter(user=request.user).delete()

            # 2. 清除Session
            logout(request)

            return Response({
                'success': True,
                'message': '已退出登录'
            })
        except Exception as e:
            return Response({
                'success': False,
                'message': f'登出失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)