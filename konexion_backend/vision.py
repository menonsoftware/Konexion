"""
Vision and Image Processing Module

This module handles all vision-related functionality including:
- Vision model capability detection
- Image data processing and validation
- Message formatting for vision-enabled models
- Error handling for vision-related requests
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

from config import get_vision_config

# Setup logging
logger = logging.getLogger(__name__)


class VisionProcessor:
    """Handles vision and image processing for AI models."""

    def __init__(self):
        self.vision_config = get_vision_config()
        logger.debug("VisionProcessor initialized")

    def supports_vision(self, model_name: str) -> bool:
        """
        Check if a model supports vision capabilities.

        Args:
            model_name (str): Name of the model to check

        Returns:
            bool: True if model supports vision, False otherwise
        """
        return self.vision_config.supports_vision(model_name)

    def extract_base64_from_data_url(self, data_url: str) -> Tuple[str, str]:
        """
        Extract base64 data and image type from data URL.

        Args:
            data_url (str): Data URL in format 'data:image/jpeg;base64,base64_string'

        Returns:
            Tuple[str, str]: (base64_data, image_type)
        """
        if "," not in data_url:
            logger.warning("Invalid data URL format - no comma separator found")
            return "", "image/jpeg"

        try:
            # Split at first comma to separate header from data
            header, base64_data = data_url.split(",", 1)

            # Extract image type from header (e.g., 'data:image/jpeg;base64')
            if ":" in header and "/" in header:
                image_type = header.split(":")[1].split(";")[0]
            else:
                image_type = "image/jpeg"  # Default fallback

            logger.debug(
                f"Extracted image type: {image_type}, data length: {len(base64_data)}"
            )
            return base64_data, image_type

        except Exception as e:
            logger.error(f"Error extracting data from URL: {e}")
            return "", "image/jpeg"

    def validate_images(self, images: List[Dict[str, Any]]) -> Tuple[bool, str]:
        """
        Validate image data and format.

        Args:
            images (List[Dict[str, Any]]): List of image objects

        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        if not images:
            return True, ""

        if not isinstance(images, list):
            return False, "Images must be provided as a list"

        for i, image in enumerate(images):
            if not isinstance(image, dict):
                return False, f"Image {i+1} must be an object with 'data' field"

            if not image.get("data"):
                return False, f"Image {i+1} is missing 'data' field"

            data_url = image["data"]
            if not isinstance(data_url, str):
                return False, f"Image {i+1} data must be a string"

            if not data_url.startswith("data:"):
                return (
                    False,
                    f"Image {i+1} data must be a valid data URL starting with 'data:'",
                )

        return True, ""

    def prepare_groq_vision_content(
        self, user_message: str, images: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Prepare message content for Groq vision models.

        Args:
            user_message (str): User's text message
            images (List[Dict[str, Any]]): List of image objects

        Returns:
            List[Dict[str, Any]]: Formatted content array for Groq vision API
        """
        user_content = []

        # Add text content
        if user_message.strip():
            user_content.append({"type": "text", "text": user_message})
        else:
            user_content.append({"type": "text", "text": "What's in this image?"})

        # Add images using Groq vision schema
        for image in images:
            if image.get("data"):
                base64_data, image_type = self.extract_base64_from_data_url(
                    image["data"]
                )

                if base64_data:
                    user_content.append(
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{image_type};base64,{base64_data}"
                            },
                        }
                    )
                    logger.debug(
                        f"Added image to Groq vision content: {image.get('name', 'Unknown')}"
                    )

        return user_content

    def prepare_ollama_vision_data(
        self, user_message: str, images: List[Dict[str, Any]]
    ) -> Tuple[str, List[str]]:
        """
        Prepare message and image data for Ollama vision models.

        Args:
            user_message (str): User's text message
            images (List[Dict[str, Any]]): List of image objects

        Returns:
            Tuple[str, List[str]]: (text_content, base64_images_list)
        """
        # Prepare text content
        text_content = user_message.strip() or "What's in this image?"

        # Extract base64 images for Ollama format
        images_list = []
        for image in images:
            if image.get("data"):
                base64_data, _ = self.extract_base64_from_data_url(image["data"])
                if base64_data:
                    images_list.append(base64_data)
                    logger.debug(
                        f"Added image to Ollama vision data: {image.get('name', 'Unknown')}"
                    )

        return text_content, images_list

    def format_vision_message(
        self,
        role: str,
        user_message: str,
        images: List[Dict[str, Any]],
        model_format: str = "groq",
    ) -> Dict[str, Any]:
        """
        Format a complete message object for vision models.

        Args:
            role (str): Message role (e.g., "user", "system")
            user_message (str): Text content of the message
            images (List[Dict[str, Any]]): List of image objects
            model_format (str): Target format ("groq" or "ollama")

        Returns:
            Dict[str, Any]: Formatted message object
        """
        if model_format.lower() == "groq":
            content = self.prepare_groq_vision_content(user_message, images)
            return {"role": role, "content": content}
        elif model_format.lower() == "ollama":
            # For Ollama, we return separate text and images
            text_content, images_list = self.prepare_ollama_vision_data(
                user_message, images
            )
            return {
                "role": role,
                "content": text_content,
                "_images": images_list,  # Special field for Ollama processing
            }
        else:
            raise ValueError(f"Unsupported model format: {model_format}")

    def create_vision_error_message(self, model_name: str, image_count: int) -> str:
        """
        Create a user-friendly error message for vision capability issues.

        Args:
            model_name (str): Name of the model that doesn't support vision
            image_count (int): Number of images the user tried to send

        Returns:
            str: Formatted error message
        """
        vision_models = ", ".join(
            self.vision_config.models_list[:5]
        )  # Show first 5 models
        if len(self.vision_config.models_list) > 5:
            vision_models += "..."

        return (
            f"The model '{model_name}' does not support image analysis. "
            f"You attempted to send {image_count} image{'s' if image_count != 1 else ''}. "
            f"Please select a vision-capable model (like {vision_models}) "
            f"or remove the images to proceed with text-only chat."
        )

    def process_vision_request(
        self, model_name: str, user_message: str, images: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Process a vision request and return the appropriate response.

        Args:
            model_name (str): Name of the target model
            user_message (str): User's text message
            images (List[Dict[str, Any]]): List of image objects

        Returns:
            Dict[str, Any]: Processing result with status and data
        """
        result = {
            "success": False,
            "error": None,
            "data": None,
            "supports_vision": False,
            "image_count": len(images) if images else 0,
        }

        try:
            # Validate images first
            if images:
                is_valid, error_msg = self.validate_images(images)
                if not is_valid:
                    result["error"] = f"Image validation failed: {error_msg}"
                    return result

            # Check vision support
            supports_vision = self.supports_vision(model_name)
            result["supports_vision"] = supports_vision

            if images and not supports_vision:
                # Model doesn't support vision but images were provided
                result["error"] = self.create_vision_error_message(
                    model_name, len(images)
                )
                logger.warning(
                    f"Model {model_name} does not support vision. User attempted to send {len(images)} images."
                )
                return result

            elif images and supports_vision:
                # Model supports vision and images were provided
                logger.info(
                    f"Processing {len(images)} images for vision-enabled model: {model_name}"
                )
                result["success"] = True
                result["data"] = {"has_images": True, "message_type": "vision"}
                return result

            else:
                # No images, regular text message
                result["success"] = True
                result["data"] = {"has_images": False, "message_type": "text"}
                return result

        except Exception as e:
            logger.error(f"Error processing vision request: {e}", exc_info=True)
            result["error"] = f"Internal error processing vision request: {str(e)}"
            return result


# Global vision processor instance
vision_processor = VisionProcessor()


# Convenience functions for backward compatibility and ease of use
def supports_vision(model_name: str) -> bool:
    """Check if a model supports vision capabilities."""
    return vision_processor.supports_vision(model_name)


def prepare_vision_message(
    role: str,
    user_message: str,
    images: List[Dict[str, Any]],
    model_format: str = "groq",
) -> Dict[str, Any]:
    """Format a message for vision models."""
    return vision_processor.format_vision_message(
        role, user_message, images, model_format
    )


def process_vision_request(
    model_name: str, user_message: str, images: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Process a vision request and return appropriate response."""
    return vision_processor.process_vision_request(model_name, user_message, images)


def create_vision_error_message(model_name: str, image_count: int) -> str:
    """Create a user-friendly error message for vision issues."""
    return vision_processor.create_vision_error_message(model_name, image_count)
