# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types

load_dotenv()

MODEL = "gemini-2.5-flash"


def get_weather(query: str) -> str:
    """Simulates a web search. Use it get information on weather.

    Args:
        query: A string containing the location to get weather information for.

    Returns:
        A string with the simulated weather information for the queried location.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        return "It's 60 degrees and foggy."
    return "It's 90 degrees and sunny."


def get_current_time(query: str) -> str:
    """Simulates getting the current time for a city.

    Args:
        city: The name of the city to get the current time for.

    Returns:
        A string with the current time information.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        tz_identifier = "America/Los_Angeles"
    else:
        return f"Sorry, I don't have timezone information for query: {query}."

    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    return f"The current time for query {query} is {now.strftime('%Y-%m-%d %H:%M:%S %Z%z')}"


from app.inventory_tools import (
    add_or_update_fridge_item,
    list_fridge_inventory,
    remove_fridge_item,
)
from app.recipe_tools import find_matching_recipes
from app.mealdb_tools import search_online_recipes_by_ingredient
from a2ui.basic_catalog.provider import BasicCatalog
from a2ui.schema.manager import A2uiSchemaManager
from app.a2ui_utils import a2ui_callback
from app.image_tools import generate_dish_image
from app.inventory_tools import (
    add_or_update_fridge_item,
    list_fridge_inventory,
    remove_fridge_item,
)
from app.mealdb_tools import search_online_recipes_by_ingredient
from app.recipe_tools import find_matching_recipes
from app.sandbox_tools import run_code
from app.video_tools import generate_dish_video
from google.adk.agents.callback_context import CallbackContext
from google.adk.code_executors import AgentEngineSandboxCodeExecutor
from google.adk.memory import VertexAiMemoryBankService
from google.adk.tools.preload_memory_tool import PreloadMemoryTool

PROJECT_ID = "qwiklabs-gcp-04-e7977ef4863a"
MEMORY_BANK_ID = "104428315871281152"
LOCATION = "us-east1"

SANDBOX_RESOURCE_NAME = (
    f"projects/460274758047/locations/{LOCATION}/reasoningEngines/{MEMORY_BANK_ID}"
    "/sandboxEnvironments/4773191082408148992"
)


# WRITE: after each turn, send the session to Memory Bank for extraction.
async def generate_memories_callback(callback_context: CallbackContext):
    if getattr(callback_context._invocation_context, "memory_service", None) is not None:
        await callback_context.add_session_to_memory()
    return None


schema_manager = A2uiSchemaManager(
    version="0.8",
    catalogs=[BasicCatalog.get_config("0.8")],
)

instruction = schema_manager.generate_system_prompt(
    role_description=(
        "You are the Fridge-to-Table Chef, a creative culinary AI assistant. "
        "Your mission is to help home cooks prepare delicious dishes using ingredients currently available in their fridge, "
        "minimizing food waste and taking into account expiration priorities (days left). "
        "You remember the user's stated dietary preferences, allergies, disliked foods, and culinary habits across conversations. "
        "You can inspect current fridge inventory, search for matching local recipes, discover global dishes via online recipe search (TheMealDB), "
        "generate appetizing dish preview images, generate short culinary preview videos, execute Python code in a secure sandbox for recipe portion calculations and nutritional math, "
        "note which ingredients should be used soonest, and help users add, update, or remove items in their fridge inventory."
    ),
    workflow_description="Analyze the request, call available tools when needed, and return structured UI when appropriate.",
    ui_description=(
        "Keep every surface tiny and flat: ONE Card > ONE Column > a few Text rows. "
        "Never nest a Card inside a Card. "
        "Use ONLY these components: Card, Column, Row, Text, and Image. Do not use "
        "Table or Heading (unsupported), or Buttons, actions, or forms (they do "
        "nothing in adk web). "
        "You may include one Image component, but only when you have a public https "
        "URL for the image (for example the URL an image tool returns after uploading "
        "to a public bucket). Set the Image url to that exact https link, for example "
        '{"Image": {"url": {"literalString": "https://..."}}}. Never point an '
        "Image at a bare filename, an artifact name, or a non-http(s) path. If you do "
        "not have a public URL, add a short Text line noting the image instead. "
        "No markdown in text; use the usageHint property ('h1', 'h2', 'body') for "
        "headings and emphasis. "
        "Output ONLY the raw A2UI JSON array — no prose, and never wrap it in "
        "<a2a_datapart_json> tags or 'kind'/'data'/'metadata' objects."
    ),
    include_schema=True,
    include_examples=True,
)

root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=instruction,
    code_executor=AgentEngineSandboxCodeExecutor(
        sandbox_resource_name=SANDBOX_RESOURCE_NAME,
    ),
    tools=[
        PreloadMemoryTool(),
        list_fridge_inventory,
        find_matching_recipes,
        search_online_recipes_by_ingredient,
        generate_dish_image,
        generate_dish_video,
        run_code,
        add_or_update_fridge_item,
        remove_fridge_item,
        get_weather,
        get_current_time,
    ],
    after_model_callback=a2ui_callback,
    after_agent_callback=generate_memories_callback,
)


def memory_bank_service_builder():
    """Builds the Vertex AI Memory Bank service for deployed Agent Runtime."""
    return VertexAiMemoryBankService(
        project=PROJECT_ID,
        location=LOCATION,
        agent_engine_id=MEMORY_BANK_ID,
    )


# Set on app for Agent Runtime deployment runners / reasoning engines
memory_service_builder = memory_bank_service_builder

app = App(
    root_agent=root_agent,
    name="app",
)
