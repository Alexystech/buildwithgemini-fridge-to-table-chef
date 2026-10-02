"""Sandbox code execution tool using AgentEngineSandboxCodeExecutor."""

import json
from typing import Any
import vertexai

PROJECT_ID = "qwiklabs-gcp-04-e7977ef4863a"
SANDBOX_RESOURCE_NAME = (
    "projects/460274758047/locations/us-east1/reasoningEngines/104428315871281152"
    "/sandboxEnvironments/4773191082408148992"
)


def run_code(code: str) -> dict[str, Any]:
    """Execute Python code safely inside the Agent Platform sandbox environment.

    Useful for complex portion scaling, unit conversions, and nutritional/calorie calculations.

    Args:
        code: Python code to execute in the sandbox. Print output to stdout using print().

    Returns:
        A dictionary containing stdout, stderr, and exit status.
    """
    try:
        client = vertexai.Client(project=PROJECT_ID, location="us-east1")
        response = client.agent_engines.sandboxes.execute_code(
            name=SANDBOX_RESOURCE_NAME,
            input_data={"code": code},
        )
        stdout = ""
        stderr = ""
        for output in response.outputs:
            if output.mime_type == "application/json":
                data = json.loads(output.data.decode("utf-8"))
                stdout += data.get("msg_out", "")
                stderr += data.get("msg_err", "")
            else:
                stdout += output.data.decode("utf-8", errors="replace")

        return {
            "stdout": stdout.strip(),
            "stderr": stderr.strip(),
            "status": "success" if not stderr else "error",
        }
    except Exception as e:
        return {
            "stdout": "",
            "stderr": str(e),
            "status": "error",
        }
