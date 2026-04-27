from django.urls import path
from . import views

urlpatterns = [
    path('ask/', views.chat_ask, name='chat-ask'),
    path('stream/', views.chat_stream, name='chat-stream'),
    path('session/', views.chat_session_list, name='chat-session-list'),
    path('history/<str:session_id>/', views.chat_history, name='chat-history'),
]  