"""Image generation and Cloud Storage upload tools for Fridge-to-Table Chef."""

import re
import uuid
from typing import Any
from google import genai
from google.adk.tools import ToolContext
from google.cloud import storage
from google.genai import types

# Hardcoded bucket and project values
PROJECT_ID = "qwiklabs-gcp-04-e7977ef4863a"
BUCKET_NAME = "fridge-to-table-chef-yyfvv1"
IMAGE_MODEL = "gemini-3.1-flash-lite-image"


def generate_dish_image(
    dish_name: str,
    tool_context: ToolContext,
    description: str = "",
) -> dict[str, Any]:
    """Generate an appetizing preview image of a dish and publish it.

    This generates an image using gemini-3.1-flash-lite-image in the global region,
    saves it into the session artifacts panel, uploads the bytes directly to Google Cloud Storage,
    and returns the public HTTPS URL.

    Args:
        dish_name: Name of the dish (e.g. 'Garlic Butter Chicken & Spinach', 'Cheddar Spinach Omelet').
        tool_context: ADK ToolContext injected automatically by the runtime.
        description: Optional culinary details to emphasize in the visual presentation.

    Returns:
        A dictionary with the public image URL, filename, and status.
    """
    # 1. Initialize GenAI client in global region
    client = genai.Client(vertexai=True, project=PROJECT_ID, location="global")

    prompt = (
        f"A beautifully plated, delicious, restaurant-quality culinary photograph of {dish_name}. "
        f"{description} Natural warm lighting, gourmet presentation, shallow depth of field, food photography."
    )

    response = client.models.generate_content(
        model=IMAGE_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(response_modalities=["IMAGE"]),
    )

    image_bytes = None
    mime_type = "image/jpeg"
    for candidate in response.candidates or []:
        for part in candidate.content.parts or []:
            if part.inline_data and part.inline_data.data:
                image_bytes = part.inline_data.data
                mime_type = part.inline_data.mime_type or "image/jpeg"
                break
        if image_bytes:
            break

    if not image_bytes:
        return {"status": "error", "message": "Failed to generate image bytes from model."}

    # Clean slug for filename
    clean_slug = re.sub(r"[^a-zA-Z0-9]+", "-", dish_name.lower()).strip("-") or "dish"
    ext = "png" if "png" in mime_type else "jpg"
    unique_suffix = uuid.uuid4().hex[:6]
    filename = f"{clean_slug}-{unique_suffix}.{ext}"

    # 2. Save artifact to ToolContext so it shows in the Playground Artifacts panel
    artifact_part = types.Part(
        inline_data=types.Blob(
            data=image_bytes,
            mime_type=mime_type,
        )
    )
    tool_context.save_artifact(filename=filename, artifact=artifact_part)

    # 3. Upload bytes directly to Google Cloud Storage (no local file written)
    storage_client = storage.Client(project=PROJECT_ID)
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(filename)
    blob.upload_from_string(image_bytes, content_type=mime_type)

    public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{filename}"

    return {
        "status": "success",
        "dish_name": dish_name,
        "filename": filename,
        "public_url": public_url,
    }
