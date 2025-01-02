from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Company, Branch
from .serializers import CompanySerializer, BranchSerializer
from users.permissions import (
    IsSuperUser,
    IsSuperUserOrCompanyAdmin,
    IsSuperUserOrCompanyAdminOrBranchManager,
)


class CompanyView(APIView):
    permission_classes = [IsSuperUser]

    def get(self, request):
        """get all companies"""
        companies = Company.objects.all()
        serializer = CompanySerializer(companies, many=True)
        return Response(serializer.data)

    def post(self, request):
        """
        create company instance
        """
        serializer = CompanySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)

        return Response(serializer.errors, status=400)


class CompanyDetailView(APIView):
    permission_class = [IsSuperUserOrCompanyAdmin]

    def get(self, request, pk):
        """
        Get details of a specific company by ID
        """
        if not request.user.is_superuser:
            if request.user.company.id != pk:
                return Response(
                    {"error": "Access denied. You can only access you company"},
                    status=403,
                )

        try:
            company = Company.objects.get(pk=pk)
        except Company.DoesNotExist:
            return Response({"error": "Company nof found"}, status=404)

        serializer = CompanySerializer(company)
        return Response(serializer.data)

    def delete(self, request, pk):
        """
        Delete specific company by ID
        """
        if not request.user.is_superuser:
            if request.user.company.id != pk:
                return Response(
                    {"error": "Access denied. You can only access you company"},
                    status=403,
                )

        try:
            company = Company.objects.get(pk=pk)
        except Company.DoesNotExist:
            return Response({"error": "Company not found"}, status=404)
        company.delete()
        return Response({"message": "Company deleted successfully"}, status=204)

    def patch(self, request, pk):
        """
        Partial Update company details
        """
        if not request.user.is_superuser:
            if request.user.company.id != pk:
                return Response(
                    {"error": "Access denied. You can only access you company"},
                    status=403,
                )

        try:
            company = Company.objects.get(pk=pk)
        except Company.DoesNotExist:
            return Response({"error": "Company not found"}, status=404)
        serializer = CompanySerializer(company, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)

        return Response(serializer.errors, status=400)

    def put(self, request, pk):
        """
        Update company details
        """

        if not request.user.is_superuser:
            if request.user.company.id != pk:
                return Response(
                    {"error": "Access denied. You can only access you company"},
                    status=403,
                )

        try:
            company = Company.objects.get(pk=pk)
        except Company.DoesNotExist:
            return Response({"error": "Company not found"}, status=404)
        serializer = CompanySerializer(company, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)

        return Response(serializer.errors, status=400)


class BranchView(APIView):
    permission_classes = [IsSuperUserOrCompanyAdmin]

    def get(self, request):
        company_id = request.query_params.get("company")
        if not company_id:
            return Response({"error": "Company ID is required"}, status=400)

        if not request.user.is_superuser:
            if str(request.user.company.id) != company_id:
                return Response(
                    {
                        "error": "Access denied. You can only access you company's branches"
                    },
                    status=403,
                )

        branches = Branch.objects.filter(company__id=company_id)
        serializer = BranchSerializer(branches, many=True)
        return Response(serializer.data)

    def post(self, request):
        company_id = request.data.get("company")
        if not company_id:
            return Response({"error": "Company ID is required"}, status=400)

        if not request.user.is_superuser:
            if str(request.user.company.id) != company_id:
                return Response(
                    {
                        "error": "Access denied. You can only access you company's branches"
                    },
                    status=403,
                )

        try:
            company = Company.objects.get(pk=company_id)
        except Company.DoesNotExist:
            return Response({"error": "Company Does not exist"}, status=400)

        serializer = BranchSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(company=company)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=404)


class BranchDetailView(APIView):
    permission_classes = [IsSuperUserOrCompanyAdminOrBranchManager]

    def get(self, request, pk):
        """
        Get details of specific branch by id
        """

        try:
            branch = Branch.objects.get(pk=pk)
        except Branch.DoesNotExist:
            return Response({"error": "Branch not found"}, status=404)

        if not request.user.is_superuser:
            if request.user.role == "company_admin":
                if request.user.company.id != branch.company.id:
                    return Response(
                        {
                            "error": "Access denied. You can only access you company's branches"
                        },
                        status=403,
                    )
            elif request.user.branch.id != pk:
                return Response(
                    {
                        "error": "Access denied. You can only access you company's branches"
                    },
                    status=403,
                )

        serializer = BranchSerializer(branch)
        return Response(serializer.data)

    def delete(self, request, pk):
        """
        Delete specific branch by id
        """
        try:
            branch = Branch.objects.get(pk=pk)
        except Branch.DoesNotExist:
            return Response({"error": "Branch not found"}, status=404)

        if not request.user.is_superuser:
            if request.user.role == "company_admin":
                if request.user.company.id != branch.company.id:
                    return Response(
                        {
                            "error": "Access denied. You can only access you company's branches"
                        },
                        status=403,
                    )
            elif request.user.branch.id != pk:
                return Response(
                    {
                        "error": "Access denied. You can only access you company's branches"
                    },
                    status=403,
                )

        branch.delete()
        return Response({"message": "Branch deleted successfully"}, status=204)

    def patch(self, request, pk):
        """
        Partial Update specific branch by id
        """
        try:
            branch = Branch.objects.get(pk=pk)
        except Branch.DoesNotExist:
            return Response({"error": "Branch not found"}, status=404)

        if not request.user.is_superuser:
            if request.user.role == "company_admin":
                if request.user.company.id != branch.company.id:
                    return Response(
                        {
                            "error": "Access denied. You can only access you company's branches"
                        },
                        status=403,
                    )
            elif request.user.branch.id != pk:
                return Response(
                    {
                        "error": "Access denied. You can only access you company's branches"
                    },
                    status=403,
                )

        serializer = BranchSerializer(branch, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)

        return Response(serializer.errors, status=404)

    def put(self, request, pk):
        """
        Update specific branch by id
        """
        try:
            branch = Branch.objects.get(pk=pk)
        except Branch.DoesNotExist:
            return Response({"error": "Branch not found"}, status=404)

        if not request.user.is_superuser:
            if request.user.role == "company_admin":
                if request.user.company.id != branch.company.id:
                    return Response(
                        {
                            "error": "Access denied. You can only access you company's branches"
                        },
                        status=403,
                    )
            elif request.user.branch.id != pk:
                return Response(
                    {
                        "error": "Access denied. You can only access you company's branches"
                    },
                    status=403,
                )

        serializer = BranchSerializer(branch, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)

        return Response(serializer.errors, status=404)
