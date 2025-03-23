from django.urls import path
from .views import BranchView, BranchDetailView, DeactivateBranchView, ActivateBranchView

urlpatterns = [
    path("", BranchView.as_view(), name="branch-view"),
    path("<int:pk>/", BranchDetailView.as_view(), name="branch-detail-view"),
    path("<int:pk>/deactivate/", DeactivateBranchView.as_view(), name="branch-deactivate"),
    path("<int:pk>/activate/", ActivateBranchView.as_view(), name="branch-deactivate"),
]
