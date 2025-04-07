from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from django.shortcuts import get_object_or_404
from .models import Customer
from .filters import CustomerFilter
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

        search_query = request.GET.get('search', "").strip()
        queryset = Customer.objects.all()

        if search_query:
            search_filter = (
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(phone_number__icontains=search_query) |
                Q(address__icontains=search_query) |
                Q(created_by__first_name__icontains=search_query) |
                Q(created_by__last_name__icontains=search_query) |
                Q(updated_by__first_name__icontains=search_query) |
                Q(updated_by__last_name__icontains=search_query) |
                Q(created_at__icontains=search_query) |
                Q(updated_at__icontains=search_query)
            )
            queryset= queryset.filter(search_filter)

        customer_filter = CustomerFilter(request.GET, queryset=queryset)
        filtered_customers = customer_filter.qs

        if not filtered_customers.exists():
            return Response({"error": "No matching customers found"}, status=404)
        serializer = CustomerSerializer(filtered_customers, many=True)
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
                resource_name="Customer",
                resource_id=customer.id,
                details=f"Customer {customer.id} created",
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
        customers = get_object_or_404(Customer, pk=pk)

        serializer = CustomerSerializer(customers)
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
            for field, new_value in serializer.validated_data.items():
                old_value = getattr(customer, field, None)
                if old_value != new_value:
                    changes.append(f"{field}: '{old_value}' -> '{new_value}'")

            details = f"Updated fields: {', '.join(changes)}"

            serializer.save(updated_by=request.user)

            # log in audit
            AuditLog.objects.create(
                action="update",
                performed_by=request.user,
                resource_name="Customer",
                resource_id=customer.id,
                details=details,
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
            for field, new_value in serializer.validated_data.items():
                old_value = getattr(customer, field, None)
                if old_value != new_value:
                    changes.append(f"{field}: '{old_value}' -> '{new_value}'")

            details = f"Updated fields: {', '.join(changes)}"

            serializer.save(updated_by=request.user)

            # log in audit
            AuditLog.objects.create(
                action="update",
                performed_by=request.user,
                resource_name="Customer",
                resouce_id=customer.id,
                details=details,
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
            resource_name="Customer",
            resouce_id=customer.id,
            details=f"Customer {customer.id} created",
        )
        return Response(
            {"message": "Customer deleted successfully"},
            status=status.HTTP_204_NO_CONTENT,
        )


class DeactivateCustomerView(APIView):
    """
    Endpoint to deactivate a customer.
    """
    def post(self, request, pk):
        customer = get_object_or_404(Customer, pk=pk)
        if not customer.is_active:
            return Response({"message":"Customer is already deactivated"}, status=400)
        customer.is_active = False
        customer.updated_by = request.user
        customer.save()

        # Log to audit trail
        AuditLog.objects.create(
            action="deactivate",
            performed_by=request.user,
            resource_name="Customer",
            resource_id=customer.id,
            details=f"Customer {customer.id} deactivated"
        )

        return Response({"message":"Customer deactivated successfully"}, status=200)

class ActivateCustomerView(APIView):
    """
    Endpoint to deactivate a customer.
    """
    def post(self, request, pk):
        customer = get_object_or_404(Customer, pk=pk)
        if customer.is_active:
            return Response({"message":"Customer is already activated"}, status=400)
        customer.is_active = True
        customer.updated_by = request.user
        customer.save()

        # Log to audit trail
        AuditLog.objects.create(
            action="activate",
            performed_by=request.user,
            resource_name="Customer",
            resource_id=customer.id,
            details=f"Customer {customer.id} deactivated"
        )

        return Response({"message":"Customer activated successfully"}, status=200)
