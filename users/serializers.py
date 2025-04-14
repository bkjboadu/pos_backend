import uuid
from rest_framework import serializers
from django.contrib.auth import authenticate

from branches.models import Branch
from .models import CustomUser
from users.helpers.validator import CustomPasswordValidator


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    branch_name = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = [
            'id',
            'email',
            'first_name',
            'last_name',
            'role',
            'branch_name',
            'user_permissions',
            'groups',
            'is_active',
            'is_staff',
            'is_superuser',
            'last_login',
            'date_joined',
            'phone_number',
            'password',
            'confirm_password'
        ]
        read_only_fields = ['branch_name']

    def get_branch_name(self, obj):
        branches_dict = {}
        for branch in obj.branches.all():
            branches_dict[str(branch.id)] = branch.name
        return branches_dict

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["uuid"] = str(instance.id)
        return data

    def validate_password(self, password):
        validator = CustomPasswordValidator()
        validator.validate(password)

        return password

    def match_passwords(self, data):
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError("Passwords do not match")
        return data

    def validate(self, data):
        # Match passwords
        if data.get("password") != data.get("confirm_password"):
            raise serializers.ValidationError("Passwords do not match")

        # Role-based branch logic
        role = data.get("role")
        branches = data.get("branches", [])

        if role == "cashier" and len(branches) != 1:
            raise serializers.ValidationError("Cashier must be assigned exactly one branch.")

        if role == "manager" and len(branches) < 1:
            raise serializers.ValidationError("Manager must be assigned at least one branch.")

        if role == "admin_manager" and branches:
            raise serializers.ValidationError("Admin Manager must not be assigned any branches.")

        return data

    def create(self, validated_data):
        validated_data.pop("confirm_password")
        branches = validated_data.pop('branches', [])
        user = CustomUser.objects.create_user(**validated_data)

        # set branches:
        if branches:
            user.branches.set(branches)

        self.context.get("request").get_host()
        return user


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            "email",
            "first_name",
            "last_name",
            "phone_number",
        ]
        extra_kwargs = {"email": {"required": False}}

    def update(self, instance, validated_data):
        # Update user instance with the validated data
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        return instance


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        # Ensure both email and password are provided
        if not email or not password:
            raise serializers.ValidationError("Must include 'email' and 'password'.")

        # Authenticate the user
        user = authenticate(email=email, password=password)

        if not user:
            raise serializers.ValidationError("Invalid credentials")

        # Ensure user account is active
        if not user.is_active:
            raise serializers.ValidationError("This account is deactivated.")

        # Check that the user's ID is a valid UUID
        if not isinstance(user.id, uuid.UUID):
            raise serializers.ValidationError("Invalid user ID format.")

        # Return the user object
        return {"user": user}


# Password management
class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, data):
        user = CustomUser.objects.filter(email=data).first()
        if not user:
            raise serializers.ValidationError(
                "No account is associated with this email."
            )
        return data


class PasswordResetConfirmSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ("password", "confirm_password")

    confirm_password = serializers.CharField(write_only=True, required=True)

    def validate_password(self, password):
        validator = CustomPasswordValidator()
        validator.validate(password)
        return password

    def validate(self, data):
        password = data["password"]
        """
        Check that the two password fields match
        """
        if password != data["confirm_password"]:
            raise serializers.ValidationError("Passwords do not match")
        return data


class PasswordChangeSerializer(PasswordResetConfirmSerializer):
    current_password = serializers.CharField(write_only=True, required=True)

    class Meta(PasswordResetConfirmSerializer.Meta):
        fields = ("current_password", "password", "confirm_password")

    def password_check(self, data):
        user = self.context["request"].user
        current_password = data["current_password"]
        if not user.check_password(current_password):
            raise serializers.ValidationError(
                "you have entered the wrong password check and try again."
            )


class DeleteAccountSerializer(PasswordResetSerializer):
    def get_user(self, email):
        user = CustomUser.objects.get(email=email)
        return user
