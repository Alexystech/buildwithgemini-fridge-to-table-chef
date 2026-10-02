# Fridge-to-Table Chef

> A conversational culinary AI assistant built with Google Agent Development Kit (ADK) that turns whatever ingredients are currently in your fridge into delicious dishes, prioritizing items before they expire to eliminate food waste.

![Fridge-to-Table Chef Demo](docs/images/demo.gif)

---

## Capabilities & Architecture

Fridge-to-Table Chef integrates real-time inventory tracking, multimodal generative AI, long-term memory, and interactive UI components. Every capability listed below is implemented in `app/`:

### 1. Long-Term Cross-Session Memory (Vertex AI Memory Bank)
- **Tool**: `PreloadMemoryTool`
- **Memory Service**: Connected to Vertex AI Memory Bank (`agentengine://...`) via `VertexAiMemoryBankService`.
- **Extraction Callback**: An `after_agent_callback` automatically extracts user dietary requirements, food allergies, ingredient dislikes, household size, and cooking habits so that suggestions remain personalized across sessions.

### 2. Persistent Fridge Inventory Management (Google Cloud Firestore)
- **Tools**: `list_fridge_inventory`, `add_or_update_fridge_item`, `remove_fridge_item`
- **Database**: Firestore database in Datastore/Native mode storing ingredient documents with quantities, units, expiration horizons (days left), and condition notes.
- **Waste Prevention**: Sorts ingredients by expiration urgency and flags items that need immediate use.

### 3. Local Recipe Matching & Global Search
- **Tools**:
  - `find_matching_recipes`: Evaluates available fridge ingredients against a curated library of practical recipes, calculating match percentages and missing items.
  - `search_online_recipes_by_ingredient`: Queries TheMealDB API to fetch global dishes that incorporate specific target ingredients.

### 4. Interactive A2UI Surfaces
- **Callback**: `a2ui_callback` using `A2uiSchemaManager` (v0.8) with the Basic Catalog.
- **Rendering**: Emits structured A2UI card layouts (Card, Column, Row, Text, Image, Divider) for inventory overviews and recipe suggestions instead of plain text blocks.

### 5. Multimodal Generation & Public Storage (Google Cloud Storage)
- **Image Generation (`generate_dish_image`)**:
  - Model: `gemini-3.1-flash-lite-image` in the `global` region.
  - Generates photorealistic dish previews and uploads bytes directly to Google Cloud Storage (`fridge-to-table-chef-yyfvv1`), returning public HTTPS URLs for display in the chat UI.
- **Video Generation (`generate_dish_video`)**:
  - Model: `gemini-omni-flash-preview` via Google GenAI Interactions API in the `global` region.
  - Generates cinematic cooking preview clips, registers the video in the session artifacts panel (`tool_context.save_artifact`), and uploads the video to Google Cloud Storage.

### 6. Secure Recipe Math & Scaling (Agent Engine Code Executor)
- **Tool**: `run_code` / `AgentEngineSandboxCodeExecutor`
- Executes Python in an isolated Vertex AI Reasoning Engine sandbox environment to perform ingredient scaling, unit conversions, and nutritional calculations.

---

## Project Structure

```text
.
├── app/
│   ├── agent.py               # Root ADK agent configuration, instruction, tools & callbacks
│   ├── a2ui_utils.py          # A2UI v0.8 after_model_callback processor
│   ├── inventory_tools.py     # Firestore fridge inventory management tools
│   ├── recipe_tools.py        # Local recipe catalog matching logic
│   ├── mealdb_tools.py        # TheMealDB API integration for external recipe discovery
│   ├── image_tools.py         # Gemini 3.1 Flash Lite Image generation & Cloud Storage upload
│   ├── video_tools.py         # Gemini Omni Flash video generation & Cloud Storage upload
│   ├── sandbox_tools.py       # Python code sandbox execution tool
│   ├── fast_api_app.py        # FastAPI runner application for Agent Runtime
│   └── app_utils/             # Shared service providers & environment utilities
├── docs/
│   └── images/
│       └── demo.gif           # Recorded demonstration of the agent UI in action
├── frontend/                  # Lightweight FastAPI chat web proxy & A2UI renderer
│   ├── main.py                # A2A protocol client proxy
│   ├── static/index.html      # Responsive chat interface with built-in A2UI mini-renderer
│   ├── requirements.txt       # Frontend dependencies
│   └── Dockerfile             # Container configuration for Cloud Run deployment
├── agents-cli-manifest.yaml   # Agent Platform CLI configuration
└── pyproject.toml             # Python package dependencies & tool settings
```

---

## Getting Started

### Prerequisites

- Python 3.11+
- `uv` package and project manager
- Google Cloud SDK (`gcloud` CLI) authenticated with access to Vertex AI, Cloud Storage, and Firestore

### 1. Authenticate with Google Cloud

```bash
gcloud auth login
gcloud auth application-default login
gcloud config set project <YOUR_PROJECT_ID>
```

### 2. Install Dependencies

```bash
uv sync
```

### 3. Run the Agent Locally (ADK Web Playground)

To run the agent locally with long-term memory support:

```bash
uv run adk web . --port 8080 --reload_agents --memory_service_uri=agentengine://<YOUR_AGENT_ENGINE_ID>
```

### 4. Run the Web Frontend Locally

The repository includes a dedicated chat interface with a built-in A2UI renderer located in `frontend/`:

```bash
cd frontend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Set the deployed reasoning engine resource name
export AGENT_ENGINE_RESOURCE_NAME="projects/<PROJECT_NUMBER>/locations/<REGION>/reasoningEngines/<REASONING_ENGINE_ID>"
export AGENT_DIRECTORY="app"
export PORT=8080

python3 main.py
```

---

## Deployment

Deploying the agent backend to Agent Platform:

```bash
uv run agents-cli deploy --project <YOUR_PROJECT_ID>
```

Deploying the web frontend proxy to Cloud Run:

```bash
cd frontend
gcloud run deploy fridge-to-table-chef-ui \
  --source . \
  --region <REGION> \
  --project <YOUR_PROJECT_ID> \
  --allow-unauthenticated \
  --set-env-vars AGENT_ENGINE_RESOURCE_NAME="projects/<PROJECT_NUMBER>/locations/<REGION>/reasoningEngines/<REASONING_ENGINE_ID>",AGENT_DIRECTORY="app"
```
