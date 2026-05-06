import json
import logging

from django.http import JsonResponse
from django.views import View
from django.views.generic import TemplateView

from .service import run_agent

logger = logging.getLogger(__name__)

SESSION_KEY = "vgoru_ai_history"
MAX_HISTORY_PAIRS = 10


class AssistantPageView(TemplateView):
    template_name = "ai_assistant/chat.html"

    def get(self, request, *args, **kwargs):
        if "clear" in request.GET:
            request.session.pop(SESSION_KEY, None)
        return super().get(request, *args, **kwargs)


class AssistantChatApiView(View):
    def post(self, request, *args, **kwargs):
        try:
            body = json.loads(request.body)
        except (json.JSONDecodeError, ValueError):
            return JsonResponse({"error": "Невірний формат запиту."}, status=400)

        user_message = (body.get("message") or "").strip()
        if not user_message:
            return JsonResponse({"error": "Порожнє повідомлення."}, status=400)

        if len(user_message) > 1000:
            return JsonResponse({"error": "Повідомлення занадто довге."}, status=400)

        history = request.session.get(SESSION_KEY, [])
        history.append({"role": "user", "content": user_message})

        try:
            reply = run_agent(history)
        except Exception as exc:
            logger.exception("ВГору AI — помилка run_agent: %s", exc)
            history.pop()
            return JsonResponse(
                {"error": f"Помилка сервісу: {exc}"},
                status=500,
            )

        history.append({"role": "assistant", "content": reply})

        if len(history) > MAX_HISTORY_PAIRS * 2:
            history = history[-(MAX_HISTORY_PAIRS * 2):]

        request.session[SESSION_KEY] = history
        request.session.modified = True

        return JsonResponse({"reply": reply})


class AssistantClearApiView(View):
    def post(self, request, *args, **kwargs):
        request.session.pop(SESSION_KEY, None)
        return JsonResponse({"ok": True})