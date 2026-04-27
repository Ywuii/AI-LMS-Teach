from django.urls import path

from course.views import get_chapters, get_sections

urlpatterns = [
    path("lesson-plan/chapters", get_chapters, name="get_chapters"),
    path("lesson-plan/sections", get_sections, name="get_sections"),
]