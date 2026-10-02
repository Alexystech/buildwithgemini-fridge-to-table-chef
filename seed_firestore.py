"""Seed script for Fridge-to-Table Chef Firestore collection."""

from google.cloud import firestore

# Hardcoded project ID as required
PROJECT_ID = "qwiklabs-gcp-04-e7977ef4863a"
COLLECTION_NAME = "fridge_inventory"

SEEDED_ITEMS = [
    {
        "item_id": "eggs",
        "name": "Eggs",
        "quantity": 6,
        "unit": "pieces",
        "category": "dairy/poultry",
        "days_left": 5,
        "notes": "Large brown eggs",
    },
    {
        "item_id": "whole-milk",
        "name": "Whole Milk",
        "quantity": 1,
        "unit": "liter",
        "category": "dairy",
        "days_left": 3,
        "notes": "Opened 2 days ago",
    },
    {
        "item_id": "cheddar-cheese",
        "name": "Cheddar Cheese",
        "quantity": 200,
        "unit": "grams",
        "category": "dairy",
        "days_left": 12,
        "notes": "Block of sharp cheddar",
    },
    {
        "item_id": "baby-spinach",
        "name": "Baby Spinach",
        "quantity": 150,
        "unit": "grams",
        "category": "produce",
        "days_left": 2,
        "notes": "Use soon",
    },
    {
        "item_id": "roma-tomatoes",
        "name": "Roma Tomatoes",
        "quantity": 3,
        "unit": "pieces",
        "category": "produce",
        "days_left": 4,
        "notes": "Ripe",
    },
    {
        "item_id": "chicken-breast",
        "name": "Chicken Breast",
        "quantity": 450,
        "unit": "grams",
        "category": "meat",
        "days_left": 1,
        "notes": "Thawed in fridge, cook today or freeze",
    },
    {
        "item_id": "butter",
        "name": "Unsalted Butter",
        "quantity": 1,
        "unit": "stick",
        "category": "dairy",
        "days_left": 20,
        "notes": "Standard stick",
    },
    {
        "item_id": "garlic",
        "name": "Garlic Cloves",
        "quantity": 4,
        "unit": "cloves",
        "category": "produce",
        "days_left": 15,
        "notes": "Peeled in crisper",
    },
]


def seed():
    print(f"Connecting to Firestore project: {PROJECT_ID}...")
    db = firestore.Client(project=PROJECT_ID)
    collection_ref = db.collection(COLLECTION_NAME)

    for item in SEEDED_ITEMS:
        doc_ref = collection_ref.document(item["item_id"])
        doc_ref.set(item)
        print(f"Seeded: {item['name']} ({item['quantity']} {item['unit']})")

    print(f"\nSuccessfully seeded {len(SEEDED_ITEMS)} items into '{COLLECTION_NAME}'.")


if __name__ == "__main__":
    seed()
