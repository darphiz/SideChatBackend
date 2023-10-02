import uuid
from django.db import models

class GuestUserAccount(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    guest_id = models.CharField(max_length=255, unique=True)
    coins = models.IntegerField(default=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.guest_id
    
class ChatParameter(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Inputs
    chats = models.JSONField(
        default=list,)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        'auth.User', 
        related_name='chats', 
        on_delete=models.CASCADE,
        null=True,
        blank=True
        )
    
    guest_user = models.ForeignKey(
        GuestUserAccount, 
        related_name='chats', 
        on_delete=models.CASCADE,
        null=True,
        blank=True   
        )
    
    # Outputs
    ai_predicted_response = models.TextField(blank=True, null=True)
    