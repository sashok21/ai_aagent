from django.urls import path
from .views import AssistantPageView, AssistantChatApiView, AssistantClearApiView

app_name = "ai_assistant"

urlpatterns = [
    path("", AssistantPageView.as_view(), name="chat"),
    path("api/chat/", AssistantChatApiView.as_view(), name="api_chat"),
    path("api/clear/", AssistantClearApiView.as_view(), name="api_clear"),
]