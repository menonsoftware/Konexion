import asyncio
import json
import logging
import time

import requests

from config import get_ollama_config
from models.ai import AIModel
from vision import VisionProcessor

# Setup logging
logger = logging.getLogger(__name__)

# Get configuration
ollama_config = get_ollama_config()

# Initialize vision processor
vision_processor = VisionProcessor()


def get_ollama_models():
    """
    Fetch available models from Ollama running on a network URL.

    Returns:
        List of models compatible with AIModel structure
    """
    try:
        # Ollama API endpoint for listing models
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
                # Ollama doesn't provide context_window in the API response
                # Default to a reasonable value, can be overridden per model
                "context_window": model.get("context_length", 4096),
                "owned_by": "ollama",
            }
            for model in data.get("models", [])
        ]

        ollama_models = [AIModel.model_validate(model) for model in all_models]
        logger.info(f"Successfully loaded {len(ollama_models)} Ollama models")
        return {"models": ollama_models}

    except requests.exceptions.HTTPError as e:
        logger.error(
            f"HTTP error connecting to Ollama at {ollama_config.url}: {e} (Status: {e.response.status_code})"
        )
        return {"models": []}
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error connecting to Ollama at {ollama_config.url}: {e}")
        return {"models": []}
    except Exception as e:
        logger.error(f"Unexpected error fetching Ollama models: {e}", exc_info=True)
        return {"models": []}


def get_ollama_client():
    """
    Get Ollama client configuration for making requests.

    Returns:
        dict: Configuration for Ollama requests
    """
    return {
        "base_url": ollama_config.url,
        "generate_url": f"{ollama_config.url}/api/generate",
        "chat_url": f"{ollama_config.url}/api/chat",
    }


def generate_ollama_response(model_name, prompt, stream=False):
    """
    Generate response from Ollama model.

    Args:
        model_name (str): Name of the Ollama model
        prompt (str): Input prompt
        stream (bool): Whether to stream the response

    Returns:
        Response from Ollama API
    """
    client_config = get_ollama_client()

    payload = {
        "model": model_name,
        "prompt": prompt,
        "stream": stream,
        "options": {"num_predict": ollama_config.max_tokens},
    }

    try:
        response = requests.post(
            client_config["generate_url"], json=payload, timeout=ollama_config.timeout
        )
        response.raise_for_status()
        logger.debug(f"Successfully generated response from Ollama model: {model_name}")
        return response.json()

    except requests.exceptions.RequestException as e:
        logger.error(f"Error generating response from Ollama: {e}")
        return {"error": str(e)}


def stream_ollama_chat(model_name, messages, max_tokens=None):
    """
    Stream chat response from Ollama model.

    Args:
        model_name (str): Name of the Ollama model
        messages (list): List of message objects with role and content
        max_tokens (int, optional): Maximum number of tokens to generate

    Yields:
        Generator of response chunks
    """
    client_config = get_ollama_client()

    # Use provided max_tokens or fall back to config default
    tokens_limit = max_tokens if max_tokens is not None else ollama_config.max_tokens

    # Process messages to handle vision content using vision module
    processed_messages = []
    images_list = []

    for message in messages:
        if isinstance(message.get("content"), list):
            # Handle vision content using vision processor
            # Extract text and images from the complex content structure
            text_content = ""
            temp_images = []

            for content_item in message["content"]:
                if content_item.get("type") == "text":
                    text_content += content_item.get("text", "")
                elif content_item.get("type") == "image_url":
                    # Convert to simple image format for vision processor
                    image_url = content_item.get("image_url", {}).get("url", "")
                    if image_url:
                        temp_images.append({"data": image_url})

            # Use vision processor to handle Ollama format conversion
            if temp_images:
                ollama_text, ollama_images = (
                    vision_processor.prepare_ollama_vision_data(
                        text_content, temp_images
                    )
                )
                images_list.extend(ollama_images)
                processed_messages.append(
                    {"role": message["role"], "content": ollama_text}
                )
            else:
                processed_messages.append(
                    {
                        "role": message["role"],
                        "content": text_content.strip() or "What's in this image?",
                    }
                )
        else:
            # Regular text message
            processed_messages.append(message)

    payload = {
        "model": model_name,
        "messages": processed_messages,
        "stream": True,
        "options": {"num_predict": tokens_limit},
    }

    # Add images to payload if present (Ollama format)
    if images_list:
        payload["images"] = images_list
        logger.info(
            f"Adding {len(images_list)} images to Ollama request for model: {model_name}"
        )

    try:
        logger.debug(f"Starting chat stream with Ollama model: {model_name}")
        logger.debug(f"Payload: {json.dumps(payload, indent=2)}")
        response = requests.post(
            client_config["chat_url"],
            json=payload,
            timeout=ollama_config.timeout,
            stream=True,
        )
        response.raise_for_status()

        chunk_count = 0
        for line in response.iter_lines():
            if line:
                try:
                    chunk_data = line.decode("utf-8")
                    chunk_json = json.loads(chunk_data)

                    if "message" in chunk_json and "content" in chunk_json["message"]:
                        content = chunk_json["message"]["content"]
                        if content:
                            chunk_count += 1
                            yield content

                    # Check if this is the final chunk
                    if chunk_json.get("done", False):
                        logger.debug(
                            f"Completed Ollama chat stream with {chunk_count} chunks"
                        )
                        break

                except (json.JSONDecodeError, KeyError) as e:
                    logger.warning(f"Error parsing Ollama response chunk: {e}")
                    continue

    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error streaming from Ollama: {e}")
        logger.error(f"Response status: {e.response.status_code}")
        logger.error(f"Response content: {e.response.text}")
        yield f"Error: HTTP {e.response.status_code} - {e.response.text}"
    except requests.exceptions.RequestException as e:
        logger.error(f"Error streaming from Ollama: {e}")
        yield f"Error: {str(e)}"


async def stream_ollama_chat_websocket(
    websocket, model_name, messages, max_tokens=None
):
    """
    Stream chat response from Ollama model with WebSocket integration.

    Args:
        websocket: WebSocket connection to send chunks
        model_name (str): Name of the Ollama model
        messages (list): List of message objects with role and content
        max_tokens (int, optional): Maximum number of tokens to generate
    """
    try:
        logger.info(f"Using Ollama client for model: {model_name}")

        chunk_buffer = ""
        last_send_time = time.time()
        BATCH_SIZE = 20  # Characters to batch
        BATCH_TIMEOUT = 0.05  # 50ms max delay

        for chunk in stream_ollama_chat(model_name, messages, max_tokens):
            if chunk:  # Only process non-empty chunks
                chunk_buffer += chunk

                current_time = time.time()
                should_send = (
                    len(chunk_buffer) >= BATCH_SIZE
                    or current_time - last_send_time >= BATCH_TIMEOUT
                    or not chunk.strip()  # Send immediately for whitespace/punctuation
                )

                if should_send:
                    logger.debug(
                        f"Sending Ollama batched chunk of {len(chunk_buffer)} characters"
                    )
                    await websocket.send_json({"chunk": chunk_buffer})
                    chunk_buffer = ""
                    last_send_time = current_time
                    await asyncio.sleep(
                        0.001
                    )  # Small delay to prevent overwhelming frontend

        # Send any remaining content
        if chunk_buffer:
            logger.debug(
                f"Sending final Ollama chunk of {len(chunk_buffer)} characters"
            )
            await websocket.send_json({"chunk": chunk_buffer})

        await websocket.send_json({"finish_reason": "completed"})
        logger.info(f"Completed Ollama chat response for model: {model_name}")

    except Exception as e:
        logger.error(f"Error streaming from Ollama: {e}", exc_info=True)
        await websocket.send_json({"error": f"Error: {str(e)}"})
        await websocket.send_json({"finish_reason": "error"})
