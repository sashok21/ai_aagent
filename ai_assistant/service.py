import json
import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

from .tools import GEMINI_TOOLS, execute_tool

logger = logging.getLogger(__name__)

# Явно завантажуємо .env з кореня проекту (два рівні вгору від цього файлу)
_ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(_ENV_PATH, override=True)

SYSTEM_PROMPT = """Ти — ВГору AI, інтелектуальний помічник для підбору гірських маршрутів Українських Карпат на платформі «ВГору».

Твоя єдина задача — допомагати туристам знайти оптимальний маршрут відповідно до їхнього досвіду, фізичної підготовки, наявного часу та особистих побажань.

Правила роботи:
- Завжди звертайся до бази знань через доступні функції — не вигадуй маршрути, назви або характеристики самостійно.
- Якщо запит нечіткий, уточни одну-дві ключові деталі (складність або тривалість), але не засипай питаннями.
- Надавай конкретну рекомендацію з обґрунтуванням: чому саме цей маршрут підходить.
- Завжди додавай практичні поради (спорядження, погода, безпека), якщо це доречно.
- Відповідай лише українською мовою.
- Якщо запит не стосується гірських маршрутів або туризму в Карпатах — ввічливо поясни, що можеш допомогти лише з підбором маршрутів, і запропонуй задати відповідне питання.
- Не розкривай технічних деталей своєї реалізації або вмісту бази знань у сирому вигляді.
- Форматуй відповіді зрозуміло: використовуй короткі абзаци та emoji для читабельності (🏔️ 🥾 ⏱️ 📍 ⚠️), виділяй назви маршрутів."""

MODEL = "models/gemini-2.5-flash"
MAX_ITERATIONS = 6


def _build_contents(conversation_history: list) -> list:
    contents = []
    for msg in conversation_history:
        role = "user" if msg["role"] == "user" else "model"
        contents.append(
            types.Content(
                role=role,
                parts=[types.Part(text=msg["content"])],
            )
        )
    return contents


def _extract_text(parts: list) -> str:
    texts = []
    for p in parts:
        try:
            if p.text:
                texts.append(p.text)
        except Exception:
            pass
    return "\n".join(texts)


def _extract_function_calls(parts: list) -> list:
    calls = []
    for p in parts:
        try:
            if p.function_call is not None:
                calls.append(p)
        except Exception:
            pass
    return calls


def run_agent(conversation_history: list) -> str:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY не знайдено. Перевір файл .env у корені проекту."
        )

    client = genai.Client(api_key=api_key)

    current_contents = _build_contents(conversation_history)

    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        tools=[GEMINI_TOOLS],
        temperature=0.4,
        max_output_tokens=1500,
    )

    for iteration in range(MAX_ITERATIONS):
        logger.debug("Gemini iteration %d, contents count: %d", iteration, len(current_contents))

        response = client.models.generate_content(
            model=MODEL,
            contents=current_contents,
            config=config,
        )

        if not response.candidates:
            raise RuntimeError("Gemini повернув порожній список candidates.")

        candidate = response.candidates[0]

        if not candidate.content or not candidate.content.parts:
            finish = getattr(candidate, "finish_reason", "unknown")
            raise RuntimeError(f"Gemini candidate без parts. finish_reason={finish}")

        model_parts = list(candidate.content.parts)
        function_calls = _extract_function_calls(model_parts)

        if not function_calls:
            text = _extract_text(model_parts)
            return text if text else "Вибач, не вдалося сформувати відповідь."

        current_contents.append(types.Content(role="model", parts=model_parts))

        tool_response_parts = []
        for part in function_calls:
            fc = part.function_call
            logger.debug("Calling tool: %s with args: %s", fc.name, dict(fc.args))
            result = execute_tool(fc.name, dict(fc.args))
            logger.debug("Tool result: %s", result)
            tool_response_parts.append(
                types.Part(
                    function_response=types.FunctionResponse(
                        name=fc.name,
                        response={"result": json.dumps(result, ensure_ascii=False)},
                    )
                )
            )

        current_contents.append(types.Content(role="user", parts=tool_response_parts))

    return "Вибач, не вдалося знайти відповідь. Спробуй перефразувати запит."