from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import UserProfile

User = get_user_model()

# For user registration
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'name', 'password', 'role']

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

# User Profile Serializer
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['full_name', 'profile_image']

# Full User Serializer with nested profile
class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'role', 'profile']

# For frontend user list
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

# For /auth/profile/ GET and PATCH
class ProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)
    name = serializers.CharField(source='user.name', read_only=True)  # Add User.name
    role = serializers.CharField(source='user.role', read_only=True)  # Add User.role
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ['email', 'name', 'full_name', 'profile_image', 'role']

    def get_full_name(self, obj):
        # Return UserProfile.full_name if set, else User.name, else email username
        return obj.full_name or obj.user.name or obj.user.email.split('@')[0]

# For uploading just profile image
class ProfilePictureUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['profile_image']
