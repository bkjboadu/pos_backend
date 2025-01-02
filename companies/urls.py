from django.urls import path
from .views import BranchView, BranchDetailView, CompanyView, CompanyDetailView

urlpatterns = [
    path("", CompanyView.as_view(), name="company-list-create"),
    path("<int:pk>/", CompanyDetailView.as_view(), name="company=detail"),
    path("branch/", BranchView.as_view(), name="branch-list-create"),
    path("branch/<int:pk>/", BranchDetailView.as_view(), name="branch-detail"),
]
