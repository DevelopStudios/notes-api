from django.db import models
from django.contrib.auth.models import User

class Tag(models.Model):
    """
        Represents a tag that can be associated with notes.
    """
    name = models.CharField(max_length=50, unique=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
class Note(models.Model):
    """
        Represents a user's note.
    """
    #Link User to User Model.
    #Each note belongs to one user.
    user = models.ForeignKey(User,on_delete=models.CASCADE, related_name='notes')

    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)

    # Many to Many relation with Tag.
    # A note can have many tags and a tag can be applied to many notes.
    tags = models.ManyToManyField(Tag, blank=True)
    is_archived = models.BooleanField(default=False)

    #Timestamps for creation and last update
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at'] # Order notes by most recent first
    
    def __str__(self):
        return self.title