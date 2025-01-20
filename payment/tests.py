from rest_framework.test import APITestCase
from rest_framework import status
from .models import Payment
from django.contrib.auth import get_user_model
from inventory_management.models import Product
from decimal import Decimal

User = get_user_model()


class PayCashViewTest(APITestCase):
    def setUp(self):
        # Create a superuser
        self.superuser = User.objects.create_superuser(
            first_name="bright",
            last_name="boadu",
            email="brbojr@gmail.com",
            password="3tjppg6BB!",
        )

        self.client.force_authenticate(user=self.superuser)
        self.Product1 = Product.objects.create(
            name="Milk", barcode="Milk009", price=2, stock=10
        )
        self.Product2 = Product.objects.create(
            name="Rice", barcode="Rice1010", price=6, stock=100
        )

    def test_post_paycash(self):
        # Send a POST request
        data = {
            "items": [
                {"product": self.Product1.id, "quantity": 5},
                {"product": self.Product2.id, "quantity": 3},
            ],
            "amount": 500,
        }

        response = self.client.post("/payment/pay-with-cash/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["balance"], Decimal("472.00"))
        self.assertEqual(self.Product1.stock, 10)
        self.assertEqual(self.Product2.stock, 100)
