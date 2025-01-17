from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Transaction, TransactionItem
from inventory_management.models import Product

User = get_user_model()

class TransactionViewTest(APITestCase):
    def setUp(self):
        # Create a superuser
        self.superuser = User.objects.create_superuser(
            first_name="bright",
            last_name="boadu",
            email="brbojr@gmail.com",
            password="3tjppg6BB!"
        )

        self.client.force_authenticate(user=self.superuser)

        self.Product1 = Product.objects.create(
            name="Milk",
            barcode="Milk009",
            price=67
        )

        self.Transaction1 = Transaction.objects.create(
            created_by=self.superuser
        )

        self.Transaction2 = Transaction.objects.create()


    def test_get_transaction(self):
        # send GET request
        response = self.client.get("/sales/transactions/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data),2)


    def test_post_transaction(self):
        # send POST request
        data = {
            "created_by":self.superuser
        }
        response = self.client.post('/sales/transactions/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class TransactionDetailViewTest(APITestCase):
    def setUp(self):
        # Create a superuser
        self.superuser = User.objects.create_superuser(
            first_name="bright",
            last_name="boadu",
            email="brbojr@gmail.com",
            password="3tjppg6BB!"
        )

        self.client.force_authenticate(user=self.superuser)

        self.Product1 = Product.objects.create(
            name="Milk",
            barcode="Milk009",
            price=67
        )

        self.Transaction1 = Transaction.objects.create(
            created_by=self.superuser
        )

        self.Transaction2 = Transaction.objects.create()

    def test_get_transaction(self):
        # send GET request
        response = self.client.get(f"/sales/transactions/{self.Transaction1.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_transaction(self):
        # send DELETE request
        response = self.client.delete(f"/sales/transactions/{self.Transaction1.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Transaction.objects.filter(id=self.Transaction1.id).exists())

    def test_patch_transaction(self):
        # send PUT request
        data = {
            "total_amount":100
        }
        response = self.client.patch(f"/sales/transactions/{self.Transaction1.id}/", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_amount'], "100.00")



class TransactionItemViewTest(APITestCase):
    def setUp(self):
        # Create a superuser
        self.superuser = User.objects.create_superuser(
            first_name="bright",
            last_name="boadu",
            email="brbojr@gmail.com",
            password="3tjppg6BB!"
        )

        self.client.force_authenticate(user=self.superuser)

        self.Product1 = Product.objects.create(
            name="Milk",
            barcode="Milk009",
            price=67,
            stock=57
        )

        self.Transaction1 = Transaction.objects.create(
            created_by=self.superuser
        )

        self.TransactionItem1 = TransactionItem.objects.create(
            transaction=self.Transaction1,
            product=self.Product1,
            quantity=2
        )


    def test_get_transactionitem(self):
        # send GET request
        response = self.client.get("/sales/transactions-items/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data),1)


    def test_post_transactionitem(self):
        # send POST request
        data = {
            "transaction":self.Transaction1.id,
            "product":self.Product1.id,
            "quantity":2,
        }
        response = self.client.post("/sales/transactions-items/", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(TransactionItem.objects.count(), 2)

        # Verify the created TransactionItem
        new_transaction_item = TransactionItem.objects.last()
        self.assertEqual(new_transaction_item.transaction, self.Transaction1)
        self.assertEqual(new_transaction_item.product, self.Product1)
        self.assertEqual(new_transaction_item.quantity, 2)
        self.assertEqual(new_transaction_item.total_amount, 134)



class TransactionItemDetailViewTest(APITestCase):
    def setUp(self):
        # Create a superuser
        self.superuser = User.objects.create_superuser(
            first_name="bright",
            last_name="boadu",
            email="brbojr@gmail.com",
            password="3tjppg6BB!"
        )

        self.client.force_authenticate(user=self.superuser)

        self.Product1 = Product.objects.create(
            name="Milk",
            barcode="Milk009",
            price=67,
            stock=57
        )

        self.Transaction1 = Transaction.objects.create(
            created_by=self.superuser
        )

        self.TransactionItem1 = TransactionItem.objects.create(
            transaction=self.Transaction1,
            product=self.Product1,
            quantity=2
        )


    def test_get_transactionitem_by_id(self):
        # send GET request
        response = self.client.get(f"/sales/transactions-items/{self.TransactionItem1.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['quantity'],2)
        self.assertEqual(response.data['total_amount'],"134.00")


    def test_delete_transactionitem_by_id(self):
        # send DELETE request
        response = self.client.delete(f"/sales/transactions-items/{self.TransactionItem1.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(TransactionItem.objects.filter(id=self.TransactionItem1.id))

    def test_put_transactionitem_by_id(self):
        data = {
            "transaction":self.Transaction1.id,
            "product":self.Product1.id,
            "quantity":3,
        }
        response = self.client.put(f"/sales/transactions-items/{self.TransactionItem1.id}/", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['quantity'],3)
        self.assertEqual(response.data['total_amount'],"201.00")


    def test_patch_transactionitem_by_id(self):
        data = {
            "quantity":4,
        }
        response = self.client.patch(f"/sales/transactions-items/{self.TransactionItem1.id}/", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['quantity'],4)
        self.assertEqual(response.data['total_amount'],"268.00")
