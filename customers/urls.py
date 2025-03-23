from django.urls import path
from .views import CustomerView, CustomerDetailView,DeactivateCustomerView, ActivateCustomerView

urlpatterns = [
    path("", CustomerView.as_view(), name="customer-list"),
    path("<int:pk>/", CustomerDetailView.as_view(), name="customer-detail"),
    path("<int:pk>/deactivate/", DeactivateCustomerView.as_view(), name="customer-deactivate"),
    path("<int:pk>/activate/", ActivateCustomerView.as_view(), name="customer-deactivate"),
]
