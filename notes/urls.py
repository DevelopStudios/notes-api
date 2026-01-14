# notes/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ChangePasswordView, NoteViewSet, PasswordResetConfirmView, PasswordResetRequestView, TagViewSet, UserDetailsView,UserRegistrationView

# Create a router instance
router = DefaultRouter()

# Register your ViewSets with the router
router.register(r'notes', NoteViewSet)
router.register(r'tags', TagViewSet)

# Define the urlpatterns for the 'notes' app
urlpatterns = [
    path('', include(router.urls)),
    path('user-details/',UserDetailsView.as_view(), name='user-details'),
    path('users/register/', UserRegistrationView.as_view(), name='register'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password-reset-request'),
    path('password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    path('auth/change-password/', ChangePasswordView.as_view(), name='change-password'),
]