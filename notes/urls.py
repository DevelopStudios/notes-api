# notes/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NoteViewSet, TagViewSet, UserDetailsView

# Create a router instance
router = DefaultRouter()

# Register your ViewSets with the router
router.register(r'notes', NoteViewSet)
router.register(r'tags', TagViewSet)

# Define the urlpatterns for the 'notes' app
urlpatterns = [
    path('', include(router.urls)),
    path('user-details/',UserDetailsView.as_view(), name='user-details')
]