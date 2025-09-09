import asyncio
import json
import logging
import time
from collections.abc import Generator
from typing import Any

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


def get_ollama_models() -> dict[str, Any]:
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
        logger.error(f"HTTP error connecting to Ollama at {ollama_config.url}: {e} (Status: {e.response.status_code})")
        return {"models": []}
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error connecting to Ollama at {ollama_config.url}: {e}")
        return {"models": []}
    except Exception as e:
        logger.error(f"Unexpected error fetching Ollama models: {e}", exc_info=True)
        return {"models": []}


def get_ollama_client() -> dict[str, Any]:
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


def generate_ollama_response(model_name: str, prompt: str, stream: bool = False) -> dict[str, Any]:
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
        response = requests.post(client_config["generate_url"], json=payload, timeout=ollama_config.timeout)
        response.raise_for_status()
        logger.debug(f"Successfully generated response from Ollama model: {model_name}")
        return response.json()  # type: ignore[no-any-return]

    except requests.exceptions.RequestException as e:
        logger.error(f"Error generating response from Ollama: {e}")
        return {"error": str(e)}


def stream_ollama_chat(
    model_name: str, messages: list[dict[str, Any]], max_tokens: int | None = None
) -> Generator[str, None, None]:
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
            # Extract text and images from the complex content structure (Groq format)
            text_content = ""
            temp_images = []

            for content_item in message["content"]:
                if content_item.get("type") == "text":
                    text_content += content_item.get("text", "")
                elif content_item.get("type") == "image_url":
                    # Extract image URL from Groq format
                    image_url = content_item.get("image_url", {}).get("url", "")
                    if image_url:
                        temp_images.append({"data": image_url})

            # Use vision processor to handle Ollama format conversion
            if temp_images:
                ollama_text, ollama_images = vision_processor.prepare_ollama_vision_data(text_content, temp_images)
                images_list.extend(ollama_images)
                processed_messages.append({"role": message["role"], "content": ollama_text})
                logger.debug(f"Processed vision message: {len(temp_images)} images, text length: {len(text_content)}")
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

    # Add images to the last user message if present (Ollama chat format)
    if images_list and processed_messages:
        # Find the last user message and add images to it
        for i in range(len(processed_messages) - 1, -1, -1):
            if processed_messages[i].get("role") == "user":
                processed_messages[i]["images"] = images_list
                logger.info(f"Adding {len(images_list)} images to user message for Ollama model: {model_name}")
                # Log the actual image data lengths for debugging
                for j, img in enumerate(images_list):
                    logger.info(f"Image {j+1}: length={len(img)}, starts_with={img[:20] if img else 'EMPTY'}")
                break
        else:
            logger.warning("No user message found to attach images to")
    elif images_list:
        logger.warning("Images provided but no processed messages found")
    else:
        logger.debug("No images found in processed messages for Ollama request")

    try:
        logger.debug(f"Starting chat stream with Ollama model: {model_name}")
        logger.debug(f"Processed messages count: {len(processed_messages)}")
        logger.debug(f"Images count for Ollama: {len(images_list)}")

        # Log the payload structure (without full image data to avoid log spam)
        payload_for_logging = payload.copy()
        payload_for_logging["messages"] = []
        for msg in payload["messages"]:  # type: ignore[attr-defined]
            msg_copy = msg.copy()
            if "images" in msg_copy:
                msg_copy["images"] = [
                    f"<base64_image_{i+1}_len_{len(img)}>" for i, img in enumerate(msg_copy["images"])
                ]
            payload_for_logging["messages"].append(msg_copy)  # type: ignore[attr-defined]
        logger.debug(f"Ollama payload structure: {json.dumps(payload_for_logging, indent=2)}")

        # CRITICAL DEBUG: Log the actual HTTP request details
        logger.info(f"Sending POST to: {client_config['chat_url']}")
        logger.info(f"Payload keys: {list(payload.keys())}")

        # Check if any message has images
        has_images = any("images" in msg for msg in payload["messages"])  # type: ignore[attr-defined]
        if has_images:
            total_images = sum(len(msg.get("images", [])) for msg in payload["messages"])  # type: ignore[attr-defined,misc]
            logger.info(f"Total images in messages: {total_images}")
        else:
            logger.info("No images found in any message")

        response = requests.post(
            client_config["chat_url"],
            json=payload,
            timeout=ollama_config.timeout,
            stream=True,
        )
        response.raise_for_status()

        # Log the response status
        logger.info(f"Ollama API responded with status {response.status_code}")

        chunk_count = 0
        total_content = ""
        for line in response.iter_lines():
            if line:
                try:
                    chunk_data = line.decode("utf-8")
                    chunk_json = json.loads(chunk_data)

                    # Log the full chunk for debugging
                    logger.debug(f"Ollama chunk {chunk_count + 1}: {chunk_json}")

                    if "message" in chunk_json and "content" in chunk_json["message"]:
                        content = chunk_json["message"]["content"]
                        if content:
                            chunk_count += 1
                            total_content += content
                            logger.debug(f"Chunk {chunk_count} content: '{content}'")
                            yield content

                    # Check if this is the final chunk
                    if chunk_json.get("done", False):
                        logger.info(
                            f"Response preview: '{total_content[:200]}{'...' if len(total_content) > 200 else ''}'"
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
        logger.error(f"Request details - URL: {client_config['chat_url']}")
        logger.error(f"Payload keys: {list(payload.keys())}")
        if "images" in payload:
            logger.error(f"Images count in payload: {len(payload['images'])}")  # type: ignore[arg-type]
        yield f"Error: {str(e)}"


async def stream_ollama_chat_websocket(
    websocket: Any, model_name: str, messages: list[dict[str, Any]], max_tokens: int | None = None
) -> None:
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
        batch_size = 20  # Characters to batch
        batch_timeout = 0.05  # 50ms max delay

        for chunk in stream_ollama_chat(model_name, messages, max_tokens):
            if chunk:  # Only process non-empty chunks
                chunk_buffer += chunk

                current_time = time.time()
                should_send = (
                    len(chunk_buffer) >= batch_size
                    or current_time - last_send_time >= batch_timeout
                    or not chunk.strip()  # Send immediately for whitespace/punctuation
                )

                if should_send:
                    logger.debug(f"Sending Ollama batched chunk of {len(chunk_buffer)} characters")
                    await websocket.send_json({"chunk": chunk_buffer})
                    chunk_buffer = ""
                    last_send_time = current_time
                    await asyncio.sleep(0.001)  # Small delay to prevent overwhelming frontend

        # Send any remaining content
        if chunk_buffer:
            logger.debug(f"Sending final Ollama chunk of {len(chunk_buffer)} characters")
            await websocket.send_json({"chunk": chunk_buffer})

        await websocket.send_json({"finish_reason": "completed"})
        logger.info(f"Completed Ollama chat response for model: {model_name}")

    except Exception as e:
        logger.error(f"Error streaming from Ollama: {e}", exc_info=True)
        await websocket.send_json({"error": f"Error: {str(e)}"})
        await websocket.send_json({"finish_reason": "error"})
