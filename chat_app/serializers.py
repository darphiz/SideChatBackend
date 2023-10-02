from contextlib import suppress
from rest_framework import serializers

from chat_app.models import ChatParameter

class ChatSerializer(serializers.Serializer):
    chat_type = serializers.ChoiceField(choices=['gpt', 'user'])
    message = serializers.CharField()
    gpt_version = serializers.CharField(allow_blank=True, required=False)

class GuestChatSerializer(serializers.Serializer):
    guest_id = serializers.CharField(max_length=255)
    chats = ChatSerializer(many=True)
    api_key = serializers.CharField(
        max_length=255, 
        required=False, 
        allow_blank=True,
        allow_null=True
        )
    
class GuestChatParamResp(serializers.Serializer):
    chat_id = serializers.UUIDField()
    guest_id = serializers.CharField(max_length=255)
    ai_response = serializers.CharField()
    coins = serializers.IntegerField()
    chats = ChatSerializer(many=True)
    
class GuestCoinSerializer(serializers.Serializer):
    guest_id = serializers.CharField(max_length=255)
    coins = serializers.IntegerField()
    
class ChatHistorySerializer(serializers.ModelSerializer):
    query = serializers.SerializerMethodField()
    class Meta:
        model = ChatParameter
        fields = ['id', 'query']
    def truncate(self, text, max_len=100):
        return f'{text[:max_len]}...' if len(text) > max_len else text
    
    def get_query(self, obj:ChatParameter) -> str:
        first_client_message = "Empty Message"
        first_client_message = next(
            (chat['message'] for chat in obj.chats if chat['chat_type'] == 'user'),
            None,
        )
        if not first_client_message:
            # return any first message
            with suppress(Exception):
                first_client_message = obj.chats[0]['message']
            
        return self.truncate(first_client_message, 40)
        