# accounts/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import UserProfile, PagePermission, ActionPermission

User = get_user_model()

class PagePermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PagePermission
        fields = ['id', 'page_name', 'min_role']

class ActionPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActionPermission
        fields = ['id', 'action_name', 'min_role']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ['email', 'name', 'password', 'role']
    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['full_name', 'profile_image']

class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)
    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'role', 'profile']

class UserListSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ['id', 'full_name', 'email', 'role', 'status']
    def get_full_name(self, obj):
        return obj.name
    def get_status(self, obj):
        return "Active" if obj.is_active else "Inactive"

class ProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)
    name = serializers.CharField(source='user.name', read_only=True)
    role = serializers.CharField(source='user.role', read_only=True)
    full_name = serializers.SerializerMethodField()
    class Meta:
        model = UserProfile
        fields = ['email', 'name', 'full_name', 'profile_image', 'role']
    def get_full_name(self, obj):
        return obj.full_name or obj.user.name or obj.user.email.split('@')[0]

class ProfilePictureUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['profile_image']

# Add these serializers if not present
class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

class ResetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(min_length=6, write_only=True)
    token = serializers.CharField()
    uid = serializers.CharField()