"""Video generation and Cloud Storage upload tools for Fridge-to-Table Chef."""

import base64
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
VIDEO_MODEL = "gemini-omni-flash-preview"


def generate_dish_video(
    dish_name: str,
    tool_context: ToolContext,
    description: str = "",
) -> dict[str, Any]:
    """Generate a short video for a culinary dish using Google's Omni model (gemini-omni-flash-preview).

    This generates a short video using gemini-omni-flash-preview in the global region via the
    Interactions API, saves it into the session artifacts panel with tool_context.save_artifact,
    uploads the same video bytes directly to the public Google Cloud Storage bucket, and returns
    its public HTTPS URL (https://storage.googleapis.com/<bucket>/<object>).

    Args:
        dish_name: Name of the dish or culinary item (e.g. 'Garlic Butter Chicken & Spinach', 'Sizzling Ribeye').
        tool_context: ADK ToolContext injected automatically by the runtime.
        description: Optional culinary details to emphasize in the visual presentation (e.g., steam rising, sizzling pan).

    Returns:
        A dictionary with the public video URL, filename, and status.
    """
    # 1. Initialize GenAI client in global region
    client = genai.Client(vertexai=True, project=PROJECT_ID, location="global")

    prompt = (
        f"A cinematic, mouth-watering close-up culinary video of {dish_name}. "
        f"{description} Sizzling hot preparation, aromatic steam rising, gourmet restaurant quality, smooth camera movement, food commercial style."
    )

    try:
        interaction = client.interactions.create(
            model=VIDEO_MODEL,
            input=prompt,
        )
    except Exception as e:
        return {"status": "error", "message": f"Video generation failed: {e}"}

    output_video = getattr(interaction, "output_video", None)
    if not output_video or not getattr(output_video, "data", None):
        return {"status": "error", "message": "No video data returned in interaction."}

    raw_data = output_video.data
    # If the video data is base64-encoded string, decode it into bytes
    if isinstance(raw_data, str):
        try:
            video_bytes = base64.b64decode(raw_data)
        except Exception:
            video_bytes = raw_data.encode("utf-8")
    elif isinstance(raw_data, bytes):
        video_bytes = raw_data
    else:
        video_bytes = bytes(raw_data)

    mime_type = getattr(output_video, "mime_type", None) or "video/mp4"

    # Clean slug for filename
    clean_slug = re.sub(r"[^a-zA-Z0-9]+", "-", dish_name.lower()).strip("-") or "dish"
    ext = "mp4" if "mp4" in mime_type else "mp4"
    unique_suffix = uuid.uuid4().hex[:6]
    filename = f"{clean_slug}-{unique_suffix}.{ext}"

    # 2. Save artifact to ToolContext so it shows in the Playground Artifacts panel
    artifact_part = types.Part(
        inline_data=types.Blob(
            data=video_bytes,
            mime_type=mime_type,
        )
    )
    tool_context.save_artifact(filename=filename, artifact=artifact_part)

    # 3. Upload bytes directly to Google Cloud Storage (no local file written)
    storage_client = storage.Client(project=PROJECT_ID)
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(filename)
    blob.upload_from_string(video_bytes, content_type=mime_type)

    public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{filename}"

    return {
        "status": "success",
        "dish_name": dish_name,
        "filename": filename,
        "public_url": public_url,
    }
