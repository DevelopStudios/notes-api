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
        # Start with the base queryset
        queryset = self.get_queryset()
        if not query:
            return Response({"count":0, "results":[]})
        #Perform case-insensitive search across title, content and tag names
        search_results = queryset.filter(
            Q(title__icontains = query)|
            Q(content__icontains = query)|
            Q(tags__name__icontains = query)
        ).distinct() #Use distinct to avoid duplicate notes if they match multiple tags or fields
        page = self.paginate_queryset(search_results)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(search_results, many=True)
        return Response(serializer.data)

class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticated] #Only authenticated Users

    #Ensure users only see tags asscociated with their notes
    def get_queryset(self):
        return Tag.objects.filter(note__user=self.request.user).distinct().order_by('name')
    
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
                # 1. Generate the Golden Ticket
                token_generator = PasswordResetTokenGenerator()
                token = token_generator.make_token(user)
                
                # 2. Encode the User ID (Security practice)
                uid = urlsafe_base64_encode(force_bytes(user.pk))

                # 3. Create the Link (This points to your ANGULAR app)
                # Example: http://localhost:4200/reset-password/MjQ/af45-3221...
                reset_link = f"http://localhost:4200/reset-password/{uid}/{token}/"

                # 4. Send Email (Prints to console in dev)
                send_mail(
                    'Password Reset Request',
                    f'Click this link to reset your password: {reset_link}',
                    'noreply@notekeeper.com',
                    [email],
                    fail_silently=False,
                )

            # Security Best Practice: Always return 200 OK.
            # Don't tell hackers if the email exists or not.
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
                # 1. Decode the User ID
                user_id = urlsafe_base64_decode(uid).decode()
                user = User.objects.get(pk=user_id)

                # 2. Verify the Token
                token_generator = PasswordResetTokenGenerator()
                if not token_generator.check_token(user, token):
                    return Response({"error": "Invalid or expired token"}, status=400)

                # 3. Set the New Password
                user.set_password(new_password)
                user.save()
                return Response({"message": "Password has been reset successfully."})

            except (TypeError, ValueError, OverflowError, User.DoesNotExist):
                return Response({"error": "Invalid user ID"}, status=400)

        return Response(serializer.errors, status=400)