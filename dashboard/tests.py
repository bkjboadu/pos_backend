from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from sales.models import Transaction, TransactionItem
from inventory_management.models import Product
from branches.models import Branch
from django.utils import timezone

User = get_user_model()

class DashboardViewsTest(APITestCase):
    def setUp(self):
        # Create users with different roles
        self.admin_user = User.objects.create_superuser(
            first_name="Admin",
            last_name="User",
            email="admin@example.com",
            password="admin123",
            role="admin_manager"
        )
        
        self.cashier_user = User.objects.create_user(
            first_name="Cashier",
            last_name="User",
            email="cashier@example.com",
            password="cashier123",
            role="cashier"
        )
        
        # Create a branch
        self.branch = Branch.objects.create(
            id=1,
            name="Main Branch", 
            address="123 Main St",
            created_by=self.admin_user
        )
        
        # Add branch to users
        self.admin_user.branches.add(self.branch)
        self.cashier_user.branches.add(self.branch)
        
        # Create some products
        self.product1 = Product.objects.create(
            name="Test Product 1", 
            barcode="TP001", 
            price=10.00,
            stock=50,
            branch=self.branch
            
        )
        
        self.product2 = Product.objects.create(
            name="Test Product 2", 
            barcode="TP002", 
            price=20.00,
            stock=30,
            branch=self.branch
        )
        
        # Create transactions
        self.transaction1 = Transaction.objects.create(
            created_by=self.cashier_user,
            branch=self.branch,
            total_amount=50.00
        )
        
        self.transaction2 = Transaction.objects.create(
            created_by=self.cashier_user,
            branch=self.branch,
            total_amount=100.00
        )
        
        # Create transaction items
        TransactionItem.objects.create(
            transaction=self.transaction1,
            product=self.product1,
            quantity=2,
            total_amount=20.00
        )
        
        TransactionItem.objects.create(
            transaction=self.transaction1,
            product=self.product2,
            quantity=1,
            total_amount=20.00
        )
        
        TransactionItem.objects.create(
            transaction=self.transaction2,
            product=self.product1,
            quantity=5,
            total_amount=50.00
        )
        
        TransactionItem.objects.create(
            transaction=self.transaction2,
            product=self.product2,
            quantity=2,
            total_amount=40.00
        )
    
    def test_admin_dashboard_access(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/dashboard/admin/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check if the response contains the expected fields
        self.assertIn('total_sales', response.data)
        self.assertIn('most_sold_items', response.data)
        self.assertIn('sales_by_cashier', response.data)
        self.assertIn('sales_by_branch', response.data)
    
    def test_cashier_dashboard_access(self):
        self.client.force_authenticate(user=self.cashier_user)
        response = self.client.get('/dashboard/cashier/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check if the response contains the expected fields
        self.assertIn('total_sales', response.data)
        self.assertIn('transaction_count', response.data)
        self.assertIn('top_selling_items', response.data)
    
    def test_cashier_cannot_access_admin_dashboard(self):
        self.client.force_authenticate(user=self.cashier_user)
        response = self.client.get('/dashboard/admin/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_period_filtering(self):
        self.client.force_authenticate(user=self.admin_user)
        
        # Test daily filter
        response = self.client.get('/dashboard/admin/?period=daily')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['period'], 'daily')
        
        # Test weekly filter
        response = self.client.get('/dashboard/admin/?period=weekly')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['period'], 'weekly')
        
        # Test monthly filter
        response = self.client.get('/dashboard/admin/?period=monthly')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['period'], 'monthly')
        
        # Test invalid filter
        response = self.client.get('/dashboard/admin/?period=invalid')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)