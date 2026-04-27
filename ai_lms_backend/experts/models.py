# models.py
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
import json


class TestGenerationConfig(models.Model):
    """测试题生成配置"""

    QUESTION_TYPES = [
        ('single_choice', '单选题'),
        ('multiple_choice', '多选题'),
        ('true_false', '判断题'),
        ('fill_blank', '填空题'),
        ('short_answer', '简答题'),
        ('programming', '编程题'),
    ]

    OUTPUT_FORMATS = [
        ('json', 'JSON格式'),
        ('markdown', 'Markdown格式'),
        ('text', '纯文本格式'),
        ('html', 'HTML格式'),
    ]

    DIFFICULTY_LEVELS = [
        ("easy", "简单"),
        ("medium", "中等"),
        ("hard", "困难"),
    ]

    difficulty_level = models.IntegerField(
        '难度级别',
        choices=DIFFICULTY_LEVELS,
        default=2
    )

    # 创建者
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='test_configs')

    # 基本信息
    name = models.CharField('配置名称', max_length=100, default='未命名配置')
    description = models.TextField('配置描述', blank=True)

    # 第一大参数：内容参数
    chapters = models.JSONField('知识点章节', default=list)  # ["第一章", "第二章"]
    knowledge_categories = models.JSONField('知识点分类', default=list)  # ["基础概念", "语法"]
    knowledge_points = models.JSONField('知识点', default=list)  # ["变量", "循环"]
    question_types = models.JSONField('题型选择', default=list)  # ["single_choice", "fill_blank"]
    output_answer = models.BooleanField('是否输出答案', default=True)
    output_explanation = models.BooleanField('是否输出解析', default=True)
    output_format = models.CharField('输出格式', max_length=20, choices=OUTPUT_FORMATS, default='json')

    # 第二大参数：检索参数
    use_knowledge_graph = models.BooleanField('使用知识图谱', default=True)
    use_rag_retrieval = models.BooleanField('使用RAG检索', default=True)

    # 其他参数
    question_count = models.IntegerField('题目数量', default=5)
    language = models.CharField('题目语言', max_length=20, choices=[('zh', '中文'), ('en', '英文')], default='zh')

    # 元数据
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    is_active = models.BooleanField('是否激活', default=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = '测试题生成配置'
        verbose_name_plural = '测试题生成配置'

    def __str__(self):
        return f"{self.name} - {self.creator.username}"

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'chapters': self.chapters,
            'knowledge_categories': self.knowledge_categories,
            'knowledge_points': self.knowledge_points,
            'question_types': self.question_types,
            'output_answer': self.output_answer,
            'output_explanation': self.output_explanation,
            'output_format': self.output_format,
            'use_knowledge_graph': self.use_knowledge_graph,
            'use_rag_retrieval': self.use_rag_retrieval,
            'difficulty_level': self.difficulty_level,
            'question_count': self.question_count,
            'language': self.language,
        }


class GeneratedTest(models.Model):
    """生成的测试题"""

    STATUS_CHOICES = [
        ('pending', '生成中'),
        ('success', '成功'),
        ('failed', '失败'),
        ('partial', '部分成功'),
    ]

    # 关联
    config = models.ForeignKey(TestGenerationConfig, on_delete=models.CASCADE, related_name='generated_tests')
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='generated_tests')

    # 生成结果
    questions = models.JSONField('生成的题目', default=list)
    raw_response = models.TextField('原始响应', blank=True)
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField('错误信息', blank=True)

    # 性能指标
    generation_time = models.FloatField('生成耗时(秒)', null=True, blank=True)
    token_count = models.IntegerField('Token数量', null=True, blank=True)

    # 检索信息
    retrieved_docs = models.JSONField('检索的文档', default=list, blank=True)
    kg_entities = models.JSONField('知识图谱实体', default=list, blank=True)

    # 元数据
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = '生成的测试题'
        verbose_name_plural = '生成的测试题'

    def __str__(self):
        return f"测试题 #{self.id} - {self.get_status_display()}"

class TaskInfo(models.Model):
    """
    表 3-2 任务信息表
    """

    id = models.AutoField(primary_key=True, verbose_name="主键")

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tasks',
        verbose_name="发起人"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="任务创建时间"
    )

    finished_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="任务完成时间"
    )

    class Meta:
        db_table = "task_info"
        verbose_name = "任务信息"
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f"Task {self.id} by {self.user.username}"

class Question(models.Model):
    """
    表 3-5 测试题信息表
    """

    id = models.AutoField(primary_key=True)

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="questions",
        verbose_name="创建用户"
    )

    knowledge_point = models.CharField(
        max_length=200,
        verbose_name="所属知识点"
    )

    chapter = models.CharField(
        max_length=200,
        verbose_name="所属章节"
    )

    QUESTION_TYPES = (
        ('single_choice', '单选题'),
        ('multi_choice', '多选题'),
        ('judge', '判断题'),
        ('fill_blank', '填空题'),
        ('short_answer', '简答题'),
    )

    question_type = models.CharField(
        max_length=50,
        choices=QUESTION_TYPES,
        verbose_name="题型"
    )

    difficulty = models.CharField(
        max_length=10,
        verbose_name="难度"
    )

    question_text = models.TextField(
        verbose_name="题目内容"
    )

    options = models.JSONField(
        null=True,
        blank=True,
        verbose_name="选项（选择题专用）"
    )

    answer = models.CharField(
        max_length=200,
        verbose_name="答案"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="创建时间"
    )

    class Meta:
        db_table = "question"
        verbose_name = "测试题"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.chapter} - {self.question_text[:30]}"