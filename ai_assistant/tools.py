import os
import re

from google.genai import types

_KB_PATH = os.path.join(os.path.dirname(__file__), "knowledge_base.txt")
_routes_cache = None


def _load_routes():
    global _routes_cache
    if _routes_cache is not None:
        return _routes_cache

    with open(_KB_PATH, encoding="utf-8") as f:
        content = f.read()

    blocks = content.split("\n---\n")
    routes = []

    for block in blocks:
        block = block.strip()
        if not block or block.startswith("#") or "НАЗВА:" not in block:
            continue

        route = {}

        for field in ("НАЗВА", "РЕГІОН", "ВИСОТА", "СКЛАДНІСТЬ", "ВІДСТАНЬ", "ТРИВАЛІСТЬ", "РЕЙТИНГ"):
            match = re.search(rf"^{field}:\s*(.+)$", block, re.MULTILINE)
            if match:
                route[field.lower()] = match.group(1).strip()

        desc_match = re.search(r"ОПИС:\n(.*?)(?=\nПОРАДИ:|\nТЕГИ:|$)", block, re.DOTALL)
        if desc_match:
            route["опис"] = desc_match.group(1).strip()

        advice_match = re.search(r"ПОРАДИ:\n(.*?)(?=\nТЕГИ:|$)", block, re.DOTALL)
        if advice_match:
            route["поради"] = advice_match.group(1).strip()

        tags_match = re.search(r"ТЕГИ:\s*(.+)$", block, re.MULTILINE)
        if tags_match:
            route["теги"] = [t.strip() for t in tags_match.group(1).split(",")]

        if route.get("назва"):
            routes.append(route)

    _routes_cache = routes
    return routes


def _load_general_info():
    with open(_KB_PATH, encoding="utf-8") as f:
        content = f.read()
    match = re.search(r"# ЗАГАЛЬНА ІНФОРМАЦІЯ ПРО КАРПАТИ\n(.*)", content, re.DOTALL)
    return match.group(1).strip() if match else ""


# ---------------------------------------------------------------------------
# Gemini Tool declarations
# ---------------------------------------------------------------------------

GEMINI_TOOLS = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="search_routes",
            description=(
                "Шукає маршрути за ключовими словами у назві, описі, тегах або регіоні. "
                "Використовуй, коли користувач згадує конкретну назву гори або місцевість."
            ),
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "query": types.Schema(
                        type=types.Type.STRING,
                        description="Ключові слова для пошуку: назва вершини, регіон, особливість.",
                    ),
                },
                required=["query"],
            ),
        ),
        types.FunctionDeclaration(
            name="filter_routes",
            description=(
                "Фільтрує маршрути за характеристиками: складність, максимальна тривалість, "
                "максимальна відстань, регіон, наявність тегів (наприклад 'діти', 'озеро', 'панорама'). "
                "Використовуй, коли користувач описує побажання без конкретної назви маршруту."
            ),
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "difficulty": types.Schema(
                        type=types.Type.STRING,
                        description="Рівень складності: 'легка', 'середня' або 'важка'.",
                    ),
                    "max_duration_hours": types.Schema(
                        type=types.Type.NUMBER,
                        description="Максимальна тривалість у годинах.",
                    ),
                    "max_distance_km": types.Schema(
                        type=types.Type.NUMBER,
                        description="Максимальна відстань у кілометрах.",
                    ),
                    "region_keyword": types.Schema(
                        type=types.Type.STRING,
                        description="Ключове слово у назві регіону, напр. 'Закарпатська', 'Львівська', 'Івано-Франківська'.",
                    ),
                    "tags": types.Schema(
                        type=types.Type.ARRAY,
                        items=types.Schema(type=types.Type.STRING),
                        description="Список тегів для фільтрації, напр. ['діти', 'озеро', 'панорама', 'один день'].",
                    ),
                },
            ),
        ),
        types.FunctionDeclaration(
            name="get_route_details",
            description=(
                "Повертає повну інформацію про конкретний маршрут за назвою. "
                "Використовуй після того, як знайшов маршрут і хочеш надати детальний опис з порадами."
            ),
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "name": types.Schema(
                        type=types.Type.STRING,
                        description="Точна або часткова назва маршруту, напр. 'Говерла' або 'Піп Іван'.",
                    ),
                },
                required=["name"],
            ),
        ),
        types.FunctionDeclaration(
            name="get_general_info",
            description=(
                "Повертає загальну інформацію про Карпати: безпеку, спорядження, сезонність, "
                "типи туристів та рекомендації. Використовуй, коли питання стосується підготовки до походу, "
                "безпеки або вибору сезону."
            ),
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={},
            ),
        ),
    ]
)


# ---------------------------------------------------------------------------
# Tool execution logic
# ---------------------------------------------------------------------------

def _route_summary(route):
    desc = route.get("опис", "")
    return {
        "назва": route.get("назва"),
        "регіон": route.get("регіон"),
        "висота": route.get("висота"),
        "складність": route.get("складність"),
        "відстань": route.get("відстань"),
        "тривалість": route.get("тривалість"),
        "рейтинг": route.get("рейтинг"),
        "опис_коротко": desc[:200] + "..." if len(desc) > 200 else desc,
        "теги": route.get("теги", []),
    }


def execute_tool(name: str, inputs: dict) -> dict:
    if name == "search_routes":
        query = inputs.get("query", "").lower()
        routes = _load_routes()
        results = []
        for r in routes:
            searchable = " ".join([
                r.get("назва", ""),
                r.get("регіон", ""),
                r.get("опис", ""),
                " ".join(r.get("теги", [])),
            ]).lower()
            if query in searchable:
                results.append(_route_summary(r))
        if not results:
            return {"found": 0, "routes": [], "message": "Маршрутів за таким запитом не знайдено."}
        return {"found": len(results), "routes": results[:5]}

    if name == "filter_routes":
        routes = _load_routes()
        results = []

        difficulty = inputs.get("difficulty")
        max_duration = inputs.get("max_duration_hours")
        max_distance = inputs.get("max_distance_km")
        region_kw = (inputs.get("region_keyword") or "").lower()
        tags = [t.lower() for t in (inputs.get("tags") or [])]

        for r in routes:
            if difficulty and r.get("складність") != difficulty:
                continue

            if max_duration is not None:
                m = re.search(r"(\d+(?:\.\d+)?)", r.get("тривалість", ""))
                if m and float(m.group(1)) > max_duration:
                    continue

            if max_distance is not None:
                m = re.search(r"(\d+(?:\.\d+)?)", r.get("відстань", ""))
                if m and float(m.group(1)) > max_distance:
                    continue

            if region_kw and region_kw not in r.get("регіон", "").lower():
                continue

            if tags:
                route_text = " ".join(r.get("теги", [])).lower() + " " + r.get("опис", "").lower()
                if not all(tag in route_text for tag in tags):
                    continue

            results.append(_route_summary(r))

        if not results:
            return {"found": 0, "routes": [], "message": "За вказаними параметрами маршрутів не знайдено."}
        results.sort(key=lambda x: float(x.get("рейтинг") or 0), reverse=True)
        return {"found": len(results), "routes": results[:5]}

    if name == "get_route_details":
        query = inputs.get("name", "").lower()
        routes = _load_routes()
        for r in routes:
            if query in r.get("назва", "").lower():
                return {
                    "назва": r.get("назва"),
                    "регіон": r.get("регіон"),
                    "висота": r.get("висота"),
                    "складність": r.get("складність"),
                    "відстань": r.get("відстань"),
                    "тривалість": r.get("тривалість"),
                    "рейтинг": r.get("рейтинг"),
                    "опис": r.get("опис"),
                    "поради": r.get("поради"),
                    "теги": r.get("теги", []),
                }
        return {"error": f"Маршрут '{inputs.get('name')}' не знайдено в базі."}

    if name == "get_general_info":
        return {"info": _load_general_info()}

    return {"error": f"Невідома функція: {name}"}