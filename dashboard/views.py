from customers.models import Customer
from customers.serializers import CustomerSerializer
from inventory_management.serializers import ProductSerializer
from inventory_management.models import Product
from order_management.models import Order
from order_management.serializers import OrderSerializer
from sales.models import Transaction, TransactionItem
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum


class DashboardView(APIView):
    def get(self, request):
        try:
            # get total sales
            total_sales = Transaction.objects.aggregate(total=Sum('total_amount'))['total'] or 0

            # get unclosed orders
            undelivered_orders = Order.objects.exclude(status="delivered")
            order_serializer = OrderSerializer(undelivered_orders, many=True)

            # get all customers
            customers = Customer.objects.count()

            # get all product in stock
            total_stock = Product.objects.aggregate(total=Sum('stock'))['total'] or 0

            # get low stock items
            low_stock_product = Product.objects.filter(stock__lt=5 )
            low_stock_product = ProductSerializer(low_stock_product, many=True)

            response = {
                "low stock items": low_stock_product.data,
                "inventory": total_stock,
                "Customers": customers,
                "Undelivered_Orders": order_serializer.data,
                "total_sales": total_sales
            }

            return Response(response, status=200)
        except Exception as e:
            return Response({'error':{e}}, status=400)
