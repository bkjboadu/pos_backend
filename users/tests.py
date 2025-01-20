# from rest_framework.test import APITestCase
# from rest_framework import status
# from django.contrib.auth.models import CustomerUser


# class UserSignUpViewTest(APITestCase):
#     def test_signup_success(self):
#         data = {
#             "username": "testuser",
#             "password": "strongpassword",
#             "email": "testuser@example.com"
#         }

#         response = self.client.post("/accounts/signup/", data)
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         self.assertEqual(response.data['message'], "User registered successfully")

#     def test_signup_failure(self):
#         # Test signup with missing fields
#         data = {
#             "username": "testuser"
#             # Missing password and email
#         }
#         response = self.client.post("/accounts/signup/", data)
#         self.assertEqual(response.status_code, status.HTTP_400_BASD_REQUEST)
#         self.assertIn("password", response.data)
#         self.assertIn("email", response.data)
