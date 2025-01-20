from .models import Branch
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from .serializers import BranchSerializer


class BranchView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        branches = Branch.objects.all()
        serializer = BranchSerializer(branches, many=True)
        return Response(serializer.data, status=200)

    def post(self, request):
        data = request.data
        serializer = BranchSerializer(data=data)
        if serializer.is_valid():
            branch = serializer.save(created_by=request.user, updated_by=request.user)
            return Response(BranchSerializer(branch).data, status=201)
        return Response(serializer.errors, status=400)


class BranchDetailView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, pk=None):
        # fetch branch
        try:
            if pk:
                branch = Branch.objects.get(pk=pk)
            else:
                return Response({"error": "Branch ID is required"}, status=400)
        except Branch.DoesNotExist:
            return Response({"error": "Branch not found"}, status=404)

        # Check user permissions
        serializer = BranchSerializer(branch)
        return Response(serializer.data, status=200)

    def delete(self, request, pk):
        # fetch product to delete
        try:
            if pk:
                branch = Branch.objects.get(pk=pk)
            else:
                return Response({"error": "Branch ID is required"}, status=400)
        except Branch.DoesNotExist:
            return Response({"error": "Branch not found"}, status=404)

        # Check user permissions
        branch.delete()
        return Response({"message": "Branch successfully deleted"}, status=200)

    def patch(self, request, pk):
        # fetch branch to update
        try:
            if pk:
                branch = Branch.objects.get(pk=pk)
            else:
                return Response({"error": "Branch ID is required"}, status=400)
        except Branch.DoesNotExist:
            return Response({"error": "Branch not found"}, status=404)

        # Check user permissions
        data = request.data.copy()
        serializer = BranchSerializer(branch, data=data, partial=True)

        if serializer.is_valid():
            branch = serializer.save(update_by=request.user)
            return Response(BranchSerializer(branch).data, status=200)
        return Response(serializer.errors, status=400)

    def put(self, request, pk, barcode=None):
        # Fetch branch to update fully
        try:
            if pk:
                branch = Branch.objects.get(pk=pk)
            else:
                return Response({"error": "Branch ID is required"}, status=400)
        except Branch.DoesNotExist:
            return Response({"error": "Branch not found"}, status=404)

        # Check user permissions
        data = request.data.copy()
        serializer = BranchSerializer(branch, data=data)

        if serializer.is_valid():
            branch = serializer.save(update_by=request.user)
            return Response(BranchSerializer(branch).data, status=200)
        return Response(serializer.errors, status=400)
