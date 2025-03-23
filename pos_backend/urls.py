from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("accounts/", include("users.urls")),
    path("sales/", include("sales.urls")),
    path("inventory/", include("inventory_management.urls")),
    path("admin/", admin.site.urls),
    path("payment/", include("payment.urls")),
    path("customers/", include("customers.urls")),
    path("branches/", include("branches.urls")),
    path("audits/", include("audit.urls")),
    path('dashboard/', include('dashboard.urls'))
]
