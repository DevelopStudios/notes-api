from rest_framework import serializers
from .models import Note, Tag
from django.contrib.auth.models import User 

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email'] 

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']

class NoteSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    tag_names = serializers.ListField(
        child=serializers.CharField(max_length=50),
        write_only=True,
        required=False
    )

    user = UserSerializer(read_only=True)

    class Meta:
        model = Note
        fields = [
             'id', 'user', 'title', 'content', 'is_archived',
            'created_at', 'updated_at', 'tags', 'tag_names'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at', 'tags']

    def create(self, validated_data):
        tag_names = validated_data.pop('tag_names', [])
        user = validated_data.pop('user')
        note = Note.objects.create(user=user, **validated_data)
        for tag_name in tag_names:
            tag, created = Tag.objects.get_or_create(name=tag_name)
            note.tags.add(tag)
        return note

    def update(self, instance, validated_data):
        tag_names = validated_data.pop('tag_names', None)
        validated_data.pop('user',None)
        instance.title = validated_data.get('title', instance.title)
        instance.content = validated_data.get('content', instance.content)
        instance.is_archived = validated_data.get('is_archived', instance.is_archived)
        instance.save()

        if tag_names is not None:
            instance.tags.clear()
            for tag_name in tag_names:
                tag, created = Tag.objects.get_or_create(name=tag_name.lower())
                instance.tags.add(tag)
        return instance

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username','email','password']
    
    def create(self, validate_data):
        user = User.objects.create_user(
            username=validate_data['username'],
            email = validate_data.get('email', ''),
            password = validate_data['password']
        )
        return user

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

class PasswordResetConfirmSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True)
    uid = serializers.CharField()
    token = serializers.CharField()