from customers.models import Customer
from customers.serializers import CustomerSerializer
from inventory_management.serializers import ProductSerializer
from inventory_management.models import Product
from order_management.models import Order
from order_management.serializers import OrderSerializer
from sales.models import Transaction, TransactionItem
from rest_framework.views import APIViews
from rest_framework.response import Response
from django.db.models import Sum


class DashboardView(APIViews):
    def get(self):
        try:
            # get total sales
            total_sales = Transaction.objects.aggregate(total=Sum('total_amount'))['total']

            # get unclosed orders
            undelivered_orders = Order.objects.exclude(status="delivered")
            undeliverd_orders_count = undelivered_orders.count()
            order_serializer = OrderSerializer(undelivered_orders, many=True)

            # get all customers
            customers = Customer.objects.count()

            # get all product in stock
            total_stock = Product.objects.aggregate(total=Sum('stock'))['total']

            # get low stock items
            low_stock_product = Product.objects.filter(stock__lt=5 )
            low_stock_product = ProductSerializer(low_stock_product, many=True)

            response = {
                "low stock items": low_stock_product,
                "inventory": total_stock,
                "Customers": customers,
                "Undelivered_Orders": order_serializer,
                "Undelivered_Orders_Count": undeliverd_orders_count,
                "total_sales": total_sales
            }

            return Response(response, status=200)
        except Exception as e:
            return Response({'error':{e}}, status=400)
