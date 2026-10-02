"""Recipe matching tool for Fridge-to-Table Chef."""

from typing import Any
from app.inventory_tools import list_fridge_inventory

RECIPE_CATALOG = [
    {
        "id": "garlic-butter-chicken-spinach",
        "title": "Garlic Butter Chicken & Spinach",
        "prep_time_minutes": 25,
        "difficulty": "Easy",
        "required_ingredients": ["chicken-breast", "baby-spinach", "butter", "garlic"],
        "instructions": (
            "1. Sauté minced garlic in butter until fragrant. "
            "2. Sear seasoned chicken breast until cooked through. "
            "3. Toss in baby spinach until wilted and serve warm."
        ),
    },
    {
        "id": "cheddar-spinach-omelet",
        "title": "Cheddar & Spinach Omelet",
        "prep_time_minutes": 15,
        "difficulty": "Easy",
        "required_ingredients": ["eggs", "baby-spinach", "cheddar-cheese", "butter"],
        "instructions": (
            "1. Whisk eggs with a splash of milk or water. "
            "2. Melt butter in a skillet, pour eggs, and fold in sautéed spinach and cheddar. "
            "3. Cook until cheese melts."
        ),
    },
    {
        "id": "creamy-tomato-chicken-skillet",
        "title": "Creamy Tomato Chicken Skillet",
        "prep_time_minutes": 30,
        "difficulty": "Medium",
        "required_ingredients": ["chicken-breast", "roma-tomatoes", "whole-milk", "garlic", "butter"],
        "instructions": (
            "1. Brown chicken in butter. "
            "2. Add diced tomatoes and minced garlic, simmer until tender. "
            "3. Stir in whole milk to create a rich pan sauce."
        ),
    },
    {
        "id": "cheesy-scrambled-eggs",
        "title": "Classic Cheesy Scrambled Eggs",
        "prep_time_minutes": 10,
        "difficulty": "Easy",
        "required_ingredients": ["eggs", "cheddar-cheese", "butter", "whole-milk"],
        "instructions": (
            "1. Beat eggs with whole milk. "
            "2. Cook slowly in melted butter over low heat. "
            "3. Fold in shredded cheddar right before removing from heat."
        ),
    },
]


def find_matching_recipes(max_missing: int = 1) -> list[dict[str, Any]]:
    """Search for recipes that can be made using ingredients currently in the fridge.

    Args:
        max_missing: Maximum number of missing ingredients allowed (default is 1).

    Returns:
        A list of matching recipes scored by how many fridge ingredients they use,
        including which ingredients are available and which are missing.
    """
    inventory = list_fridge_inventory()
    available_item_ids = {item.get("item_id") for item in inventory}

    matches = []
    for recipe in RECIPE_CATALOG:
        required = set(recipe["required_ingredients"])
        have = required.intersection(available_item_ids)
        missing = required - available_item_ids

        if len(missing) <= max_missing:
            match_percentage = int((len(have) / len(required)) * 100)
            matches.append({
                "id": recipe["id"],
                "title": recipe["title"],
                "prep_time_minutes": recipe["prep_time_minutes"],
                "difficulty": recipe["difficulty"],
                "match_percentage": match_percentage,
                "available_ingredients": sorted(list(have)),
                "missing_ingredients": sorted(list(missing)),
                "instructions": recipe["instructions"],
            })

    # Sort recipes by highest match percentage first, then shortest prep time
    matches.sort(key=lambda r: (-r["match_percentage"], r["prep_time_minutes"]))
    return matches
