from django.conf import settings
from langchain.chat_models import ChatOpenAI
from langchain.schema import (
    AIMessage,
    HumanMessage
)


class AIChatUtils:
    @staticmethod
    def generate_reply(chats:list, gpt_version="4.0", api_key=None) -> str:
        try:
            openai_api_key = api_key or settings.OPENAI_API_KEY 
            req_messages = []
            for chat in chats:
                if chat['chat_type'] == 'user':
                    req_messages.append(HumanMessage(content = chat['message']))
                elif chat['chat_type'] == 'gpt':
                    req_messages.append(AIMessage(content = chat['message']))
                    
            ai = ChatOpenAI(openai_api_key=openai_api_key)
            resp = ai(req_messages)
            return str(resp.content)
        except Exception as e:
            return str(e)