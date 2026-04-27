import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from experts.services.llm_provider import LLMProvider
from utils.decorators import token_auth_required
from experts.serializers import QuestionRequestSerializer, LessonPlanRequestSerializer, CodeReviewRequestSerializer
from experts.services.agent_service import AgentService


@token_auth_required
@require_POST
def generate_question(request):
    print("🟢 原始请求 body:", request.body.decode())
    # 1. 解析 JSON
    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    # 2. 校验参数
    serializer = QuestionRequestSerializer(data=body)
    serializer.is_valid(raise_exception=True)

    print("🟢 validated_data:", serializer.validated_data)

    prompt_data = serializer.to_representation(serializer.validated_data)
    print("🟢 prompt_data:", prompt_data)

    # 3. 调用服务层
    service = AgentService()
    result = service.generate_question(prompt_data)

    print("🟢 Agent 返回结果:", result)
    # 4. 返回结果
    print("🟢 result 类型:", type(result))
    print("🟢 result 内容:", result)

    return JsonResponse(result, safe=False)

@token_auth_required
@require_POST
def generate_lesson_plan(request):
    print("🟢 原始请求 body:", request.body.decode())

    # 1. 解析 JSON
    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    # 2. 校验参数
    serializer = LessonPlanRequestSerializer(data=body)
    serializer.is_valid(raise_exception=True)

    print("🟢 validated_data:", serializer.validated_data)

    prompt_data = serializer.to_representation(serializer.validated_data)
    print("🟢 prompt_data:", prompt_data)

    # 3. 调用服务层
    service = AgentService()
    result = service.generate_lesson_plan(prompt_data)

    print("🟢 LessonPlanAgent 返回结果:", result)

    # 4. 返回结果
    return JsonResponse(result, safe=False)

@token_auth_required
@require_POST
def code_review(request):
    """
    代码审查接口
    """
    print("🟢 原始请求 body:", request.body.decode())

    # 1. 解析 JSON
    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    # 2. 参数校验
    serializer = CodeReviewRequestSerializer(data=body)
    serializer.is_valid(raise_exception=True)

    print("🟢 validated_data:", serializer.validated_data)

    # 3. 构造 prompt / 业务数据
    prompt_data = serializer.to_representation(serializer.validated_data)
    print("🟢 prompt_data:", prompt_data)

    # 4. 调用服务层
    service = AgentService()
    result = service.code_review(prompt_data)

    print("🟢 Code Review 返回结果:", result)

    # 5. 返回结果
    return JsonResponse({
        "success": True,
        "data": result
    }, safe=False)
