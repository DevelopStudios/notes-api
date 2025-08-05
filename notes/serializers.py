from rest_framework import serializers
from .models import Note, Tag
from django.contrib.auth.models import User #Required for UserSerializer

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email'] #Only expose necessary user fields

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name'] #Fields to be included in the API representation

class NoteSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    tag_names = serializers.ListField(
        child=serializers.CharField(max_length=50),
        write_only=True,
        required=False
    )
    # Display user's username for each note (read-only)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Note
        fields = [
             'id', 'user', 'title', 'content', 'is_archived',
            'created_at', 'updated_at', 'tags', 'tag_names'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at', 'tags'] # Ensure these are not updated directly by frontend

        def create(self, validated_data):
            tag_names = validated_data.pop('tag_names',[])
            #Assign the current user making the request as the note's user
            # self.context['request'].user will be available in the viewset
            note = Note.objects.create(user=self.context['request'].user, **validated_data)
            for tag_name in tag_names:
                tag, created = Tag.objects.get_or_create(name=tag_name.lower()) # Ensure tags are lowercase and unique
                note.tags.add(tag)
            return note

        def update(self, instance, validated_data):
            tag_names = validated_data.pop('tag_names', None)

            #Update core note fields
            instance.title = validated_data.get('title', instance.title)
            instance.content = validated_data.get('content', instance.content)
            instance.is_archived = validated_data.get('is_archived', instance.is_archived)
            instance.save()

            # Handle tag updates if tag_names are provied
            if tag_names is not None:
                instance.tags.clear()
                for tag_name in tag_names:
                    tag, created = Tag.objects.get_or_create(name=tag_name.lower())
                    instance.tags.add(tag)
            return instance

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username','email']