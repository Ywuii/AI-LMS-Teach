from django.contrib import admin
from django.http import JsonResponse
from django.urls import path, include

# 这是URL配置的核心列表
urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/chat/", include("chat.urls")),
    path("api/auth/", include("authentication.urls")),
    path("api/experts/", include("experts.urls")), 
    path("api/system/", include("system.urls")),
    path("api/course/", include("course.urls"))
]
