from functools import wraps
from django.http import JsonResponse
from rest_framework.authtoken.models import Token
from rest_framework import status


# Token认证装饰器
def token_auth_required(view_func):
    """
    Token认证装饰器
    验证Authorization头中的Token
    """

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # 1. 尝试获取并验证Token
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')

        if not auth_header:
            return JsonResponse({
                'error': '缺少认证Token',
                'success': False
            }, status=status.HTTP_401_UNAUTHORIZED)

        # 2. 解析Token
        # 支持两种格式: "Token <token>" 或 "Bearer <token>"
        parts = auth_header.split()
        if len(parts) != 2:
            return JsonResponse({
                'error': 'Token格式错误，应为: Token <token_key> 或 Bearer <token_key>',
                'success': False
            }, status=status.HTTP_401_UNAUTHORIZED)

        auth_type, token_key = parts

        if auth_type.lower() not in ['token', 'bearer']:
            return JsonResponse({
                'error': f'不支持的认证类型: {auth_type}，请使用Token或Bearer',
                'success': False
            }, status=status.HTTP_401_UNAUTHORIZED)

        # 3. 验证Token
        try:
            token = Token.objects.get(key=token_key)
            request.user = token.user
        except Token.DoesNotExist:
            return JsonResponse({
                'error': 'Token无效或已过期',
                'success': False
            }, status=status.HTTP_401_UNAUTHORIZED)

        # 4. 检查用户状态
        if not request.user.is_active:
            return JsonResponse({
                'error': '用户账户已被禁用',
                'success': False
            }, status=status.HTTP_403_FORBIDDEN)

        # 5. Token验证通过，调用原函数
        return view_func(request, *args, **kwargs)

    return wrapper
