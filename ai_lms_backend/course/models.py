from django.db import models


class Chapter(models.Model):
    """
    表 3-3 章节信息表
    """
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200, verbose_name="章节标题")
    book_name = models.CharField(max_length=200, verbose_name="教材名称")

    class Meta:
        db_table = "chapter"
        verbose_name = "章节信息"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.book_name} - {self.title}"


class KnowledgePoint(models.Model):
    """
    表 3-4 知识点信息表
    """
    id = models.AutoField(primary_key=True)
    chapter = models.ForeignKey(
        Chapter,
        on_delete=models.CASCADE,
        related_name="knowledge_points",
        verbose_name="所属章节"
    )
    title = models.CharField(max_length=200, verbose_name="知识点内容")

    class Meta:
        db_table = "knowledge_point"
        verbose_name = "知识点"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title