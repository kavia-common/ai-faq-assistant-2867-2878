from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import health, AskView, SearchView, AuthView, KnowledgeBaseViewSet

router = DefaultRouter()
router.register(r'kb', KnowledgeBaseViewSet, basename='kb')

urlpatterns = [
    path('health/', health, name='Health'),
    path('ask/', AskView.as_view(), name='Ask'),
    path('search/', SearchView.as_view(), name='Search'),
    path('auth/', AuthView.as_view(), name='Auth'),
    path('', include(router.urls)),
]
