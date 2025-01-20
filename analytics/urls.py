from django.urls import path
from .views import (
    SalesByDateView,
    SalesByProductView,
    InventoryManagementAPIView,
    PaymentRevenueInsightsAPIView,
)

urlpatterns = [
    path("sales-by-date/", SalesByDateView.as_view(), name="sales_by_date"),
    path("sales-by-product/", SalesByProductView.as_view(), name="sales_by_product"),
    path("inventory", InventoryManagementAPIView.as_view(), name="inv_totals"),
    path("payment", PaymentRevenueInsightsAPIView.as_view(), name="payment_totals"),
]
