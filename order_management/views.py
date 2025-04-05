from django.views.i18n import JsonResponse
from rest_framework import generics, status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from audit.models import AuditLog
from django.db.models import Q
from .models import Order, OrderItem, Shipment
from .filters import OrderFilter
from inventory_management.models import Product
from .serializers import (
    OrderSerializer,
    ShipmentSerializer,
)
from django.shortcuts import get_object_or_404
from django.utils import timezone



class OrderListView(APIView):
    def get(self, request):
        search_query = request.GET.get('search',"").strip()
        queryset = Order.objects.all()

        if search_query:
            # Search across multiple fields
            filtered_orders  = Order.objects.filter(
                Q(name__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(phone_number__icontains=search_query) |
                Q(order_number__icontains=search_query) |
                Q(status__icontains=search_query) |
                Q(payment_status__icontains=search_query) |
                Q(payment_method__icontains=search_query) |
                Q(return_reason__icontains=search_query) |
                Q(shipping_address__icontains=search_query) |
                Q(billing_address__icontains=search_query)
            )
        else:
            order_filter = OrderFilter(request.GET, queryset=Order.objects.all())
            filtered_orders = order_filter.qs

        if not filtered_orders.exists():
            return Response({"error": "No matching orders found"}, status=404)

        serializer = OrderSerializer(filtered_orders, many=True)
        return Response(serializer.data, status=200)


# Create a New Order
class CreateOrderView(APIView):
    def post(self, request):
        cart = request.data.get("cart")
        if not cart:
            return Response(
                {"detail": "No cart data provided."}, status=status.HTTP_400_BAD_REQUEST
            )

        order = Order.objects.create(
            name=request.data.get('name'),
            email=request.data.get('email'),
            shipping_address=request.data.get("shipping_address"),
            billing_address=request.data.get("billing_address", None),
        )

        total_amount = 0

        # Create Order Items from cart data
        for item in cart:
            product = get_object_or_404(Product, id=item["product_id"])
            quantity = item["quantity"]
            if quantity > product.stock:
                return JsonResponse(
                    {
                        "status": "error",
                        "details": f"'{product.name}' is currently out of stock.",
                    }
                )
            order_item = OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price_at_order=product.price,
            )
            total_amount += order_item.total_price

        order.total_amount = total_amount
        order.save()

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


class RequestReturnView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)

        if order.status != "delivered":
            return Response(
                {"detail": "Only delivered orders can be returned"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        order.return_requested = True
        order.return_reason = request.data.get("return_reason", "")
        order.save()
        return Response(
            {
                "details": "Your return request has been successfully submitted. Our team will review it and contact you shortly."
            },
            status=status.HTTP_200_OK,
        )


class ProcessReturnView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)

        if not order.return_requested:
            return Response(
                {"details": "No return request has been made for this order"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        approve_return = request.data.get("approve", False)
        if approve_return:
            order.return_approved = True
            return Response(
                {"details": "Return request approved"}, status=status.HTTP_200_OK
            )
        else:
            order.return_approved = False
            return Response(
                {"details": "Return request denied"}, status=status.HTTP_200_OK
            )


# View, Update, or Cancel an Order
class OrderDetailView(APIView):
    def get(self, request, pk):
        orders = get_object_or_404(Order, pk=pk)
        serializer = OrderSerializer(orders)
        return Response(serializer.data, status=200)

    def delete(self, request, pk):
        orders = get_object_or_404(Order, pk=pk)
        orders.status = "cancelled"

        # log in audit
        AuditLog.objects.create(
            action="cancelled",
            performed_by=request.user,
            resource_name="Order",
            resource_id=pk,
            details=f"Product {pk} cancelled",
        )

        return Response({"message": "Order successfully deleted"}, status=200)


class AdminOrderListView(generics.ListAPIView):
    permission_classes = [IsAdminUser]
    queryset = Order.objects.all()
    serializer_class = OrderSerializer


class UpdateOrderStatusView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        new_status = request.data.get("status")

        if new_status not in dict(Order.STATUS_CHOICES):
            return Response(
                {"detail": "Invalid status."}, status=status.HTTP_400_BAD_REQUEST
            )

        order.status = new_status
        order.save()
        return Response(
            {"detail": f"Order status updated to {new_status}."},
            status=status.HTTP_200_OK,
        )


# Handle Payments
class PaymentView(APIView):
    def post(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, user=request.user)

        if order.payment_method:
            return Response(
                {"detail": "Payment already made for this order."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        payment_data = {
            "order": order.id,
            "amount": order.total_amount,
            "payment_method": request.data.get("payment_method"),
            "status": "completed",
            "transaction_id": f'TRANSACTION-{order_id}-{timezone.now().strftime("%Y%m%d%H%M%S")}',
        }

        serializer = PaymentSerializer(data=payment_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Shipment Details and Tracking (Admin Only)
class ShipmentView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)

        if not order.payment or order.payment.status != "completed":
            return Response(
                {"detail": "Cannot create a shipment for unpaid orders."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        shipment_data = {
            "order": order.id,
            "tracking_number": request.data.get("tracking_number"),
            "carrier": request.data.get("carrier"),
            "estimated_delivery": request.data.get("estimated_delivery"),
            "status": "in_transit",
        }

        serializer = ShipmentSerializer(data=shipment_data)
        if serializer.is_valid():
            serializer.save()
            order.status = "shipped"
            order.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, order_id):
        shipment = get_object_or_404(Shipment, order__id=order_id)
        return Response(ShipmentSerializer(shipment).data, status=status.HTTP_200_OK)


class CancelOrderView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, order_id):
        # Get the specific order for the authenticated user
        order = get_object_or_404(Order, id=order_id)

        # Check if the order can be canceled (e.g., check if it's not already shipped or completed)
        if order.status in ["shipped", "completed"]:
            return Response(
                {
                    "detail": "This order cannot be canceled as it is already shipped or completed."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Update the order status to 'canceled'
        order.status = "canceled"
        order.save()

        return Response(
            {"detail": f"Order {order.id} has been successfully canceled."},
            status=status.HTTP_200_OK,
        )
