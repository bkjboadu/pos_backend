from django.urls import path
from .views import (
    ProductView,
    ProductDetailView
)

urlpatterns = [
    path("",ProductView.as_view(),name="product-view"),
    path("<int:pk>/",ProductDetailView.as_view(), name="product-detail-view")
]
