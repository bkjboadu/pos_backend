

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('companies/',include('companies.urls')),
    path('users/',include('users.urls')),
    path('sales/',include('sales.urls')),
    path('products/',include('products.urls')),
    path("admin/", admin.site.urls),
]
