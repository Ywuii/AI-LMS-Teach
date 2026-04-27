# authentication/management/commands/cleanup_expired_tokens.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = '清理超过3小时的DRF Token'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=7,  # ✅ 修改为 7 天
            help='清理多少天之前创建的 Token（默认：7 天）'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='模拟运行，只显示统计不实际删除'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='显示详细输出'
        )

    def handle(self, *args, **options):
        hours = options['hours']
        dry_run = options['dry_run']
        verbose = options['verbose']

        # 计算3小时前的时间点
        cutoff_time = timezone.now() - timedelta(hours=hours)

        if verbose:
            self.stdout.write(f"当前时间: {timezone.now()}")
            self.stdout.write(f"清理时间点: {cutoff_time} (前{hours}小时)")
            self.stdout.write("正在查询过期的Token...")

        try:
            # 导入DRF的Token模型
            from rest_framework.authtoken.models import Token

            # 查询所有创建时间早于3小时前的Token
            expired_tokens = Token.objects.filter(created__lt=cutoff_time)

            # 统计数量
            count = expired_tokens.count()

            if verbose:
                self.stdout.write(f"找到 {count} 个超过{hours}小时的Token")

                # 显示部分示例（前5个）
                if count > 0 and verbose:
                    self.stdout.write("\n示例Token（前5个）:")
                    for i, token in enumerate(expired_tokens[:5]):
                        self.stdout.write(
                            f"  {i + 1}. 用户: {token.user.username if token.user else 'N/A'}, "
                            f"创建: {token.created}, "
                            f"Key: {token.key[:8]}..."
                        )

            if dry_run:
                self.stdout.write(
                    self.style.WARNING(f"[模拟运行] 将删除 {count} 个超过{hours}小时的Token")
                )
                if count == 0:
                    self.stdout.write("没有需要清理的Token")
            else:
                if count > 0:
                    # 实际删除
                    deleted_count, _ = expired_tokens.delete()
                    self.stdout.write(
                        self.style.SUCCESS(f"✅ 成功清理 {deleted_count} 个超过{hours}小时的Token")
                    )

                    # 记录日志
                    logger.info(f"清理了 {deleted_count} 个过期Token（超过{hours}小时）")

                    # 可选的额外操作：记录清理的用户
                    if verbose and deleted_count > 0:
                        # 可以在这里记录哪些用户的Token被清理了
                        pass
                else:
                    self.stdout.write("没有找到需要清理的Token")

        except ImportError:
            self.stdout.write(
                self.style.ERROR("❌ 未找到DRF Token模块，请确保已安装djangorestframework")
            )
            logger.error("清理Token失败：未安装DRF")

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ 清理Token时发生错误: {e}")
            )
            logger.error(f"清理Token失败: {e}", exc_info=True)