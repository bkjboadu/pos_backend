import pkgutil
import logging

from django.shortcuts import get_object_or_404
from .models import CustomUser
from .filters import CustomUserFilter
from .serializers import (
    UserSerializer,
    UserProfileUpdateSerializer,
    LoginSerializer,
    DeleteAccountSerializer,
    PasswordChangeSerializer,
    AdminUserUpdateSerializer
)
from core.permissions import IsSuperUserOrManager
from audit.models import AuditLog
from rest_framework.views import APIView
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.views import TokenRefreshView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser

# RBAC imports
from rbac.services import RBACService
from rbac.serializers import ModuleSerializer
from rbac.models import UserRole, Role


logging.basicConfig(level=logging.INFO)

# signup view
class UserSignupView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Assign default role based on user's role field
            self.assign_default_role(user)
            
            return Response(
                {"message": "User registered successfully!"},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def assign_default_role(self, user):
        """Assign default RBAC role based on user's role field"""
        try:
            role = Role.objects.get(code=user.role)
            RBACService.assign_role_to_user(user, role)
        except Role.DoesNotExist:
            # If role doesn't exist, assign cashier as default
            try:
                default_role = Role.objects.get(code='cashier')
                RBACService.assign_role_to_user(user, default_role)
            except Role.DoesNotExist:
                pass

# login view
class UserLoginView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)
        user_data = UserSerializer(user).data

        # Get user's accessible modules and actions
        modules = RBACService.get_user_modules_and_actions(user)
        modules_data = ModuleSerializer(modules, many=True, context={'user': user}).data
        
        # Get user's roles
        user_roles = Role.objects.filter(user_roles__user=user, is_active=True)
        
        # log in audit
        AuditLog.objects.create(
            action="login",
            performed_by=request.user if request.user.is_authenticated else None,
            resource_name="CustomUser Login",
            resource_id=None,
            details=f"{user_data.get('email')} logged in ",
        )
        
        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": user_data,
                "access_control": {
                    "modules": modules_data,
                    "roles": [role.name for role in user_roles],
                    "permissions": [perm.code for perm in RBACService.get_user_permissions(user)]
                }
            },
            status=status.HTTP_200_OK,
        )

# User profile update
class UserProfileUpdateView(generics.UpdateAPIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileUpdateSerializer

    def get_object(self):
        return self.request.user

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

# user list view
class UserListView(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsSuperUserOrManager,)

    def get(self, request):
        search_query = request.GET.get('search',"")
        print('search_query:', search_query)
        queryset = CustomUser.objects.all()

        if search_query:
            filtered_users = queryset.filter(
                Q(email__icontains=search_query) |
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(phone_number__icontains=search_query) |
                Q(branches__name__icontains=search_query) |
                Q(role__icontains=search_query)
            )
            queryset = queryset.filter(filtered_users)

        filterset = CustomUserFilter(request.GET, queryset=queryset)
        if filterset.is_valid():
            filtered_users = filterset.qs
        else:
            return Response(filterset.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer = UserSerializer(filtered_users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# password change view
class PasswordChange(generics.GenericAPIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = PasswordChangeSerializer

    def put(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        current_password = serializer.validated_data["current_password"]
        user = self.request.user

        if not user.check_password(current_password):
            raise NotFound("You have entered the wrong password, try again.")

        password = serializer.validated_data["password"]
        user.set_password(password)
        user.save()

        # log in audit
        AuditLog.objects.create(
            action="login",
            performed_by=request.user if request.user.is_authenticated else None,
            resource_name="CustomUser Login",
            resource_id=None,
            details=f"{user.email} changed password",
        )
        return Response(
            {"detail": "Password has been changed."}, status=status.HTTP_200_OK
        )

# logout view
class LogoutView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        refresh_token = request.data.get("refresh_token")
        if not refresh_token:
            return Response(
                {"error": "Refresh token is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError:
            return Response(
                {"error": "Invalid or expired token."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        except Exception as e:
            return Response(
                {"error": f"{e}: Failed to logout user."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # log in audit
        AuditLog.objects.create(
            action="login",
            performed_by=request.user if request.user.is_authenticated else None,
            resource_name="CustomUser",
            resource_id=None,
            details="customer user logged out",
        )

        return Response(
            {"message": "User has been logged out successfully."},
            status=status.HTTP_200_OK,
        )

# delete accout view
class DeleteAccount(generics.GenericAPIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = [IsAdminUser]
    serializer_class = DeleteAccountSerializer

    def delete(self, request, pk):
        user = CustomUser.objects.get(id=pk)
        user.is_active = False
        user.delete()
        return Response({"detail: user deleted"})

# refreshtoken view
class CustomTokenRefreshView(TokenRefreshView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code == status.HTTP_200_OK:
            return Response(
                {
                    "access": response.data.get("access"),
                    "refresh": response.data.get("refresh"),
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(response.data, status=response.status_code)


class AdminUserUpdateView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsSuperUserOrManager]

    def put(self, request, pk):
        try:
            user = CustomUser.objects.get(id=pk)
        except CustomUser.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        self.check_object_permissions(request, user)  # manually call permission check for object

        serializer = AdminUserUpdateSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        try:
            user = CustomUser.objects.get(id=pk)
        except CustomUser.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        self.check_object_permissions(request, user)

        serializer = AdminUserUpdateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
