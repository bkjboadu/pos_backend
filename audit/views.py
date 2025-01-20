from .serializers import AuditLogSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import AuditLog


class AuditLogView(APIView):
    def get(self, request):
        try:
            audit_instance = AuditLog.objects.all()
        except AuditLog.DoesNotExists:
            return Response({"error", "AudiLogs instance does not exist"}, status=404)

        serializer = AuditLogSerializer(audit_instance, many=True)
        return Response(serializer.data, status=200)


class AuditLogDetailView(APIView):
    def get(self, request, pk):
        try:
            audit_instance = AuditLog.objects.get(pk=pk)
        except AuditLog.DoesNotExists:
            return Response({"error", "AudiLogs instance does not exist"}, status=404)

        serializer = AuditLogSerializer(audit_instance)
        return Response(serializer.data, status=200)

    def delete(self, request, pk):
        try:
            audit_instance = AuditLog.objects.get(pk=pk)
        except AuditLog.DoesNotExists:
            return Response({"error", "AudiLogs instance does not exist"}, status=404)

        audit_instance.delete()
        return Response({"message": "Audit instance successfully saved"}, status=200)
