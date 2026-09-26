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

import json
from pathlib import Path

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.apps import App
from google.adk.code_executors import AgentEngineSandboxCodeExecutor
from google.adk.models import Gemini
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.genai import types

from app.api_tools import lookup_ip_info
from app.firestore_tools import (
    add_knowledge_base_article,
    get_knowledge_base_article,
    search_knowledge_base,
)
from app.image_tools import generate_it_diagram
from app.network_tools import ping_host

# Load Agent Engine Reasoning Engine resource name from deployment_metadata.json
REASONING_ENGINE_ID = "projects/590661546420/locations/us-east1/reasoningEngines/7796775491024715776"
metadata_file = Path(__file__).parent.parent / "deployment_metadata.json"
if metadata_file.exists():
    try:
        data = json.loads(metadata_file.read_text())
        REASONING_ENGINE_ID = data.get("remote_agent_runtime_id", REASONING_ENGINE_ID)
    except Exception:
        pass


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
        query: The name of the city to get the current time for.

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


# Callback to extract and save session memories to Memory Bank
async def generate_memories_callback(callback_context: CallbackContext):
    try:
        await callback_context.add_session_to_memory()
    except Exception as e:
        print(f"Memory Bank callback skipped: {e}")
    return None


# Instantiate Agent Engine sandbox code executor with explicit project ID
code_executor = AgentEngineSandboxCodeExecutor(
    agent_engine_resource_name=REASONING_ENGINE_ID,
)
code_executor._project_id = "qwiklabs-gcp-01-411423280d35"

root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model="gemini-flash-latest",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=(
        "You are an expert General IT & Tech Support Agent. "
        "Help users diagnose, troubleshoot, and resolve IT, hardware, network, and software issues. "
        "You remember user preferences, stated facts, and allergies across sessions to personalize your responses. "
        "You can write and execute Python code in a safe sandbox to perform data analysis, math, or automation scripts. "
        "Use ping_host to test network connectivity and latency for servers, IPs, or hostnames. "
        "Use lookup_ip_info to fetch ISP, organization, and geolocation details for IP addresses or domain names. "
        "Use generate_it_diagram to generate visual network topologies or architecture diagrams. "
        "Use search_knowledge_base and get_knowledge_base_article to look up troubleshooting guides in Firestore, "
        "and add_knowledge_base_article to create or update knowledge base entries when requested."
    ),
    tools=[
        PreloadMemoryTool(),
        get_weather,
        get_current_time,
        ping_host,
        lookup_ip_info,
        generate_it_diagram,
        search_knowledge_base,
        get_knowledge_base_article,
        add_knowledge_base_article,
    ],
    after_agent_callback=generate_memories_callback,
    code_executor=code_executor,
)

app = App(
    root_agent=root_agent,
    name="app",
)


