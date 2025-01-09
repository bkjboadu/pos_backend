from django.urls import path
from .views import CustomerView, CustomerDetailView

urlpatterns = [
    path('customers/', CustomerView.as_view(), name='customer-list'),
    path('customers/<int:pk>/', CustomerDetailView.as_view(), name='customer-detail'),
]
