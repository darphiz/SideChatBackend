from rest_framework.routers import SimpleRouter
from .views import (
    ChatRetrieveView,
    GuestChatView, 
    GuestChatUpdate, 
    FetchGuestCoinView,
    GuestChatHistory
    )
from django.urls import path
router = SimpleRouter()

    
urlpatterns = router.urls
urlpatterns += [
    path('guest/chat/', GuestChatView.as_view(), name='guest-chat'),
    path('guest/chat/<str:chat_id>/', GuestChatUpdate.as_view(), name='guest-chat-update'),
    path('guest/coins/<str:guest_id>/', FetchGuestCoinView.as_view(), name='fetch-guest-coins'),
    path('guest/history/<str:guest_id>/', GuestChatHistory.as_view(), name='guest-chat-history'),
    path('guest/chat/<str:chat_id>/history/', ChatRetrieveView.as_view(), name='guest-chat-history')
]