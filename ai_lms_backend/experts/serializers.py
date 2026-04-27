from rest_framework import serializers
from .models import TestGenerationConfig


class QuestionRequestSerializer(serializers.Serializer):
    chapter = serializers.CharField()
    knowledge_type = serializers.CharField()
    knowledge_point = serializers.CharField()

    question_type = serializers.ChoiceField(
        choices=TestGenerationConfig.QUESTION_TYPES
    )

    question_count = serializers.IntegerField(min_value=1, max_value=20)

    difficulty = serializers.ChoiceField(
        choices=TestGenerationConfig.DIFFICULTY_LEVELS
    )

    use_kg = serializers.BooleanField(default=True)
    use_rag = serializers.BooleanField(default=True)
    include_answer = serializers.BooleanField(default=True)
    include_explanation = serializers.BooleanField(default=True)

class LessonPlanRequestSerializer(serializers.Serializer):
    chapter = serializers.CharField(
        help_text="章节名称，如：指针与数组"
    )

    section_title = serializers.CharField(
        help_text="小节标题，如：指针与数组的关系"
    )

    def to_representation(self, instance):
        """
        仅做必要的数据清洗，不做映射
        """
        return super().to_representation(instance)

class CodeReviewRequestSerializer(serializers.Serializer):
    student_code = serializers.CharField(
        help_text="待审查的代码内容"
    )