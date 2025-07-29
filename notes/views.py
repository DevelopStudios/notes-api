from rest_framework import viewsets,permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Note, Tag
from .serializers import NoteSerializer,TagSerializer
from django.db.models import Q

class NoteViewSet(viewsets.ModelViewSet):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    permission_classes = [permissions.IsAuthenticated] #Only authenticated users can access

    #Ensure users only see and manage their own notes
    def get_queryset(self):
        return Note.objects.filter(user=self.request.user).order_by('-updated_at')
    #Override perform_create to automatically set the user for a new note
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def archived(self, request):
        """
        List all archived notes for authenticated user.
        """
        queryset = self.get_queryset().filter(is_archived=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def search(self, request):
        """
        Search notes by title, content or tag name for the authenticated user.
        Requires a 'q' query parameter
        """
        query = request.query_params.get('q','')
        if not query:
            return Response({"detail":"Please provide a 'q' query parameter for search"})
        # Filter notes belonging to the current user
        queryset = self.get_queryset()
        #Perform case-insensitive search across title, content and tag names
        search_results = queryset.filter(
            Q(title__icontains = query)|
            Q(content__icontains = query)|
            Q(tags__name__icontains = query)
        ).distinct() #Use distinct to avoid duplicate notes if they match multiple tags or fields
        serializer = self.get_serializer(search_results, many=True)
        return Response(serializer.data)

class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticated] #Only authenticated Users

    #Ensure users only see tags asscociated with their notes
    def get_queryset(self):
        return Tag.objects.filter(note__user=self.request.user).distinct().order_by('name')