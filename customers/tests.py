from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from rest_framework import status
from .models import Customer

User = get_user_model()


class CustomerViewTest(APITestCase):
    def setUp(self):
        # Create a superuser for authentication
        self.superuser = User.objects.create_superuser(
            first_name="admin",
            last_name="super",
            email="admin@example.com",
            password="admin123",
        )
        self.client.force_authenticate(user=self.superuser)

        # Create some Customer
        self.customer1 = Customer.objects.create(
            first_name="bright",
            last_name="bright",
            email="brbojr@gmail.com",
            phone_number="18243546876",
        )

        self.customer2 = Customer.objects.create(
            first_name="kwadwo",
            last_name="junior",
            email="kwadwojunior@gmail.com",
            phone_number="1417898090",
        )

    def test_get_all_customer(self):
        # send a GET request
        response = self.client.get("/customers/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_create_customer(self):
        # send a POST request
        data = {
            "first_name": "customer",
            "last_name": "test",
            "email": "customer.test@gmail.com",
            "phone_number": "1790898989",
        }
        response = self.client.post("/customers/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["first_name"], "customer")
        self.assertEqual(response.data["last_name"], "test")
        self.assertEqual(response.data["email"], "customer.test@gmail.com")


class CustomerDetailViewTest(APITestCase):
    def setUp(self):
        # Create a superuser for authentication
        self.superuser = User.objects.create_superuser(
            first_name="admin",
            last_name="super",
            email="admin@example.com",
            password="admin123",
        )
        self.client.force_authenticate(user=self.superuser)

        # Create some Customer
        self.customer1 = Customer.objects.create(
            first_name="bright",
            last_name="boadu",
            email="brbojr@gmail.com",
            phone_number="18243546876",
        )

        self.customer2 = Customer.objects.create(
            first_name="kwadwo",
            last_name="junior",
            email="kwadwojunior@gmail.com",
            phone_number="1417898090",
        )

    def test_get_customer_by_id(self):
        # send GET request
        response = self.client.get(f"/customers/{self.customer1.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["first_name"], "bright")
        self.assertEqual(response.data["last_name"], "boadu")

    def test_put_customer(self):
        # send PUT request
        data = {
            "first_name": "monika",
            "last_name": "Pearson",
            "email": "monika.pearson@gmail.com",
            "phone_number": "6767778679",
        }
        response = self.client.put(f"/customers/{self.customer1.id}/", data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["first_name"], "monika")
        self.assertEqual(response.data["last_name"], "Pearson")

    def test_patch_customer(self):
        # send PATCH request
        data = {"email": "monika.pearson.put@gmail.com"}
        response = self.client.patch(f"/customers/{self.customer1.id}/", data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["email"], "monika.pearson.put@gmail.com")

    def test_delete_customer(self):
        # send DELETE request
        response = self.client.delete(f"/customers/{self.customer1.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Customer.objects.filter(id=self.customer1.id).exists())
