from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from rest_framework.pagination import PageNumberPagination
from chat_app.ai_utils import AIChatUtils
from chat_app.models import ChatParameter, GuestUserAccount

from chat_app.serializers import ChatHistorySerializer, GuestChatParamResp, GuestChatSerializer, GuestCoinSerializer

class ChatUtils:
    @staticmethod
    def get_last_gpt_version(chats):
        last_gpt_version = 3.5
        for chat in chats:
            if chat['chat_type'] == 'user':
                last_gpt_version = chat['gpt_version']
        return last_gpt_version


@extend_schema(
    description="ask questions as a guest",
    responses={
        200: GuestChatParamResp
    },
    tags=['Guest Chats']
)
class GuestChatView(APIView):
    serializer_class = GuestChatSerializer
    def post(self, request: Request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        guid = serializer.validated_data['guest_id']
        chats = serializer.validated_data['chats']
        api_key = serializer.validated_data.get('api_key', None)
        # get or create guest
        guest_account,_ = GuestUserAccount.objects.get_or_create(guest_id=guid)
        # save chat
        chat_manager = ChatParameter.objects.create(
            guest_user=guest_account,
            chats=chats
        )

        # check guest coins
        if not api_key and guest_account.coins <= 0:
            return Response({"error": "Insufficient coins"}, status=403)

        # run ai
        ai_response = AIChatUtils.generate_reply(chats, api_key=api_key)
        ai_resp_dict = {
            "chat_type": "gpt",
            "message": ai_response,
            "gpt_version": ChatUtils.get_last_gpt_version(chats)
        }
        
        new_chats = chats + [ai_resp_dict]
        
        # return response
        chat_manager.ai_predicted_response = ai_response
        chat_manager.chats = new_chats
        chat_manager.save()
        
        # deduct coins
        if not api_key:
            guest_account.coins -= 1
            guest_account.save()
            
        
        resp = {
            "guest_id": guid,
            "ai_response": ai_response,
            "chats": chat_manager.chats,
            "coins": guest_account.coins,
            "chat_id": chat_manager.id
        }
        return Response(resp, status=200)
    
@extend_schema(
    description="update questions as a guest",
    responses={
        200: GuestChatParamResp
    },
    tags=['Guest Chats']
)
class GuestChatUpdate(APIView):
    serializer_class = GuestChatSerializer

    def put(self, request: Request, chat_id):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        guid = serializer.validated_data['guest_id']
        chats = serializer.validated_data['chats']
        api_key = serializer.validated_data.get('api_key', None)
        
        
        try:
            chat_manager = ChatParameter.objects.get(id=chat_id)
        except ChatParameter.DoesNotExist:
            return Response({"error": "Invalid chat"}, status=404)
        
        if chat_manager.guest_user.guest_id != guid:
            return Response({"error": "Invalid guest"}, status=403)
        
        # check guest coins
        if not api_key and chat_manager.guest_user.coins <= 0:
            return Response({"error": "Insufficient coins"}, status=403)
        
        # run ai
        ai_response = AIChatUtils.generate_reply(chats, api_key=api_key)
        
        ai_resp_dict = {
            "chat_type": "gpt",
            "message": ai_response,
            "gpt_version": ChatUtils.get_last_gpt_version(chats)
        }
        new_chats = chats + [ai_resp_dict]
        # save chat
        chat_manager.chats = new_chats
        chat_manager.ai_predicted_response = ai_response
        chat_manager.save()
        
        #deduct coins
        if not api_key:
            chat_manager.guest_user.coins -= 1
            chat_manager.guest_user.save()
        
        # return response
        resp = {
            "guest_id": guid,
            "ai_response": ai_response,
            "chats": chat_manager.chats,
            "coins": chat_manager.guest_user.coins,
            "chat_id": chat_manager.id
        }

        return Response(resp, status=200)
@extend_schema(
    description="fetch guest coins",
    responses={
        200: GuestCoinSerializer
    },
    request=None,
    tags=['Guest Chats']
)
class FetchGuestCoinView(APIView):
    def get(self, request: Request, guest_id):
        try:
            guest_account, _ = GuestUserAccount.objects.get_or_create(guest_id=guest_id)
        except Exception as e:
            return Response({"error": "Invalid guest"}, status=404)
        
        resp = {
            "guest_id": guest_id,
            "coins": guest_account.coins
        }
        return Response(resp, status=200)
    
@extend_schema(
    description="fetch guest chat history",
    responses={
        200: ChatHistorySerializer(many=True)
    },
    request=None,
    tags=['Guest Chats']
)
class GuestChatHistory(APIView):
    def get(self, request: Request, guest_id):
        paginator = PageNumberPagination()
        try:
            guest_account, _ = GuestUserAccount.objects.get_or_create(guest_id=guest_id)
        except Exception as e:
            return Response({"error": "Invalid guest"}, status=404)

        chat_history = ChatParameter.objects.filter(guest_user=guest_account).order_by('-created_at')

        # paginate response
        paginated_chat_history = paginator.paginate_queryset(chat_history, request)
        resp_serializer = ChatHistorySerializer(paginated_chat_history, many=True)
        return paginator.get_paginated_response(resp_serializer.data)

@extend_schema(
    description="fetch guest chat history detail",
    responses={
        200: ChatHistorySerializer
    },
    request=None,
    tags=['Guest Chats']
)
class ChatRetrieveView(APIView):
    def get(self, request: Request, chat_id):
        try:
            chat_manager = ChatParameter.objects.get(id=chat_id)
        except ChatParameter.DoesNotExist:
            return Response({"error": "Invalid chat"}, status=404)
        
        resp = {
            "guest_id": chat_manager.guest_user.guest_id,
            "ai_response": chat_manager.ai_predicted_response,
            "chats": chat_manager.chats,
            "coins": chat_manager.guest_user.coins,
            "chat_id": chat_manager.id
        }
        return Response(resp, status=200)