"""
Model Registry Module

This module provides a centralized model registry for caching and managing
AI model data from different providers (Groq, Ollama).
"""

import logging
from typing import Any

from konexion_backend.services.unified_ai_service import get_groq_models, get_ollama_models, get_open_router_models

# Setup logging
logger = logging.getLogger(__name__)


class ModelRegistry:
    """
    Caches model data to avoid repeated API calls and provides efficient model lookup.

    This class maintains separate caches for Groq and Ollama models, along with
    combined model lists and model ID sets for fast lookups.
    """

    def __init__(self) -> None:
        """Initialize empty model registry cache."""
        self._groq_models: dict[str, Any] | None = None
        self._ollama_models: dict[str, Any] | None = None
        self._open_router_models: dict[str, Any] | None = None
        self._all_models: list[Any] | None = None
        self._groq_model_ids: set[str] | None = None
        self._ollama_model_ids: set[str] | None = None
        self._open_router_model_ids: set[str] | None = None
        logger.debug("ModelRegistry initialized")

    def get_groq_models(self) -> dict[str, Any]:
        """
        Get Groq models with caching.

        Returns:
            Dict[str, Any]: Groq models data with 'models' key containing list of models
        """
        if self._groq_models is None:
            logger.debug("Loading Groq models from API")
            self._groq_models = get_groq_models()
            self._groq_model_ids = {model.model_id for model in self._groq_models.get("models", [])}
            logger.info(f"Cached {len(self._groq_model_ids)} Groq models")
        return self._groq_models

    def get_ollama_models(self) -> dict[str, Any]:
        """
        Get Ollama models with caching.

        Returns:
            Dict[str, Any]: Ollama models data with 'models' key containing list of models
        """
        if self._ollama_models is None:
            logger.debug("Loading Ollama models from API")
            self._ollama_models = get_ollama_models()
            self._ollama_model_ids = {model.model_id for model in self._ollama_models.get("models", [])}
            logger.info(f"Cached {len(self._ollama_model_ids)} Ollama models")
        return self._ollama_models

    def get_open_router_models(self) -> dict[str, Any]:
        """
        Get Open Router models with caching.

        Returns:
            Dict[str, Any]: Open Router models data with 'models' key containing list of models
        """
        if self._open_router_models is None:
            logger.debug("Loading Open Router models from API")
            self._open_router_models = get_open_router_models()
            self._open_router_model_ids = {model.model_id for model in self._open_router_models.get("models", [])}
            logger.info(f"Cached {len(self._open_router_model_ids)} Open Router models")
        return self._open_router_models

    def get_all_models(self) -> list[Any]:
        """
        Get all models combined with caching.

        Returns:
            List[Any]: Combined list of all models from both providers
        """
        if self._all_models is None:
            logger.debug("Building combined model list")
            groq_models = self.get_groq_models()
            ollama_models = self.get_ollama_models()
            open_router_models = self.get_open_router_models()
            self._all_models = groq_models["models"] + ollama_models["models"] + open_router_models["models"]
            logger.info(
                f"Built combined model list with {len(self._all_models) if self._all_models else 0} total models"
            )
        return self._all_models or []

    def is_groq_model(self, model_id: str) -> bool:
        """
        Check if model is a Groq model with fast O(1) lookup.

        Args:
            model_id (str): Model identifier to check

        Returns:
            bool: True if model is from Groq, False otherwise
        """
        if self._groq_model_ids is None:
            self.get_groq_models()
        return model_id in (self._groq_model_ids or set())

    def is_ollama_model(self, model_id: str) -> bool:
        """
        Check if model is an Ollama model with fast O(1) lookup.

        Args:
            model_id (str): Model identifier to check

        Returns:
            bool: True if model is from Ollama, False otherwise
        """
        if self._ollama_model_ids is None:
            self.get_ollama_models()
        return model_id in (self._ollama_model_ids or set())
    
    def is_open_router_model(self, model_id: str) -> bool:
        """
        Check if model is an Open Router model with fast O(1) lookup.

        Args:
            model_id (str): Model identifier to check

        Returns:
            bool: True if model is from Open Router, False otherwise
        """
        if self._open_router_model_ids is None:
            self.get_open_router_models()
        return model_id in (self._open_router_model_ids or set())

    def get_model_provider(self, model_id: str) -> str | None:
        """
        Get the provider name for a given model.

        Args:
            model_id (str): Model identifier to check

        Returns:
            Optional[str]: 'groq', 'ollama', or None if model not found
        """
        if self.is_groq_model(model_id):
            return "groq"
        elif self.is_ollama_model(model_id):
            return "ollama"
        elif self.is_open_router_model(model_id):
            return "open_router"
        else:
            return None

    def get_model_count(self) -> dict[str, int]:
        """
        Get count of models by provider.

        Returns:
            Dict[str, int]: Dictionary with provider names and model counts
        """
        groq_models = self.get_groq_models()
        ollama_models = self.get_ollama_models()
        open_router_models = self.get_open_router_models()
        return {
            "groq": len(groq_models.get("models", [])),
            "ollama": len(ollama_models.get("models", [])),
            "open_router": len(open_router_models.get("models", [])),
            "total": len(self.get_all_models()),
        }

    def refresh_cache(self) -> None:
        """
        Clear all cached data to force refresh on next access.

        This method resets all internal caches, forcing the next access
        to fetch fresh data from the AI provider APIs.
        """
        logger.info("Refreshing model registry cache")
        self._groq_models = None
        self._ollama_models = None
        self._all_models = None
        self._groq_model_ids = None
        self._ollama_model_ids = None
        self._open_router_models = None
        self._open_router_model_ids = None
        logger.debug("Model registry cache cleared")

    def is_cache_loaded(self) -> dict[str, bool]:
        """
        Check which caches are currently loaded.

        Returns:
            Dict[str, bool]: Status of each cache (loaded/not loaded)
        """
        return {
            "groq_models": self._groq_models is not None,
            "ollama_models": self._ollama_models is not None,
            "all_models": self._all_models is not None,
            "groq_model_ids": self._groq_model_ids is not None,
            "ollama_model_ids": self._ollama_model_ids is not None,
            "open_router_models": self._open_router_models is not None,
            "open_router_model_ids": self._open_router_model_ids is not None,
        }

    async def preload_models(self) -> dict[str, int]:
        """
        Preload all models to warm up the cache.

        Returns:
            Dict[str, int]: Model count summary after preloading
        """
        logger.info("Preloading model registry cache")
        try:
            # Load all models to populate cache
            # all_models = self.get_all_models()
            counts = self.get_model_count()
            logger.info(
                f"Successfully preloaded {counts['total']} models ({counts['groq']} Groq, {counts['ollama']} Ollama)"
            )
            return counts
        except Exception as e:
            logger.error(f"Failed to preload models: {e}", exc_info=True)
            return {"groq": 0, "ollama": 0, "open_router": 0, "total": 0}


# Global model registry instance
model_registry = ModelRegistry()


# Convenience functions for backward compatibility
def get_cached_groq_models() -> dict[str, Any]:
    """Get cached Groq models."""
    return model_registry.get_groq_models()


def get_cached_ollama_models() -> dict[str, Any]:
    """Get cached Ollama models."""
    return model_registry.get_ollama_models()


def get_cached_open_router_models() -> dict[str, Any]:
    """Get cached Open Router models."""
    return model_registry.get_open_router_models()

def get_cached_all_models() -> list[Any]:
    """Get all cached models."""
    return model_registry.get_all_models()


def is_groq_model(model_id: str) -> bool:
    """Check if model is from Groq."""
    return model_registry.is_groq_model(model_id)


def is_ollama_model(model_id: str) -> bool:
    """Check if model is from Ollama."""
    return model_registry.is_ollama_model(model_id)


def is_open_router_model(model_id: str) -> bool:
    """Check if model is from Open Router."""
    return model_registry.is_open_router_model(model_id)

def get_model_provider(model_id: str) -> str | None:
    """Get provider name for model."""
    return model_registry.get_model_provider(model_id)


def get_model_count() -> dict[str, int]:
    """Get provider name for model."""
    return model_registry.get_model_count()

def refresh_model_cache() -> None:
    """Refresh the model cache."""
    model_registry.refresh_cache()

def is_cache_loaded() -> dict[str, bool]:
    """Check if cache is loaded."""
    return model_registry.is_cache_loaded()

def preload_models() -> dict[str, int]:
    """Preload models."""
    return model_registry.preload_models()
