"""
WSGI config for ai_lms_backend project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
# 设置系统环境变量
# 用于告诉Django，项目的配置文件(settings.py)的位置
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

# Django提供的函数
# 作用：加载Django项目，返回一个符合WSGI规范的应用程序对象(application)
# Web服务器启动时会寻找这个application变量，作为处理HTTP请求的入口。
application = get_wsgi_application()
