# authentication/scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from django_apscheduler.jobstores import DjangoJobStore, register_events
from django_apscheduler.models import DjangoJobExecution
from django.conf import settings
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


def cleanup_job():
    """定时清理任务"""
    try:
        logger.info("开始执行定时Token清理...")

        # 这里调用你的管理命令逻辑
        from django.core.management import call_command
        call_command('cleanup_expired_tokens', '--hours=24')

        logger.info("Token清理完成")

    except Exception as e:
        logger.error(f"定时清理任务失败: {e}")


def start_scheduler():
    """启动调度器"""
    scheduler = BackgroundScheduler(timezone=settings.TIME_ZONE)
    scheduler.add_jobstore(DjangoJobStore(), "default")

    # 注册定时任务
    # 每天凌晨4点执行
    scheduler.add_job(
        cleanup_job,
        trigger='interval',
        minutes=30,
        id="cleanup_tokens",
        max_instances=1,
        replace_existing=True,
    )

    # 可选：添加监控任务
    scheduler.add_job(
        log_scheduler_status,
        trigger='interval',
        minutes=60,  # 每小时记录一次状态
        id="log_scheduler_status",
        max_instances=1,
        replace_existing=True,
    )

    # 启动调度器
    scheduler.start()
    logger.info("调度器已启动，定时任务已安排")

    # 优雅关闭
    import atexit
    atexit.register(lambda: scheduler.shutdown())


def log_scheduler_status():
    """记录调度器状态"""
    logger.info("调度器运行正常，定时任务活跃")
