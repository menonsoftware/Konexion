"""
Configuration module for the Konexion backend application.

Loads all environment variables using Pydantic Settings for type safety and validation.
"""

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):  # type: ignore[misc]
    """Main application settings that loads all environment variables."""

    # Groq Configuration
    groq_api_key: str | None = Field(default=None, description="Groq API key for authentication")
    groq_url: str = Field(default="https://api.groq.com/openai/v1/models", description="Groq API base URL")

    # Ollama Configuration
    ollama_url: str = Field(default="http://localhost:11434", description="Ollama service URL")
    ollama_timeout: int = Field(default=30, description="Request timeout in seconds")
    ollama_max_tokens: int = Field(default=2048, description="Maximum number of tokens to generate in responses")

    # Server Configuration
    server_host: str = Field(
        default="0.0.0.0",
        description="Server host",  # nosec B104
    )
    server_port: int = Field(default=8000, description="Server port")
    debug: bool = Field(default=False, description="Debug mode")
    reload: bool = Field(default=False, description="Auto-reload on code changes")
    workers: int = Field(default=1, description="Number of worker processes for the server")

    # Database Configuration
    database_url: str | None = Field(default=None, description="Database connection URL")
    database_max_connections: int = Field(default=10, description="Maximum database connections")

    # Security Configuration
    secret_key: str = Field(
        default="change-me-to-a-random-32-char-secret!!", description="Secret key for JWT and sessions (min 32 chars)"
    )
    jwt_algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(default=15, description="Access token expiration time in minutes")
    refresh_token_expire_days: int = Field(default=7, description="Refresh token expiration time in days")
    cors_origins: str = Field(default="*", description="Comma-separated list of allowed CORS origins")

    # OAuth Provider Configuration
    google_client_id: str | None = Field(default=None, description="Google OAuth2 client ID")
    google_client_secret: str | None = Field(default=None, description="Google OAuth2 client secret")
    google_redirect_uri: str = Field(
        default="http://localhost:8000/api/auth/google/callback", description="Google OAuth2 redirect URI"
    )

    microsoft_client_id: str | None = Field(default=None, description="Microsoft OAuth2 client ID")
    microsoft_client_secret: str | None = Field(default=None, description="Microsoft OAuth2 client secret")
    microsoft_tenant_id: str = Field(
        default="common", description="Microsoft tenant ID (use 'common' for multi-tenant)"
    )
    microsoft_redirect_uri: str = Field(
        default="http://localhost:8000/api/auth/microsoft/callback", description="Microsoft OAuth2 redirect URI"
    )

    # Frontend & Auth Shared Config
    frontend_url: str = Field(
        default="http://localhost:5173", description="Frontend application URL for post-auth redirects"
    )
    enabled_providers: str = Field(
        default="google,microsoft", description="Comma-separated list of enabled OAuth providers"
    )

    @field_validator("secret_key")
    @classmethod
    def secret_key_min_length(cls, v: str) -> str:
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        return v

    # Logging Configuration
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log message format",
    )
    log_file: str | None = Field(default=None, description="Log file path")

    # Vision Models Configuration
    vision_models: str = Field(
        default="gemma3,llava,scout,maverick,vision,llama-3.2-11b-vision-preview,llama-3.2-90b-vision-preview",
        description="Comma-separated list of model keywords that support vision capabilities",
    )

    # Environment
    environment: str = Field(default="development", description="Application environment")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore",
    }

    # Model Context Protocol (MCP) Configuration

    mcp_url: str = Field(default="http://localhost:8080/mcp", description="MCP service URL")
    mcp_enabled: bool = Field(default=False, description="Whether to enable Model Context Protocol (MCP)")
    mcp_gateway_timeout: int = Field(default=30, description="Timeout for MCP gateway requests in seconds")

    postgres_host: str = Field(default="localhost", description="PostgreSQL host")
    postgres_port: int = Field(default=5432, description="PostgreSQL port")
    postgres_user: str = Field(default="postgres", description="PostgreSQL user")
    postgres_password: str = Field(default="password", description="PostgreSQL password")
    postgres_db: str = Field(default="konexion_db", description="PostgreSQL database name")

    @property
    def cors_origins_list(self) -> list[str]:
        """Convert CORS origins string to list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    @property
    def enabled_providers_list(self) -> list[str]:
        """Convert enabled providers string to list."""
        return [p.strip().lower() for p in self.enabled_providers.split(",") if p.strip()]

    @property
    def vision_models_list(self) -> list[str]:
        """Convert vision models string to list."""
        return [model.strip().lower() for model in self.vision_models.split(",")]


class GroqConfig:
    """Groq configuration accessor."""

    def __init__(self, settings: Settings):
        self._settings = settings

    @property
    def api_key(self) -> str | None:
        return self._settings.groq_api_key

    @property
    def url(self) -> str:
        return self._settings.groq_url


class OllamaConfig:
    """Ollama configuration accessor."""

    def __init__(self, settings: Settings):
        self._settings = settings

    @property
    def url(self) -> str:
        return self._settings.ollama_url

    @property
    def timeout(self) -> int:
        return self._settings.ollama_timeout

    @property
    def max_tokens(self) -> int:
        return self._settings.ollama_max_tokens


class ServerConfig:
    """Server configuration accessor."""

    def __init__(self, settings: Settings):
        self._settings = settings

    @property
    def host(self) -> str:
        return self._settings.server_host

    @property
    def port(self) -> int:
        return self._settings.server_port

    @property
    def debug(self) -> bool:
        return self._settings.debug

    @property
    def reload(self) -> bool:
        return self._settings.reload

    @property
    def workers(self) -> int:
        return self._settings.workers


class DatabaseConfig:
    """Database configuration accessor."""

    def __init__(self, settings: Settings):
        self._settings = settings

    @property
    def url(self) -> str | None:
        return self._settings.database_url

    @property
    def max_connections(self) -> int:
        return self._settings.database_max_connections


class SecurityConfig:
    """Security configuration accessor."""

    def __init__(self, settings: Settings):
        self._settings = settings

    @property
    def secret_key(self) -> str | None:
        return self._settings.secret_key

    @property
    def algorithm(self) -> str:
        return self._settings.jwt_algorithm

    @property
    def access_token_expire_minutes(self) -> int:
        return self._settings.access_token_expire_minutes

    @property
    def refresh_token_expire_days(self) -> int:
        return self._settings.refresh_token_expire_days

    @property
    def cors_origins(self) -> str:
        return self._settings.cors_origins

    @property
    def cors_origins_list(self) -> list[str]:
        return self._settings.cors_origins_list


class LoggingConfig:
    """Logging configuration accessor."""

    def __init__(self, settings: Settings):
        self._settings = settings

    @property
    def level(self) -> str:
        return self._settings.log_level

    @property
    def format(self) -> str:
        return self._settings.log_format

    @property
    def file(self) -> str | None:
        return self._settings.log_file


class VisionConfig:
    """Vision models configuration accessor."""

    def __init__(self, settings: Settings):
        self._settings = settings

    @property
    def models(self) -> str:
        return self._settings.vision_models

    @property
    def models_list(self) -> list[str]:
        return self._settings.vision_models_list

    def supports_vision(self, model_name: str) -> bool:
        """Check if a model supports vision capabilities."""
        model_lower = model_name.lower()
        return any(vision_keyword in model_lower for vision_keyword in self.models_list)


class OAuthConfig:
    """OAuth provider configuration accessor."""

    def __init__(self, settings: Settings):
        self._settings = settings

    @property
    def google_client_id(self) -> str | None:
        return self._settings.google_client_id

    @property
    def google_client_secret(self) -> str | None:
        return self._settings.google_client_secret

    @property
    def google_redirect_uri(self) -> str:
        return self._settings.google_redirect_uri

    @property
    def microsoft_client_id(self) -> str | None:
        return self._settings.microsoft_client_id

    @property
    def microsoft_client_secret(self) -> str | None:
        return self._settings.microsoft_client_secret

    @property
    def microsoft_tenant_id(self) -> str:
        return self._settings.microsoft_tenant_id

    @property
    def microsoft_redirect_uri(self) -> str:
        return self._settings.microsoft_redirect_uri

    @property
    def frontend_url(self) -> str:
        return self._settings.frontend_url

    @property
    def enabled_providers(self) -> list[str]:
        return self._settings.enabled_providers_list


class MCPConfig:
    def __init__(self, settings: Settings):
        self._settings = settings

    @property
    def url(self) -> str:
        return self._settings.mcp_url

    @property
    def enabled(self) -> bool:
        return self._settings.mcp_enabled

    @property
    def gateway_timeout(self) -> int:
        return self._settings.mcp_gateway_timeout


class DBConfig:
    def __init__(self, settings: Settings):
        self._settings = settings

    @property
    def postgres_host(self) -> str:
        return self._settings.postgres_host

    @property
    def postgres_port(self) -> int:
        return self._settings.postgres_port

    @property
    def postgres_user(self) -> str:
        return self._settings.postgres_user

    @property
    def postgres_password(self) -> str:
        return self._settings.postgres_password

    @property
    def postgres_db(self) -> str:
        return self._settings.postgres_db


# Global settings instance
settings = Settings()

# Configuration accessors
groq_config = GroqConfig(settings)
ollama_config = OllamaConfig(settings)
server_config = ServerConfig(settings)
database_config = DatabaseConfig(settings)
security_config = SecurityConfig(settings)
logging_config = LoggingConfig(settings)
vision_config = VisionConfig(settings)
mcp_config = MCPConfig(settings)
db_config = DBConfig(settings)
oauth_config = OAuthConfig(settings)


def get_settings() -> Settings:
    """
    Get the application settings instance.
    This function can be used for dependency injection in FastAPI.
    """
    return settings


def reload_settings() -> Settings:
    """
    Reload settings from environment variables and .env file.
    Useful for testing or runtime configuration changes.
    """
    global settings, groq_config, ollama_config, server_config
    global database_config, security_config, logging_config, vision_config, mcp_config, db_config, oauth_config
    settings = Settings()
    groq_config = GroqConfig(settings)
    ollama_config = OllamaConfig(settings)
    server_config = ServerConfig(settings)
    database_config = DatabaseConfig(settings)
    security_config = SecurityConfig(settings)
    logging_config = LoggingConfig(settings)
    vision_config = VisionConfig(settings)
    mcp_config = MCPConfig(settings)
    db_config = DBConfig(settings)
    oauth_config = OAuthConfig(settings)

    return settings


# Convenience accessors for commonly used configurations
def get_groq_config() -> GroqConfig:
    """Get Groq configuration."""
    return groq_config


def get_ollama_config() -> OllamaConfig:
    """Get Ollama configuration."""
    return ollama_config


def get_server_config() -> ServerConfig:
    """Get server configuration."""
    return server_config


def get_database_config() -> DatabaseConfig:
    """Get database configuration."""
    return database_config


def get_security_config() -> SecurityConfig:
    """Get security configuration."""
    return security_config


def get_logging_config() -> LoggingConfig:
    """Get logging configuration."""
    return logging_config


def get_vision_config() -> VisionConfig:
    """Get vision configuration."""
    return vision_config


def get_mcp_config() -> MCPConfig:
    """Get Model Context Protocol (MCP) configuration."""
    return mcp_config


def get_oauth_config() -> OAuthConfig:
    """Get OAuth provider configuration."""
    return oauth_config


# Export commonly used settings for easy access
__all__ = [
    "Settings",
    "GroqConfig",
    "OllamaConfig",
    "ServerConfig",
    "DatabaseConfig",
    "SecurityConfig",
    "LoggingConfig",
    "VisionConfig",
    "DBConfig",
    "MCPConfig",
    "settings",
    "groq_config",
    "ollama_config",
    "server_config",
    "database_config",
    "security_config",
    "logging_config",
    "vision_config",
    "get_settings",
    "reload_settings",
    "get_groq_config",
    "get_ollama_config",
    "get_server_config",
    "get_database_config",
    "get_security_config",
    "get_logging_config",
    "get_vision_config",
    "get_mcp_config",
]
