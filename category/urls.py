from django.urls import path
from .views import CategoryView,CategoryDetailView

urlpatterns = [
    path('', CategoryView.as_view(), name='category-list'),
    path('<int:pk>/', CategoryDetailView.as_view(), name='category-detail'),
]
