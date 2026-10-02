"""Public API tool integrating TheMealDB for culinary recipe search."""

import os
from typing import Any
import requests

THEMEALDB_API_KEY = os.environ.get("THEMEALDB_API_KEY", "1")
BASE_URL = f"https://www.themealdb.com/api/json/v1/{THEMEALDB_API_KEY}"


def search_online_recipes_by_ingredient(ingredient: str) -> list[dict[str, Any]]:
    """Search for real recipes online that feature a specific ingredient.

    Uses TheMealDB public API to discover community dishes from around the world.

    Args:
        ingredient: An ingredient to search recipes for (e.g., 'chicken_breast', 'egg', 'tomato', 'cheese').

    Returns:
        A list of recipes with meal title, meal ID, thumbnail image URL, and country/origin if available.
    """
    clean_ing = ingredient.strip().lower().replace(" ", "_")
    url = f"{BASE_URL}/filter.php?i={clean_ing}"

    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        meals = data.get("meals") or []

        results = []
        for meal in meals[:5]:  # Return top 5 matches
            results.append({
                "meal_id": meal.get("idMeal"),
                "title": meal.get("strMeal"),
                "image_url": meal.get("strMealThumb"),
                "country": meal.get("strCountry") or meal.get("strArea") or "International",
            })
        return results
    except Exception as e:
        return [{"error": f"Failed to fetch recipes from TheMealDB: {str(e)}"}]
