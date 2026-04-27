from django.urls import path

from experts import views

urlpatterns = [
    path("question/", views.generate_question, name="generate_question"),
    path("lesson/", views.generate_lesson_plan, name="generate_lesson_plan"),
    path("code/", views.code_review, name="code_review"),
]