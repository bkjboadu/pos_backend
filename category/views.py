from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from audit.models import AuditLog
from .models import Category
from .filters import CategoryFilter
from django.db.models import Q
from .serializers import CategorySerializer

class CategoryView(APIView):
    def get(self, request):
        search_query = request.GET.get('search', '')
        queryset = Category.objects.all()

        if search_query:
            category_filters = (
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query)
            )
            queryset = queryset.filter(category_filters)

        category_filter = CategoryFilter(request.GET, queryset=queryset)
        categories = category_filter.qs

        if not categories.exists():
            return Response({'message': 'No categories found'}, status=404)

        serializer = CategorySerializer(categories, many=True)
        return Response({'categories': serializer.data})

    def post(self, request):
        data = request.data
        serializer = CategorySerializer(data=data)
        if serializer.is_valid():
            category = serializer.save(created_by=request.user)
            AuditLog.objects.create(
                action='create',
                resource_name='Category',
                resource_id=category.id,
                performed_by=request.user
            )
            return Response({'message': 'Category created successfully'}, status=201)
        return Response(serializer.errors, status=400)

class CategoryDetailView(APIView):
    def get(self, request, pk):
        category = get_object_or_404(Category, pk=pk)
        serializer = CategorySerializer(category)
        return Response({'category': serializer.data}, status=200)

    def delete(self, request, pk):
        try:
            category = get_object_or_404(Category, pk=pk)
            category_id = category.id
            category.delete()

            AuditLog.objects.create(
                action='delete',
                resource_id=category.id,
                performed_by=request.user,
                resource_name='Category',
            )
            return Response({"message": "Category deleted successfully"}, status=200)
        except Category.DoesNotExist:
            return Response({"error": "Category not found"}, status=404)

    def patch(self, request, pk):
        try:
            category = get_object_or_404(Category, pk=pk)
            name = request.data.get('name', '')
            description = request.data.get('description', '')
            if name:
                category.name = name
            if description:
                category.description = description

            AuditLog.objects.create(
                action='update',
                resource_name='Category',
                resource_id=category.id,
                performed_by=request.user,
            )
            category.save()
            return Response({"message": "Category updated successfully"}, status=200)
        except Category.DoesNotExist:
            return Response({"error": "Category not found"}, status=404)
