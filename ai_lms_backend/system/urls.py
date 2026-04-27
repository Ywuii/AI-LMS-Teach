from django.urls import path

from system.views import AsyncRouteViewSet

urlpatterns = [
    path("asyncroutes/", AsyncRouteViewSet.as_view()),
]

