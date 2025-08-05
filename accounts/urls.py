from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    MeView, CustomTokenObtainPairView, RegisterView, UserView,
    ChangePasswordView, UserListView, AdminCreateUserView,
    AdminDeleteUserView, UserProfileView, ProfilePictureUploadView, LogoutView, PagePermissionViewSet, ActionPermissionViewSet

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
    path('profile/', UserProfileView.as_view()),                  # 👈 GET + PATCH
    path('profile/upload/', ProfilePictureUploadView.as_view()), # 👈 POST
    path('logout/', LogoutView.as_view(), name='logout'),
    path('', include(router.urls)),
]

