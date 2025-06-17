from django.urls import path
from .views import DashboardView, AdminDashboardView, CashierDashboardView

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('admin/', AdminDashboardView.as_view(), name='admin-dashboard'),
    path('cashier/', CashierDashboardView.as_view(), name='cashier-dashboard'),
]