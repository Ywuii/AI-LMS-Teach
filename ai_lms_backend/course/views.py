from django.http import JsonResponse
from django.views.decorators.http import require_GET

from utils.decorators import token_auth_required
from .models import Chapter, KnowledgePoint


@token_auth_required
@require_GET
def get_chapters(request):
    """
    获取所有章节
    返回格式：
    [
      { "id": 1, "label": "xxx", "value": "xxx" }
    ]
    """
    chapters = Chapter.objects.values("id", "title")

    data = [
        {
            "id": chapter["id"],
            "label": chapter["title"],
            "value": chapter["title"]
        }
        for chapter in chapters
    ]

    return JsonResponse({
        "code": 200,
        "msg": "success",
        "data": data
    })


@token_auth_required
@require_GET
def get_sections(request):
    """
    根据 chapter_id 获取知识点
    """
    chapter_id = request.GET.get("chapter_id")
    print("chapter_id:", chapter_id)
    if not chapter_id:
        return JsonResponse({
            "code": 400,
            "msg": "chapter_id 参数不能为空",
            "data": None
        })

    knowledge_list = KnowledgePoint.objects.filter(
        chapter_id=chapter_id
    ).values("id", "title")
    print("SQL:", knowledge_list.query)

    data = [
        {
            "id": k["id"],
            "label": k["title"],
            "value": k["title"]
        }
        for k in knowledge_list
    ]
    print(data)

    return JsonResponse({
        "code": 200,
        "msg": "success",
        "data": data
    })