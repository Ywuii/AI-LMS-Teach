from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate


class UserSerializer(serializers.ModelSerializer):
    """用户信息序列化器 - 用于返回用户信息"""

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'date_joined']
        read_only_fields = ['id', 'date_joined']
        # 简单配置，不需要额外验证


class LoginSerializer(serializers.Serializer):
    """登录序列化器 - 用于验证登录数据"""
    username = serializers.CharField(required=True)
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}  # 前端显示为密码框
    )

    def validate(self, data):
        """验证用户名和密码"""
        username = data.get('username')
        password = data.get('password')

        # 1. 验证必填字段
        if not username or not password:
            raise serializers.ValidationError("用户名和密码不能为空")

        # 2. 验证用户
        user = authenticate(username=username, password=password)

        if not user:
            raise serializers.ValidationError("用户名或密码错误")

        if not user.is_active:
            raise serializers.ValidationError("账户已被禁用")

        # 3. 将验证通过的用户添加到数据中
        data['user'] = user
        return data