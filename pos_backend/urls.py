from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("accounts/", include("users.urls")),
    path("sales/", include("sales.urls")),
    path("inventory/", include("inventory_management.urls")),
    path("admin/", admin.site.urls),
    path("payment/", include("payment.urls")),
    path("customers/", include("customers.urls")),
    path("analytics/", include("analytics.urls"))
]
