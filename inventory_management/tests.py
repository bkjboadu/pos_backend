from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Product


User = get_user_model()

class ProductViewTests(APITestCase):
    def setUp(self):
        # Create a superuser for authentication
        self.superuser = User.objects.create_superuser(
            first_name='admin',
            last_name="super",
            email="admin@example.com",
            password="admin123"
        )
        self.client.force_authenticate(user=self.superuser)

        # Create some products
        self.product1 = Product.objects.create(
            name="Product 1", barcode="1234543", price=10.0
        )

        self.product2 = Product.objects.create(
            name="Product 2", barcode="34343435", price=20.0
        )

    def test_get_all_product(self):
        # send get request
        response = self.client.get("/inventory/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_create_product(self):
        # send post request
        data = {
            "name": "Product 3",
            "barcode": "234324324",
            "price":15.0
        }
        response = self.client.post('/inventory/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Product 3')


class ProductDetailViewTests(APITestCase):
    def setUp(self):
        # Create a superuser for authentication
        self.superuser = User.objects.create_superuser(
            first_name='admin',
            last_name="super",
            email="admin@example.com",
            password="admin123"
        )
        self.client.force_authenticate(user=self.superuser)

        # Create a Product
        self.product = Product.objects.create(
            name="Product 1", barcode="23435", price=30
        )

    def test_get_product_by_id(self):
        # send get request
        response = self.client.get(f'/inventory/{self.product.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Product 1")

    def test_get_product_by_barcode(self):
        # send get request
        response = self.client.get(f'/inventory/barcode/{self.product.barcode}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Product 1")

    def test_patch_product(self):
        # send patch request
        data = {
            "name":"Patch Product 1"
        }
        response = self.client.patch(f'/inventory/{self.product.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Patch Product 1")


    def test_put_product(self):
        # send put request
        data = {
            "name":"Put Product 1",
            "barcode": "new barcode",
            "price":2.00
        }
        response = self.client.put(f'/inventory/{self.product.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Put Product 1")
        self.assertEqual(response.data['barcode'], "new barcode")
        self.assertEqual(response.data['price'], '2.00')

    def test_delete_product_by_id(self):
        # send delete request
        response = self.client.delete(f"/inventory/{self.product.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Product.objects.filter(id=self.product.id).exists())
