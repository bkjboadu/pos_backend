from .serializers import AuditLogSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import AuditLog
from django.db.models import Q
from .filters import AuditLogFilter


class AuditLogView(APIView):
    def get(self, request):
        search_query = request.GET.get('search', '').strip()
        queryset = AuditLog.objects.all()

        if search_query:
            search_filters = (
                Q(action__icontains=search_query)|
                Q(performed_by__first_name__icontains=search_query)|
                Q(resource_name__icontains=search_query) |
                Q(resource_id__icontains=search_query) |
                Q(details__icontains=search_query)
            )

            if search_query.isdigit():
                search_filters |= Q(performed_by__id=search_query) | Q(resource_id=search_query)

            queryset = queryset.filter(search_filters)

        audit_filter = AuditLogFilter(request.GET, queryset=queryset)
        filtered_audits = audit_filter.qs

        if not filtered_audits.exists():
            return Response({'error':"No matching audits found"}, status=404)

        serializer = AuditLogSerializer(filtered_audits, many=True)
        return Response(serializer.data, status=200)

class AuditLogDetailView(APIView):
    def get(self, request, pk):
        try:
            audit_instance = AuditLog.objects.get(pk=pk)
        except AuditLog.DoesNotExists:
            return Response({"error", "AudiLogs instance does not exist"}, status=404)

        serializer = AuditLogSerializer(audit_instance)
        return Response(serializer.data, status=200)
