from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Product, StockInput
from .serializers import ProductSerializer, StockInputSerializer
from audit.models import AuditLog


class ProductView(APIView):

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

            # log in audit
            AuditLog.objects.create(
                action="create",
                performed_by=request.user,
                resource_name="Product",
                resource_id=product.id,
                details=f"Product {product.id} created",
            )
            return Response(ProductSerializer(product).data, status=201)
        return Response(serializer.errors, status=400)


class ProductDetailView(APIView):

    def get(self, request, pk=None, barcode=None):
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
            return Response({"error": "Product not found"}, status=404)

        # Check user permissions
        serializer = ProductSerializer(product)
        return Response(serializer.data, status=200)

    def delete(self, request, pk, barcode=None):
        if not (request.user.is_superuser or request.user.role=='manager'):
            return Response({"message":"You do not have permission to access this resource"}, status=403)


        # fetch product to delete
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
        deleted_product_id = product.id
        product.delete()

        # log in audit
        AuditLog.objects.create(
            action="delete",
            performed_by=request.user,
            resource_name="Product",
            resource_id=deleted_product_id,
            details=f"Product {product.id} deleted",
        )

        return Response({"message": "Product successfully deleted"}, status=200)

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

        data = request.data


        if "stock" in data:
            if not (request.user.is_superuser or request.user.role=='manager'):
                return Response({"message":"You do not have permission to access this resource"}, status=403)

        serializer = ProductSerializer(product, data=data, partial=True)

        if serializer.is_valid():
            # Log changes for audit
            changes = []
            for field, new_value in serializer.validated_data.items():
                old_value = getattr(product, field, None)
                if old_value != new_value:
                    changes.append(f"{field}: '{old_value}' -> '{new_value}'")

            details = f"Updated fields: {', '.join(changes)}"

            updated_product = serializer.save(update_by=request.user)

            # log in audit
            AuditLog.objects.create(
                action="update",
                performed_by=request.user,
                resource_name="Product",
                resource_id=product.id,
                details=details,
            )
            return Response(ProductSerializer(updated_product).data, status=200)
        return Response(serializer.errors, status=400)


class StockView(APIView):
    permission_classes = []

    def get(self, request):
        stock_inputs = StockInput.objects.all()
        serializer = StockInputSerializer(stock_inputs, many=True)
        return Response(serializer.data, status=200)

    def post(self, request):
        data = request.data
        serializer = StockInputSerializer(data=data)

        if serializer.is_valid():
            stock_input = serializer.save(added_by=request.user)
            return Response(StockInputSerializer(stock_input).data, status=200)
        else:
            return Response(serializer.errors, status=400)


class StockDetailView(APIView):
    def get(self, request, pk):
        try:
            stockinput_instance = StockInput.objects.get(pk=pk)
        except StockInput.DoesNotExist:
            return Response({"error": "StockInput instance does not exist"})

        serializer = StockInputSerializer(stockinput_instance)
        return Response(serializer.data, status=200)

    def delete(self, request, pk):
        try:
            stockinput_instance = StockInput.objects.get(pk=pk)
        except StockInput.DoesNotExist:
            return Response({"error": "StockInput instance does not exist"})

        try:
            product = stockinput_instance.product

            if stockinput_instance.quantity > product.stock:
                raise ValueError(
                    f"Insufficient stock: Cannot deduct {stockinput_instance.quantity} from {product.stock}."
                )

            product.stock -= stockinput_instance.quantity
            product.save()

        except ValueError as e:
            return Response({"error": {e}}, status=400)

        deleted_stockinput_instance = stockinput_instance.id
        stockinput_instance.delete()

        # log in audit
        AuditLog.objects.create(
            action="delete",
            performed_by=request.user,
            resource_name="StockInput",
            resource_id=deleted_stockinput_instance,
            details=f"StockInput {stockinput_instance.id} deleted",
        )

        return Response(
            {"message": "StockInput instance successfully delete"}, status=200
        )

    def patch(self, request, pk):
        try:
            stockinput_instance = StockInput.objects.get(pk=pk)
        except StockInput.DoesNotExist:
            return Response({"error": "StockInput instance does not exist"})

        data = request.data
        serializer = StockInputSerializer(stockinput_instance, data=data, partial=True)

        if serializer.is_valid():
            # Access the validated data
            validated_data = serializer.validated_data
            new_quantity = validated_data.get("quantity", stockinput_instance.quantity)

            # check if quantity was updated
            if new_quantity != stockinput_instance.quantity:
                product = stockinput_instance.product

                quantity_diff = new_quantity - stockinput_instance.quantity

                if quantity_diff > 0 and quantity_diff > product.stock:
                    raise Response(
                        {
                            "error": f"Insufficient stock: Cannot deduct {stockinput_instance.quantity} from {product.stock}"
                        }
                    )

                product.stock += quantity_diff
                product.save()

            changes = []
            for field, new_value in validated_data.items():
                old_value = getattr(stockinput_instance, field, None)
                if new_value != old_value:
                    changes.append(f"{field}: '{old_value}' -> '{new_value}'")

            details = f"Updated fields: {', '.join(changes)}"

            instance = serializer.save()

            # log in audit
            AuditLog.objects.create(
                action="update",
                performed_by=request.user,
                resource_name="StockInput",
                resource_id=stockinput_instance.id,
                details=details,
            )

            return Response(StockInputSerializer(instance).data, status=200)
        else:
            return Response(serializer.errors, status=400)
