from django.urls import path
from .views import (
    ProductView,
    ProductDetailView,
    StockDetailView,
    StockView
)

urlpatterns = [
    path("", ProductView.as_view(), name="product-view"),
    path("<int:pk>/", ProductDetailView.as_view(), name="product-detail-pk"),
    path("barcode/<str:barcode>/", ProductDetailView.as_view(), name="product-detail-barcode"),
    path('stock-input/', StockView.as_view(), name="stock-view"),
    path('stock-input/<int:pk>/', StockDetailView.as_view(), name='stock-detail-view')
]
