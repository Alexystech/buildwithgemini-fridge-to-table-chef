"""Firestore tools for managing fridge inventory."""

import re
from typing import Any
from google.cloud import firestore

# Hardcoded project ID as required to prevent project number resolution issues on Agent Platform
PROJECT_ID = "qwiklabs-gcp-04-e7977ef4863a"
COLLECTION_NAME = "fridge_inventory"

_db = None


def _get_db() -> firestore.Client:
    global _db
    if _db is None:
        _db = firestore.Client(project=PROJECT_ID)
    return _db


def _slugify(name: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", name.lower()).strip("-")
    return slug or "item"


def list_fridge_inventory(category: str = "") -> list[dict[str, Any]]:
    """List all food items currently in the fridge inventory.

    Args:
        category: Optional category filter (e.g., 'dairy', 'produce', 'meat').
                  Leave empty to return all items.

    Returns:
        A list of items currently in the fridge with their quantity, unit, days left, and category.
    """
    db = _get_db()
    docs = db.collection(COLLECTION_NAME).stream()
    items = []
    category_filter = category.strip().lower()

    for doc in docs:
        data = doc.to_dict()
        if category_filter:
            item_cat = str(data.get("category", "")).lower()
            if category_filter not in item_cat:
                continue
        items.append(data)

    # Sort items by days_left ascending so expiring items appear first
    items.sort(key=lambda x: x.get("days_left", 999))
    return items


def add_or_update_fridge_item(
    name: str,
    quantity: float,
    unit: str,
    category: str = "general",
    days_left: int = 7,
    notes: str = "",
) -> dict[str, Any]:
    """Add a new food item or update an existing item in the fridge inventory.

    Args:
        name: Name of the food item (e.g. 'Greek Yogurt', 'Avocados').
        quantity: Numerical quantity available.
        unit: Unit of measure (e.g. 'grams', 'pieces', 'liters', 'pack').
        category: Food category (e.g. 'produce', 'dairy', 'meat', 'bakery', 'condiment').
        days_left: Estimated days until expiration/spoilage.
        notes: Optional extra detail (e.g. 'Opened', 'Organic', 'Store-bought').

    Returns:
        The saved item record.
    """
    db = _get_db()
    item_id = _slugify(name)
    doc_ref = db.collection(COLLECTION_NAME).document(item_id)

    item_data = {
        "item_id": item_id,
        "name": name.strip(),
        "quantity": quantity,
        "unit": unit.strip().lower(),
        "category": category.strip().lower(),
        "days_left": int(days_left),
        "notes": notes.strip(),
    }
    doc_ref.set(item_data)
    return {"status": "success", "item": item_data}


def remove_fridge_item(item_name: str) -> dict[str, Any]:
    """Remove a food item from the fridge (e.g. when fully consumed or expired).

    Args:
        item_name: Name or item ID of the ingredient to remove (e.g. 'eggs', 'spinach').

    Returns:
        Status message indicating if the item was removed.
    """
    db = _get_db()
    item_id = _slugify(item_name)
    doc_ref = db.collection(COLLECTION_NAME).document(item_id)
    doc = doc_ref.get()

    if not doc.exists:
        # Search by name match in case slug differs slightly
        docs = list(db.collection(COLLECTION_NAME).stream())
        matched_id = None
        for d in docs:
            data = d.to_dict()
            if item_name.strip().lower() in data.get("name", "").lower():
                matched_id = d.id
                break
        if matched_id:
            db.collection(COLLECTION_NAME).document(matched_id).delete()
            return {"status": "success", "removed_item_id": matched_id}
        return {"status": "not_found", "message": f"No item matching '{item_name}' found in fridge."}

    doc_ref.delete()
    return {"status": "success", "removed_item_id": item_id}
