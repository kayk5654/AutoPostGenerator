"""
Configuration for Auto Post Generator

Contains all configuration constants including Phase 9 dynamic model management.
"""

import os
from typing import Dict, List, Tuple, Any, Optional

# Core Application Configuration
LLM_PROVIDERS = ["Google Gemini", "OpenAI", "Anthropic"]

TARGET_PLATFORMS = ["X", "Facebook", "LinkedIn", "Instagram"]

SUPPORTED_TEXT_FORMATS = [".txt", ".docx", ".pdf", ".md"]

SUPPORTED_HISTORY_FORMATS = [".xlsx"]

MAX_FILE_SIZE_MB = 10

POST_COUNT_MIN = 1
POST_COUNT_MAX = 50

# Phase 9: Dynamic Model Selection Configuration

# Provider Model Endpoint Configuration
PROVIDER_MODEL_ENDPOINTS = {
    "openai": {
        "base_url": "https://api.openai.com/v1",
        "models_endpoint": "/models",
        "auth_method": "bearer_token",
        "rate_limit": 60,  # requests per minute
        "timeout": 30,  # seconds
        "discovery_method": "api_endpoint",
        "retry_attempts": 3,
        "retry_delay": 1.0  # seconds
    },
    "anthropic": {
        "base_url": "https://api.anthropic.com/v1",
        "models_endpoint": None,  # Uses trial-and-error approach
        "auth_method": "x_api_key",
        "rate_limit": 50,  # requests per minute
        "timeout": 30,  # seconds
        "discovery_method": "trial_and_error",
        "retry_attempts": 2,
        "retry_delay": 2.0  # seconds
    },
    "google": {
        "base_url": "https://generativelanguage.googleapis.com/v1",
        "models_endpoint": "/models",
        "auth_method": "api_key",
        "rate_limit": 60,  # requests per minute
        "timeout": 30,  # seconds
        "discovery_method": "api_endpoint",
        "retry_attempts": 3,
        "retry_delay": 1.0  # seconds
    }
}

# Model Capability Definitions
MODEL_CAPABILITIES = {
    # OpenAI Models
    "gpt-4o": {
        "provider": "openai",
        "max_tokens": 4096,
        "context_window": 128000,
        "supports_functions": True,
        "supports_vision": True,
        "supports_json_mode": True,
        "temperature_range": (0.0, 2.0),
        "top_p_range": (0.0, 1.0),
        "pricing": {
            "input_per_1k": 0.005,
            "output_per_1k": 0.015
        },
        "deprecated": False,
        "version": "2024-05-13",
        "recommended_use_cases": ["general", "creative", "analysis", "vision"]
    },
    "gpt-4o-mini": {
        "provider": "openai",
        "max_tokens": 4096,
        "context_window": 128000,
        "supports_functions": True,
        "supports_vision": True,
        "supports_json_mode": True,
        "temperature_range": (0.0, 2.0),
        "top_p_range": (0.0, 1.0),
        "pricing": {
            "input_per_1k": 0.00015,
            "output_per_1k": 0.0006
        },
        "deprecated": False,
        "version": "2024-07-18",
        "recommended_use_cases": ["general", "fast", "cost-effective"]
    },
    "gpt-3.5-turbo": {
        "provider": "openai",
        "max_tokens": 4096,
        "context_window": 16385,
        "supports_functions": True,
        "supports_vision": False,
        "supports_json_mode": True,
        "temperature_range": (0.0, 2.0),
        "top_p_range": (0.0, 1.0),
        "pricing": {
            "input_per_1k": 0.0005,
            "output_per_1k": 0.0015
        },
        "deprecated": False,
        "version": "0125",
        "recommended_use_cases": ["general", "fast", "legacy"]
    },
    
    # Anthropic Models
    "claude-3-5-sonnet-20241022": {
        "provider": "anthropic",
        "max_tokens": 8192,
        "context_window": 200000,
        "supports_functions": True,
        "supports_vision": True,
        "supports_json_mode": False,
        "temperature_range": (0.0, 1.0),
        "top_p_range": (0.0, 1.0),
        "pricing": {
            "input_per_1k": 0.003,
            "output_per_1k": 0.015
        },
        "deprecated": False,
        "version": "2024-10-22",
        "recommended_use_cases": ["analysis", "writing", "reasoning", "vision"]
    },
    "claude-3-haiku-20240307": {
        "provider": "anthropic",
        "max_tokens": 4096,
        "context_window": 200000,
        "supports_functions": True,
        "supports_vision": True,
        "supports_json_mode": False,
        "temperature_range": (0.0, 1.0),
        "top_p_range": (0.0, 1.0),
        "pricing": {
            "input_per_1k": 0.00025,
            "output_per_1k": 0.00125
        },
        "deprecated": False,
        "version": "2024-03-07",
        "recommended_use_cases": ["fast", "cost-effective", "simple-tasks"]
    },
    
    # Google Models
    "gemini-1.5-pro": {
        "provider": "google",
        "max_tokens": 8192,
        "context_window": 1048576,
        "supports_functions": True,
        "supports_vision": True,
        "supports_json_mode": True,
        "temperature_range": (0.0, 2.0),
        "top_p_range": (0.0, 1.0),
        "pricing": {
            "input_per_1k": 0.00125,
            "output_per_1k": 0.005
        },
        "deprecated": False,
        "version": "001",
        "recommended_use_cases": ["analysis", "large-context", "vision", "multimodal"]
    },
    "gemini-1.5-flash": {
        "provider": "google",
        "max_tokens": 8192,
        "context_window": 1048576,
        "supports_functions": True,
        "supports_vision": True,
        "supports_json_mode": True,
        "temperature_range": (0.0, 2.0),
        "top_p_range": (0.0, 1.0),
        "pricing": {
            "input_per_1k": 0.000075,
            "output_per_1k": 0.0003
        },
        "deprecated": False,
        "version": "001",
        "recommended_use_cases": ["fast", "cost-effective", "multimodal"]
    }
}

# Model Parameter Templates
MODEL_PARAMETER_TEMPLATES = {
    "default": {
        "temperature": 0.7,
        "max_tokens": 4096,
        "top_p": 1.0,
        "frequency_penalty": 0.0,
        "presence_penalty": 0.0,
        "stop": None
    },
    "creative": {
        "temperature": 1.2,
        "max_tokens": 4096,
        "top_p": 0.9,
        "frequency_penalty": 0.1,
        "presence_penalty": 0.1,
        "stop": None
    },
    "precise": {
        "temperature": 0.2,
        "max_tokens": 4096,
        "top_p": 0.8,
        "frequency_penalty": 0.0,
        "presence_penalty": 0.0,
        "stop": None
    },
    "balanced": {
        "temperature": 0.7,
        "max_tokens": 4096,
        "top_p": 0.95,
        "frequency_penalty": 0.05,
        "presence_penalty": 0.05,
        "stop": None
    }
}

# Provider-Specific Parameter Mapping
PROVIDER_PARAMETER_MAPPING = {
    "openai": {
        "temperature": "temperature",
        "max_tokens": "max_tokens",
        "top_p": "top_p",
        "frequency_penalty": "frequency_penalty",
        "presence_penalty": "presence_penalty",
        "stop": "stop"
    },
    "anthropic": {
        "temperature": "temperature",
        "max_tokens": "max_tokens",
        "top_p": "top_p",
        "stop": "stop_sequences"
        # Note: Anthropic doesn't support frequency/presence penalty
    },
    "google": {
        "temperature": "temperature",
        "max_tokens": "maxOutputTokens",
        "top_p": "topP",
        "stop": "stopSequences"
        # Note: Google uses different parameter names
    }
}

# Fallback Model Lists (when dynamic discovery fails)
FALLBACK_MODELS = {
    "openai": ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"],
    "anthropic": ["claude-3-5-sonnet-20241022", "claude-3-haiku-20240307"],
    "google": ["gemini-1.5-pro", "gemini-1.5-flash"]
}

# Model Discovery Configuration
MODEL_DISCOVERY_CONFIG = {
    "cache_expiry_hours": 1,  # How long to cache model lists
    "max_concurrent_requests": 3,  # Max concurrent discovery requests
    "discovery_timeout": 30,  # Timeout for discovery requests (seconds)
    "enable_fallback": True,  # Use fallback models if discovery fails
    "auto_refresh_on_error": True,  # Auto-refresh cache on API errors
    "min_models_threshold": 1  # Minimum models required before using fallbacks
}

# Platform-Specific Character Limits (for validation)
PLATFORM_LIMITS = {
    "X": {
        "max_characters": 280,
        "supports_threads": True,
        "supports_media": True
    },
    "LinkedIn": {
        "max_characters": 3000,
        "supports_threads": False,
        "supports_media": True
    },
    "Facebook": {
        "max_characters": 63206,
        "supports_threads": False,
        "supports_media": True
    },
    "Instagram": {
        "max_characters": 2200,
        "supports_threads": False,
        "supports_media": True
    }
}

# Environment-Based Configuration Overrides
def get_env_config() -> Dict[str, Any]:
    """Get configuration overrides from environment variables."""
    env_config = {}
    
    # Model discovery settings
    if cache_hours := os.getenv('AUTO_POST_GENERATOR_CACHE_HOURS'):
        try:
            env_config['cache_expiry_hours'] = int(cache_hours)
        except ValueError:
            pass
    
    if discovery_timeout := os.getenv('AUTO_POST_GENERATOR_DISCOVERY_TIMEOUT'):
        try:
            env_config['discovery_timeout'] = int(discovery_timeout)
        except ValueError:
            pass
    
    # Rate limiting
    for provider in PROVIDER_MODEL_ENDPOINTS:
        rate_limit_key = f'AUTO_POST_GENERATOR_{provider.upper()}_RATE_LIMIT'
        if rate_limit := os.getenv(rate_limit_key):
            try:
                if provider not in env_config:
                    env_config[provider] = {}
                env_config[provider]['rate_limit'] = int(rate_limit)
            except ValueError:
                pass
    
    return env_config

# Dynamic Configuration Management
class ConfigurationManager:
    """Manages dynamic configuration with validation and hot-reloading."""
    
    def __init__(self):
        self._config_cache = {}
        self._last_reload = None
        self.env_config = get_env_config()
    
    def get_provider_config(self, provider: str) -> Dict[str, Any]:
        """Get configuration for a specific provider."""
        base_config = PROVIDER_MODEL_ENDPOINTS.get(provider, {})
        env_overrides = self.env_config.get(provider, {})
        
        # Merge configurations
        config = {**base_config, **env_overrides}
        return config
    
    def get_model_capabilities(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Get capabilities for a specific model."""
        return MODEL_CAPABILITIES.get(model_id)
    
    def get_parameter_template(self, template_name: str) -> Dict[str, Any]:
        """Get parameter template by name."""
        return MODEL_PARAMETER_TEMPLATES.get(template_name, MODEL_PARAMETER_TEMPLATES["default"])
    
    def map_parameters_for_provider(self, provider: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Map generic parameters to provider-specific format."""
        mapping = PROVIDER_PARAMETER_MAPPING.get(provider, {})
        mapped_params = {}
        
        for generic_param, value in parameters.items():
            if generic_param in mapping:
                provider_param = mapping[generic_param]
                mapped_params[provider_param] = value
        
        return mapped_params
    
    def validate_model_parameters(self, model_id: str, parameters: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate parameters against model capabilities.
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        capabilities = self.get_model_capabilities(model_id)
        if not capabilities:
            return False, [f"Unknown model: {model_id}"]
        
        errors = []
        
        # Validate temperature
        if 'temperature' in parameters:
            temp = parameters['temperature']
            temp_range = capabilities.get('temperature_range', (0.0, 1.0))
            if not (temp_range[0] <= temp <= temp_range[1]):
                errors.append(f"Temperature {temp} outside valid range {temp_range}")
        
        # Validate max_tokens
        if 'max_tokens' in parameters:
            max_tokens = parameters['max_tokens']
            model_max = capabilities.get('max_tokens', 4096)
            if max_tokens > model_max:
                errors.append(f"max_tokens {max_tokens} exceeds model limit {model_max}")
        
        # Validate top_p
        if 'top_p' in parameters:
            top_p = parameters['top_p']
            top_p_range = capabilities.get('top_p_range', (0.0, 1.0))
            if not (top_p_range[0] <= top_p <= top_p_range[1]):
                errors.append(f"top_p {top_p} outside valid range {top_p_range}")
        
        return len(errors) == 0, errors
    
    def get_fallback_models(self, provider: str) -> List[str]:
        """Get fallback models for a provider."""
        return FALLBACK_MODELS.get(provider, [])
    
    def reload_configuration(self) -> None:
        """Reload configuration from environment variables."""
        self.env_config = get_env_config()
        self._config_cache.clear()
        self._last_reload = os.path.getmtime(__file__) if os.path.exists(__file__) else None

# Global configuration manager instance
_config_manager: Optional[ConfigurationManager] = None

def get_config_manager() -> ConfigurationManager:
    """Get or create the global configuration manager instance."""
    global _config_manager
    
    if _config_manager is None:
        _config_manager = ConfigurationManager()
    
    return _config_manager