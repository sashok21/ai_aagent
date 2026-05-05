import json
import os

from google import genai
from google.genai import types

from .tools import GEMINI_TOOLS, execute_tool

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

MODEL = "gemini-2.0-flash"
MAX_ITERATIONS = 6


def _build_gemini_history(conversation_history: list) -> list:
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


def run_agent(conversation_history: list) -> str:
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    history = conversation_history[:-1]
    last_user_message = conversation_history[-1]["content"]

    current_contents = _build_gemini_history(history) + [
        types.Content(
            role="user",
            parts=[types.Part(text=last_user_message)],
        )
    ]

    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        tools=[GEMINI_TOOLS],
        temperature=0.4,
        max_output_tokens=1500,
    )

    for _ in range(MAX_ITERATIONS):
        response = client.models.generate_content(
            model=MODEL,
            contents=current_contents,
            config=config,
        )

        candidate = response.candidates[0]
        model_parts = list(candidate.content.parts)
        function_calls = [p for p in model_parts if p.function_call is not None]

        if not function_calls:
            text_parts = [p.text for p in model_parts if p.text]
            return "\n".join(text_parts) if text_parts else "Вибач, не вдалося сформувати відповідь."

        current_contents.append(types.Content(role="model", parts=model_parts))

        response_parts = []
        for part in function_calls:
            fc = part.function_call
            result = execute_tool(fc.name, dict(fc.args))
            response_parts.append(
                types.Part(
                    function_response=types.FunctionResponse(
                        name=fc.name,
                        response={"result": json.dumps(result, ensure_ascii=False)},
                    )
                )
            )

        current_contents.append(types.Content(role="user", parts=response_parts))

    return "Вибач, не вдалося знайти відповідь. Спробуй перефразувати запит."