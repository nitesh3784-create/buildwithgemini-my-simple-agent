# Copyright 2026 Google LLC
# Image generation tool for General IT & Tech Support Agent.

import uuid
from google import genai
from google.cloud import storage
from google.genai import types
from google.adk.tools import ToolContext

BUCKET_NAME = "it-support-assets-qwiklabs-gcp-01-411423280d35"
PROJECT_ID = "qwiklabs-gcp-01-411423280d35"


async def generate_it_diagram(
    prompt: str,
    tool_context: ToolContext,
) -> str:
    """Generates an IT diagram, network architecture, or technical illustration to assist in troubleshooting.

    Args:
        prompt: Description of the diagram or technical illustration to generate (e.g. 'Network topology showing router, firewall, switch, and workstations').
        tool_context: ADK ToolContext used to save session artifacts for Playground display.

    Returns:
        The public HTTPS URL of the generated image stored in Cloud Storage.
    """
    try:
        # Initialize Vertex AI client targeting global region
        client = genai.Client(vertexai=True, project=PROJECT_ID, location="global")

        # Request image generation using gemini-3.1-flash-lite-image
        response = client.models.generate_content(
            model="gemini-3.1-flash-lite-image",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=["TEXT", "IMAGE"],
            ),
        )

        image_bytes = None
        if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if part.inline_data:
                    image_bytes = part.inline_data.data
                    break

        if not image_bytes:
            return "Error: Model response did not contain image data."

        filename = f"it_diagram_{uuid.uuid4().hex[:8]}.png"

        # 1. Save artifact with tool_context.save_artifact for Playground display
        try:
            artifact_part = types.Part.from_bytes(data=image_bytes, mime_type="image/png")
            await tool_context.save_artifact(filename=filename, artifact=artifact_part)
        except Exception as err:
            # Handle if artifact service is not bound in one-off local CLI runs
            pass

        # 2. Upload same image bytes to public Cloud Storage bucket
        storage_client = storage.Client(project=PROJECT_ID)
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(filename)
        blob.upload_from_string(image_bytes, content_type="image/png")

        public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{filename}"
        return public_url
    except Exception as e:
        return f"Error generating IT diagram image: {str(e)}"
