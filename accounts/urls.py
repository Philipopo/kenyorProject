# accounts/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    MeView, CustomTokenObtainPairView, RegisterView, UserView,
    ChangePasswordView, UserListView, AdminCreateUserView,
    AdminDeleteUserView, UserProfileView, ProfilePictureUploadView, LogoutView,
    PagePermissionViewSet, ActionPermissionViewSet, page_allowed, action_allowed,
    ForgotPasswordView, ResetPasswordView
)

router = DefaultRouter()
router.register(r'page-permissions', PagePermissionViewSet, basename='page-permissions')
router.register(r'action-permissions', ActionPermissionViewSet, basename='action-permissions')

urlpatterns = [
    path('me/', MeView.as_view()),
    path('login/', CustomTokenObtainPairView.as_view()),
    path('register/', RegisterView.as_view()),
    path('user/', UserView.as_view()),
    path('change-password/', ChangePasswordView.as_view()),
    path('users/', UserListView.as_view()),
    path('admin/create-user/', AdminCreateUserView.as_view()),
    path('admin/delete-user/<int:id>/', AdminDeleteUserView.as_view()),
    path('profile/', UserProfileView.as_view()),
    path('profile/upload/', ProfilePictureUploadView.as_view()),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
    path('', include(router.urls)),
    path('permissions/page/<str:page_name>/', page_allowed),
    path('permissions/action/<str:action_name>/', action_allowed),
]