import json
import os

from pathlib import Path
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from tools import search_recipes, get_recipe

OUTPUT_FILE = Path(__file__).parent / "meal_plan.txt"

PLAN_PROMPT = """\
You are a meal planning chef. Using ONLY the recipes listed below, create:

1. A 3-day meal plan in this EXACT pipe-delimited format (no extra text on these lines):
   Day 1 | <Breakfast meal> | <Lunch meal> | <Dinner meal>
   Day 2 | <Breakfast meal> | <Lunch meal> | <Dinner meal>
   Day 3 | <Breakfast meal> | <Lunch meal> | <Dinner meal>

   Rules:
   - Use only meal names from the recipes provided.
   - Skip any meal that violates the dietary preference: {preferences}.
   - Reuse meals across days if needed to fill all 9 slots.

2. A shopping list of ingredients NOT already in the user's available ingredients.
   Format as bullet points: - ingredient name

Available ingredients: {ingredients}
Dietary preferences: {preferences}

Recipes available:
{recipes}
"""


def _build_llm() -> ChatOpenAI:
    load_dotenv(override=True)
    api_key = os.getenv("OPENROUTER_API_KEY", "")
    model = os.getenv("OPENROUTER_MODEL", "deepseek/deepseek-v4-flash:free")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY is not set in .env")
    return ChatOpenAI(
        model=model,
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
        temperature=0.4,
        default_headers={
            "HTTP-Referer": "https://github.com/100-days-agentic-ai",
            "X-Title": "Smart Recipe Planner",
        },
    )


def run_agent(
    ingredients: str,
    preferences: str,
    on_step=None,   # optional callable(str) for live progress updates
) -> str:

    def step(msg: str):
        if on_step:
            on_step(msg)

    # ── Step 1: search TheMealDB directly (no LLM needed) ────────────────────
    ing_list = [i.strip() for i in ingredients.replace(";", ",").split(",") if i.strip()][:5]
    recipe_details: list[dict] = []
    seen_ids: set[str] = set()

    for ing in ing_list:
        step(f"🔍 Searching recipes for: **{ing}**")
        meals = search_recipes(ing)          # returns list[dict] directly

        if not meals:
            step(f"   ⚠️ No results for **{ing}**")
            continue

        step(f"   ✅ Found **{len(meals)}** recipes")

        for meal in meals[:2]:
            meal_id = meal["id"]
            if meal_id in seen_ids:
                continue
            seen_ids.add(meal_id)
            step(f"📖 Fetching details: **{meal['name']}**")
            detail = get_recipe(meal_id)
            if detail:
                recipe_details.append(detail)

    if not recipe_details:
        return (
            "Could not find any recipes for the given ingredients. "
            "Please try common ingredient names like 'chicken', 'pasta', 'tomato'."
        )

    # ── Step 2: one LLM call to plan ─────────────────────────────────────────
    step(f"🧠 Sending **{len(recipe_details)}** recipes to AI to build meal plan…")

    recipes_text = json.dumps(
        [{"name": r["name"], "ingredients": r["ingredients"][:10]} for r in recipe_details],
        indent=2,
    )
    prompt = PLAN_PROMPT.format(
        ingredients=ingredients,
        preferences=preferences or "none",
        recipes=recipes_text,
    )

    llm = _build_llm()
    response = llm.invoke([HumanMessage(content=prompt)])
    result = response.content.strip()

    step("🏁 **Done!**")
    OUTPUT_FILE.write_text(result, encoding="utf-8")
    return result


if __name__ == "__main__":
    ingredients = input("Ingredients you have: ")
    preferences = input("Dietary preferences (or none): ")
    print("=" * 60)

    def printer(msg):
        print(msg)

    output = run_agent(ingredients, preferences, on_step=printer)
    print("=" * 60)
    print(output)
