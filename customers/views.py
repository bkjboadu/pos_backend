from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Customer
from .serializers import CustomerSerializer
from audit.models import AuditLog


class CustomerView(APIView):
    """
    Handles creating and listing customers.
    """

    def get(self, request):
        """
        Retrieve a list of all customers.
        """
        customers = Customer.objects.all()
        serializer = CustomerSerializer(customers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """
        Create a new customer.
        """
        serializer = CustomerSerializer(data=request.data)
        if serializer.is_valid():
            customer = serializer.save(created_by=request.user, updated_by=request.user)
            # log in audit
            AuditLog.objects.create(
                action="create",
                performed_by=request.user,
                resource_name = "Customer",
                resource_id=customer.id,
                details = f"Customer {customer.id} created"
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomerDetailView(APIView):
    """
    Handles retrieving, updating, and deleting a single customer.
    """

    def get(self, request, pk):
        """
        Retrieve a single customer by ID.
        """
        customer = get_object_or_404(Customer, pk=pk)
        serializer = CustomerSerializer(customer)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        """
        Update a customer's details.
        """
        customer = get_object_or_404(Customer, pk=pk)
        serializer = CustomerSerializer(customer, data=request.data, partial=True)
        if serializer.is_valid():
            # Log changes for audit
            changes = []
            for (field, new_value) in serializer.validated_data.items():
                old_value = getattr(customer, field, None)
                print('old value', old_value)
                print('new value', new_value)
                if old_value != new_value:
                    print(f"{field}: '{old_value}' -> '{new_value}'")
                    changes.append(f"{field}: '{old_value}' -> '{new_value}'")

            details = f"Updated fields: {', '.join(changes)}"

            serializer.save(updated_by=request.user)

            # log in audit
            AuditLog.objects.create(
                action="update",
                performed_by=request.user,
                resource_name = "Customer",
                resource_id=customer.id,
                details = details
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        """
        Update a customer's details.
        """
        customer = get_object_or_404(Customer, pk=pk)
        serializer = CustomerSerializer(customer, data=request.data)
        if serializer.is_valid():

            # Log changes for audit
            changes = []
            for (field, new_value) in serializer.validated_data.items():
                old_value = getattr(customer, field, None)
                if old_value != new_value:
                    changes.append(f"{field}: '{old_value}' -> '{new_value}'")

            details = f"Updated fields: {', '.join(changes)}"

            serializer.save(updated_by=request.user)

            # log in audit
            AuditLog.objects.create(
                action="update",
                performed_by=request.user,
                resource_name = "Customer",
                resouce_id=customer.id,
                details = details
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """
        Delete a customer by ID.
        """
        customer = get_object_or_404(Customer, pk=pk)
        customer.delete()

        # log in audit
        AuditLog.objects.create(
            action="delete",
            performed_by=request.user,
            resource_name = "Customer",
            resouce_id=customer.id,
            details = f"Customer created"
        )
        return Response(
            {"message": "Customer deleted successfully"},
            status=status.HTTP_204_NO_CONTENT,
        )
