from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Product
from .serializers import ProductSerializer
from core.permissions import IsSuperUserOrManager


class ProductView(APIView):
    permission_classes = [IsSuperUserOrManager]

    def get(self, request):
        try:
            product = Product.objects.all()
        except Product.DoesNotExist:
            return Response({"error": "Products not found"}, status=404)

        # Check user permissions
        serializer = ProductSerializer(product, many=True)
        return Response(serializer.data, status=200)

    def post(self, request):
        data = request.data
        serializer = ProductSerializer(data=data)

        if serializer.is_valid():
            product = serializer.save(created_by=request.user, updated_by=request.user)
            return Response(ProductSerializer(product).data, status=201)
        return Response(serializer.errors, status=400)


class ProductDetailView(APIView):
    permission_classes = [IsSuperUserOrManager]

    def get(self, request, pk, barcode=None):
        try:
            if pk:
                product = Product.objects.get(pk=pk)
            elif barcode:
                product = Product.objects.get(barcode=barcode)
            else:
                return Response(
                    {"error": "Product ID or Barcode is required"}, status=400
                )
        except Product.DoesNotExist:
            return Response({"error": "Branch not found"}, status=404)

        # Check user permissions
        serializer = ProductSerializer(product)
        return Response(serializer.data, status=200)

    def delete(self, request, pk, barcode=None):
        # fetch product to update
        try:
            if pk:
                product = Product.objects.get(pk=pk)
            elif barcode:
                product = Product.objects.get(barcode=barcode)
            else:
                return Response({"error": "Product ID or Barcode required"}, status=400)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=404)

        # Check user permissions
        product.delete()
        return Response({"message": "Product successfully deleted"})

    def patch(self, request, pk, barcode=None):
        # fetch product to update
        try:
            if pk:
                product = Product.objects.get(pk=pk)
            elif barcode:
                product = Product.objects.get(barcode=barcode)
            else:
                return Response({"error": "Product ID or Barcode required"}, status=400)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=404)

        # Check user permissions

        data = request.data.copy()
        serializer = ProductSerializer(product, data=data, partial=True)

        if serializer.is_valid():
            product = serializer.save(update_by=request.user)
            return Response(ProductSerializer(product).data, status=200)
        return Response(serializer.errors, status=400)

    def put(self, request, pk, barcode=None):
        # fetch product to update
        try:
            if pk:
                product = Product.objects.get(pk=pk)
            elif barcode:
                product = Product.objects.get(barcode=barcode)
            else:
                return Response({"error": "Product ID or Barcode required"}, status=400)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=404)

        # Check user permissions

        data = request.data.copy()
        serializer = ProductSerializer(product, data=data)

        if serializer.is_valid():
            product = serializer.save(update_by=request.user)
            return Response(ProductSerializer(product).data, status=200)
        return Response(serializer.errors, status=400)
