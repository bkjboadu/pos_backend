from django.urls import path
from .views import BranchView, BranchDetailView

urlpatterns = [
    path("",BranchView.as_view(), name='branch-view'),
    path("<int:pk>/",BranchDetailView.as_view(), name='branch-detail-view')
]
