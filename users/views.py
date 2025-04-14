import logging
from .models import CustomUser
from .filters import CustomUserFilter
from .serializers import UserSerializer, UserProfileUpdateSerializer, LoginSerializer
from .serializers import DeleteAccountSerializer, PasswordChangeSerializer
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


logging.basicConfig(level=logging.INFO)


class UserSignupView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "User registered successfully!"},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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


class UserLoginView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)
        user_data = UserSerializer(user).data

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
            },
            status=status.HTTP_200_OK,
        )

@method_decorator(csrf_exempt, name='dispatch')
class AdminUserUpdateView(generics.UpdateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserProfileUpdateSerializer
    permission_classes = [IsSuperUserOrManager]
    authentication_classes = (JWTAuthentication,)
    lookup_field = "pk"

class UserProfileUpdateView(generics.UpdateAPIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileUpdateSerializer

    def get_object(self):
        return self.request.user

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

class UserLists(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAdminUser,)

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
                Q(branch__name__icontains=search_query) |
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


class DeleteAccount(generics.GenericAPIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = [IsAdminUser]
    serializer_class = DeleteAccountSerializer

    def delete(self, request, pk):
        user = CustomUser.objects.get(id=pk)
        user.is_active = False
        user.delete()
        return Response({"detail: user deleted"})


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
