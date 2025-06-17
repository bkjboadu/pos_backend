from customers.models import Customer
from customers.serializers import CustomerSerializer
from inventory_management.serializers import ProductSerializer
from inventory_management.models import Product
from order_management.models import Order
from order_management.serializers import OrderSerializer
from sales.models import Transaction, TransactionItem

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from core.permissions import IsSuperUserOrManager
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta

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


class AdminDashboardView(APIView):
    """Dashboard view for superadmins and managers"""
    permission_classes = [IsAuthenticated, IsSuperUserOrManager]

    def get(self, request):
        # Get query parameters for filtering
        period = request.query_params.get('period', 'daily')  # daily, weekly, monthly
        branch_id = request.query_params.get('branch')
        cashier_id = request.query_params.get('cashier')

        # Calculate date ranges based on period
        today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        if period == 'daily':
            start_date = today
            end_date = today + timedelta(days=1)
        elif period == 'weekly':
            start_date = today - timedelta(days=today.weekday())
            end_date = start_date + timedelta(days=7)
        elif period == 'monthly':
            start_date = today.replace(day=1)
            next_month = today.month + 1 if today.month < 12 else 1
            next_month_year = today.year if today.month < 12 else today.year + 1
            end_date = today.replace(year=next_month_year, month=next_month, day=1)
        else:
            return Response({"error": "Invalid period. Use 'daily', 'weekly', or 'monthly'"}, status=400)
        
        # Base queryset for transactions in the date range
        transactions = Transaction.objects.filter(created_at__gte=start_date, created_at__lt=end_date)
        
        # Apply additional filters
        if branch_id:
            transactions = transactions.filter(branch_id=branch_id)
        if cashier_id:
            transactions = transactions.filter(created_by_id=cashier_id)
        
        # Get total sales in the period
        total_sales = transactions.aggregate(total=Sum('total_amount'))['total'] or 0
        
        # Get most sold items
        most_sold_items = TransactionItem.objects.filter(
            transaction__in=transactions
        ).values(
            'product__id', 
            'product__name', 
            'product__price'
        ).annotate(
            total_quantity=Sum('quantity'),
            total_value=Sum('total_amount')
        ).order_by('-total_quantity')[:10]
        
        # Get sales by cashier
        sales_by_cashier = transactions.values(
            'created_by__id',
            'created_by__first_name',
            'created_by__last_name',
        ).annotate(
            total_sales=Sum('total_amount'),
            transactions_count=Count('id')
        ).order_by('-total_sales')
        
        # Get sales by branch
        sales_by_branch = transactions.values(
            'branch__id',
            'branch__name'
        ).annotate(
            total_sales=Sum('total_amount'),
            transactions_count=Count('id')
        ).order_by('-total_sales')
        
        response = {
            "period": period,
            "start_date": start_date,
            "end_date": end_date,
            "total_sales": total_sales,
            "most_sold_items": list(most_sold_items),
            "sales_by_cashier": list(sales_by_cashier),
            "sales_by_branch": list(sales_by_branch),
            "transactions_count": transactions.count(),
        }
        
        return Response(response, status=200)


class CashierDashboardView(APIView):
    """Dashboard view for cashiers to see their own performance"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Only show data for the logged-in user
        cashier = request.user
        
        # Get query parameters for filtering
        period = request.query_params.get('period', 'daily')  # daily, weekly, monthly
        
        # Calculate date ranges based on period
        today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        if period == 'daily':
            start_date = today
            end_date = today + timedelta(days=1)
        elif period == 'weekly':
            start_date = today - timedelta(days=today.weekday())
            end_date = start_date + timedelta(days=7)
        elif period == 'monthly':
            start_date = today.replace(day=1)
            next_month = today.month + 1 if today.month < 12 else 1
            next_month_year = today.year if today.month < 12 else today.year + 1
            end_date = today.replace(year=next_month_year, month=next_month, day=1)
        else:
            return Response({"error": "Invalid period. Use 'daily', 'weekly', or 'monthly'"}, status=400)
        
        # Get transactions by this cashier in the specified period
        transactions = Transaction.objects.filter(
            created_by=cashier,
            created_at__gte=start_date,
            created_at__lt=end_date
        )
        
        # Calculate metrics
        total_sales = transactions.aggregate(total=Sum('total_amount'))['total'] or 0
        transaction_count = transactions.count()
        
        # Get top selling items for this cashier
        top_items = TransactionItem.objects.filter(
            transaction__in=transactions
        ).values(
            'product__id',
            'product__name'
        ).annotate(
            quantity_sold=Sum('quantity'),
            total_value=Sum('total_amount')
        ).order_by('-quantity_sold')[:5]
        
        # Get daily breakdown if viewing weekly or monthly
        daily_breakdown = None
        if period in ['weekly', 'monthly']:
            daily_breakdown = transactions.values('created_at__date').annotate(
                day_total=Sum('total_amount'),
                transactions_count=Count('id')
            ).order_by('created_at__date')
        
        response = {
            "period": period,
            "start_date": start_date,
            "end_date": end_date,
            "total_sales": total_sales,
            "transaction_count": transaction_count,
            "top_selling_items": list(top_items),
        }
        
        if daily_breakdown:
            response["daily_breakdown"] = list(daily_breakdown)

        return Response(response, status=200)
