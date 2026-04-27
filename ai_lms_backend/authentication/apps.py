import os

from django.apps import AppConfig


class AuthenticationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "authentication"

    def ready(self):
        """Django启动时运行"""
        import sys
        from django.conf import settings

        # 判断是否应该启动定时任务
        should_start = False

        # 情况1：生产环境（DEBUG=False）直接启动
        if not settings.DEBUG:
            should_start = True
            print("生产环境: 启动定时任务")

        # 情况2：开发环境，只在服务进程启动
        elif settings.DEBUG and os.environ.get('RUN_MAIN'):
            should_start = True
            print("开发环境: 在服务进程启动定时任务")

        # 情况3：管理命令不启动
        if len(sys.argv) > 1 and sys.argv[1] in ['runserver', 'test', 'shell']:
            # 这些命令可能需要特殊处理
            pass

        if should_start:
            try:
                from .scheduler import start_scheduler
                start_scheduler()
                print("✅ 定时清理任务已启动")
            except Exception as e:
                print(f"❌ 定时任务启动失败: {e}")