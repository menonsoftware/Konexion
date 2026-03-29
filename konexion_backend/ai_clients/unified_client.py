import asyncio
import logging
import time
from typing import Any

import requests
from config import get_groq_config, get_ollama_config
from models.ai import AIModel
from openai import OpenAI

# Setup logging
logger = logging.getLogger(__name__)

# Get configuration
groq_config = get_groq_config()
ollama_config = get_ollama_config()


def _get_groq_client() -> OpenAI:
    """Get an OpenAI client configured for Groq."""
    if not groq_config.api_key:
        logger.warning("Groq API key not configured")
        raise Exception("Groq API key not configured, cannot initialize Groq client")
    base_url = groq_config.url.rsplit("/models", 1)[0]
    return OpenAI(api_key=groq_config.api_key, base_url=base_url)


def _get_ollama_client() -> OpenAI:
    """Get an OpenAI client configured for Ollama."""
    return OpenAI(api_key="ollama", base_url=f"{ollama_config.url}/v1")


def get_groq_models() -> dict[str, Any]:
    """Fetch available models from Groq API with proper error handling and logging."""
    if not groq_config.api_key:
        logger.warning("Groq API key not configured, returning empty model list")
        return {"models": []}

    headers = {
        "Authorization": f"Bearer {groq_config.api_key}",
        "Content-Type": "application/json",
    }

    try:
        logger.debug(f"Fetching Groq models from: {groq_config.url}")
        response = requests.get(groq_config.url, headers=headers, timeout=10)
        response.raise_for_status()

        data = response.json()
        logger.debug(f"Received {len(data.get('data', []))} models from Groq API")

        all_models = [
            {
                "client_type": "groq",
                "model_id": model["id"],
                "context_window": model["context_window"],
                "owned_by": model["owned_by"],
            }
            for model in data["data"]
            if "tts" not in model["id"].lower()
            and "whisper" not in model["id"].lower()
            and "guard" not in model["id"].lower()
        ]

        groq_models = [AIModel.model_validate(model) for model in all_models]
        logger.info(f"Successfully loaded {len(groq_models)} Groq models")
        return {"models": groq_models}

    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error fetching Groq models: {e} (Status: {e.response.status_code})")
        return {"models": []}
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error fetching Groq models: {e}")
        return {"models": []}
    except Exception as e:
        logger.error(f"Unexpected error fetching Groq models: {e}", exc_info=True)
        return {"models": []}


def get_ollama_models() -> dict[str, Any]:
    """Fetch available models from Ollama API with proper error handling and logging."""
    try:
        models_url = f"{ollama_config.url}/api/tags"

        logger.debug(f"Fetching Ollama models from: {models_url}")
        response = requests.get(models_url, timeout=ollama_config.timeout)
        response.raise_for_status()

        data = response.json()
        logger.debug(f"Received {len(data.get('models', []))} models from Ollama API")

        all_models = [
            {
                "client_type": "ollama",
                "model_id": model["name"],
                "context_window": model.get("context_length", 4096),
                "owned_by": "ollama",
            }
            for model in data.get("models", [])
        ]

        ollama_models = [AIModel.model_validate(model) for model in all_models]
        logger.info(f"Successfully loaded {len(ollama_models)} Ollama models")
        return {"models": ollama_models}

    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error connecting to Ollama at {ollama_config.url}: {e} (Status: {e.response.status_code})")
        return {"models": []}
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error connecting to Ollama at {ollama_config.url}: {e}")
        return {"models": []}
    except Exception as e:
        logger.error(f"Unexpected error fetching Ollama models: {e}", exc_info=True)
        return {"models": []}


async def stream_chat(
    websocket: Any,
    model_name: str,
    messages: list[dict[str, Any]],
    max_tokens: int | None = None,
    provider: str = "groq",
) -> None:
    """
    Stream chat response from any OpenAI-compatible provider via WebSocket.

    Args:
        websocket: WebSocket connection to send chunks
        model_name: Name of the model
        messages: List of message objects with role and content
        max_tokens: Maximum number of tokens to generate
        provider: Provider name ('groq' or 'ollama')
    """
    try:
        client = _get_groq_client() if provider == "groq" else _get_ollama_client()

        logger.info(f"Using {provider} OpenAI client for model: {model_name}")

        completion_params: dict[str, Any] = {
            "model": str(model_name),
            "messages": messages,
            "stream": True,
        }

        if max_tokens is not None:
            completion_params["max_tokens"] = max_tokens
            logger.debug(f"Using custom max_tokens: {max_tokens}")
        elif provider == "ollama":
            completion_params["max_tokens"] = ollama_config.max_tokens

        stream = client.chat.completions.create(**completion_params)

        # Batch chunks for better network efficiency
        chunk_buffer = ""
        last_send_time = time.time()
        batch_size = 20  # Characters to batch
        batch_timeout = 0.05  # 50ms max delay

        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                chunk_buffer += content

                current_time = time.time()
                should_send = (
                    len(chunk_buffer) >= batch_size
                    or current_time - last_send_time >= batch_timeout
                    or not content.strip()  # Send immediately for whitespace/punctuation
                )

                if should_send:
                    logger.debug(f"Sending batched chunk of {len(chunk_buffer)} characters")
                    await websocket.send_json({"chunk": chunk_buffer})
                    chunk_buffer = ""
                    last_send_time = current_time
                    await asyncio.sleep(0.001)  # Small delay to prevent overwhelming frontend

        # Send any remaining content
        if chunk_buffer:
            logger.debug(f"Sending final chunk of {len(chunk_buffer)} characters")
            await websocket.send_json({"chunk": chunk_buffer})

        await websocket.send_json({"finish_reason": "completed"})
        logger.info(f"Completed {provider} chat response for model: {model_name}")

    except Exception as e:
        logger.error(f"Error streaming from {provider}: {e}", exc_info=True)
        await websocket.send_json({"error": f"Error: {str(e)}"})
        await websocket.send_json({"finish_reason": "error"})
