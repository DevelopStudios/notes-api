from rest_framework import viewsets,permissions, filters, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Note, Tag
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import NoteSerializer, TagSerializer, UserSerializer, UserRegisterSerializer, PasswordResetRequestSerializer, PasswordResetConfirmSerializer
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_decode


class NoteViewSet(viewsets.ModelViewSet):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        queryset = Note.objects.filter(user=self.request.user).order_by('-updated_at')
        if self.action == 'archived':
            return queryset.filter(is_archived=True)
        
        if self.action == 'list':
            queryset = queryset.filter(is_archived=False)
        
        tag_id = self.request.query_params.get('tag_id')
        if(tag_id):
            queryset = queryset.filter(tags__id=tag_id).distinct()
        return queryset
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
        queryset = self.get_queryset()
        if not query:
            return Response({"count":0, "results":[]})
        search_results = queryset.filter(
            Q(title__icontains = query)|
            Q(content__icontains = query)|
            Q(tags__name__icontains = query)
        ).distinct()
        page = self.paginate_queryset(search_results)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(search_results, many=True)
        return Response(serializer.data)

class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticated] 
    def get_queryset(self):
        return Tag.objects.filter(
            note__user=self.request.user,
            note__is_archived=False
        ).distinct().order_by('name')

class UserDetailsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]

class PasswordResetRequestView(generics.GenericAPIView):
    serializer_class = PasswordResetRequestSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.filter(email=email).first()
            print(User.objects.values())
            if user:
                token_generator = PasswordResetTokenGenerator()
                token = token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                reset_link = f"http://localhost:4200/auth/reset-password/{uid}/{token}/"

                send_mail(
                    'Password Reset Request',
                    f'Click this link to reset your password: {reset_link}',
                    'noreply@notekeeper.com',
                    [email],
                    fail_silently=False,
                )

            return Response({"message": "If your email exists, a link has been sent."})
        
        return Response(serializer.errors, status=400)
    

class PasswordResetConfirmView(generics.GenericAPIView):
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            uid = serializer.validated_data['uid']
            token = serializer.validated_data['token']
            new_password = serializer.validated_data['new_password']

            try:
                user_id = urlsafe_base64_decode(uid).decode()
                user = User.objects.get(pk=user_id)

                token_generator = PasswordResetTokenGenerator()
                if not token_generator.check_token(user, token):
                    return Response({"error": "Invalid or expired token"}, status=400)
                user.set_password(new_password)
                user.save()
                return Response({"message": "Password has been reset successfully."})

            except (TypeError, ValueError, OverflowError, User.DoesNotExist):
                return Response({"error": "Invalid user ID"}, status=400)

        return Response(serializer.errors, status=400)