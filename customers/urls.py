from django.urls import path
from .views import CustomerView, CustomerDetailView

urlpatterns = [
    path("", CustomerView.as_view(), name="customer-list"),
    path("<int:pk>/", CustomerDetailView.as_view(), name="customer-detail"),
]
