import json
import requests
from langchain.tools import tool

MEALDB_BASE = "https://www.themealdb.com/api/json/v1/1"
TIMEOUT = 10


def _get(url: str, params: dict) -> dict | None:
    for attempt in range(2):
        try:
            r = requests.get(url, params=params, timeout=TIMEOUT)
            r.raise_for_status()
            return r.json()
        except requests.exceptions.Timeout:
            if attempt == 1:
                return None
        except requests.exceptions.RequestException:
            return None
    return None


# ── Plain functions (called directly by agent.py) ────────────────────────────

def search_recipes(ingredient: str) -> list[dict]:
    """Returns list of {id, name} dicts. Empty list if nothing found."""
    data = _get(f"{MEALDB_BASE}/filter.php", {"i": ingredient})
    if not data or not data.get("meals"):
        simplified = ingredient.split()[0]
        if simplified != ingredient:
            data = _get(f"{MEALDB_BASE}/filter.php", {"i": simplified})
    if not data or not data.get("meals"):
        return []
    return [{"id": m["idMeal"], "name": m["strMeal"]} for m in data["meals"][:10]]


def get_recipe(meal_id: str) -> dict | None:
    """Returns full recipe dict or None."""
    data = _get(f"{MEALDB_BASE}/lookup.php", {"i": meal_id})
    if not data or not data.get("meals"):
        return None
    meal = data["meals"][0]
    ingredients = []
    for i in range(1, 21):
        ing  = (meal.get(f"strIngredient{i}") or "").strip()
        meas = (meal.get(f"strMeasure{i}") or "").strip()
        if ing:
            ingredients.append(f"{meas} {ing}".strip())
    return {
        "id":           meal["idMeal"],
        "name":         meal["strMeal"],
        "category":     meal.get("strCategory", ""),
        "area":         meal.get("strArea", ""),
        "ingredients":  ingredients,
        "instructions": (meal.get("strInstructions") or "")[:800],
    }


# ── LangChain @tool wrappers (kept for future agent use) ─────────────────────

@tool
def search_recipes_by_ingredient(ingredient: str) -> str:
    """Search TheMealDB for recipes that use a given ingredient.
    Returns a JSON list of meal names and IDs."""
    results = search_recipes(ingredient)
    if not results:
        return f"No recipes found for ingredient: {ingredient}. Try a simpler name."
    return json.dumps(results, indent=2)


@tool
def get_recipe_details(meal_id: str) -> str:
    """Fetch full recipe details from TheMealDB by meal ID."""
    detail = get_recipe(meal_id)
    if not detail:
        return f"Could not retrieve details for meal ID: {meal_id}"
    return json.dumps(detail, indent=2)
