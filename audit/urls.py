from django.urls import path
from .views import AuditLogView, AuditLogDetailView

urlpatterns = [
    path("", AuditLogView.as_view(), name="audit-views"),
    path("<int:pk>/", AuditLogDetailView.as_view(), name="audit-detail-views"),
]
