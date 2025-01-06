from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("users/", include("users.urls")),
    path("sales/", include("sales.urls")),
    path("inventory/", include("inventory_management.urls")),
    path("admin/", admin.site.urls),
]
