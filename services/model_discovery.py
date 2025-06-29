"""
Model Discovery Service for Phase 9: Dynamic Model Selection

This service provides dynamic model discovery and caching for all LLM providers.
It supports real-time model fetching, caching, and capability discovery.

Author: Auto Post Generator
Version: 1.0.0
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import requests
from dataclasses import dataclass, asdict

# Import provider clients
try:
    import openai
except ImportError:
    openai = None

try:
    import anthropic
except ImportError:
    anthropic = None

try:
    import google.generativeai as genai
except ImportError:
    genai = None


@dataclass
class ModelInfo:
    """Model information data class."""
    id: str
    name: str
    provider: str
    description: str = ""
    max_tokens: Optional[int] = None
    context_window: Optional[int] = None
    supports_functions: bool = False
    supports_vision: bool = False
    supports_json_mode: bool = False
    temperature_range: Tuple[float, float] = (0.0, 1.0)
    pricing: Optional[Dict[str, float]] = None
    deprecated: bool = False
    version: Optional[str] = None
    created_at: Optional[str] = None


@dataclass
class CacheEntry:
    """Cache entry for models."""
    models: List[ModelInfo]
    cached_at: datetime
    expires_at: datetime
    provider: str


class ModelDiscoveryService:
    """
    Service for discovering available models from LLM providers.
    
    Provides real-time model discovery, caching, and capability analysis
    for OpenAI, Anthropic, and Google providers.
    """
    
    def __init__(self, cache_expiry_hours: int = 1):
        """
        Initialize the model discovery service.
        
        Args:
            cache_expiry_hours: Hours before cache expires (default: 1)
        """
        self.cache_expiry_hours = cache_expiry_hours
        self._cache: Dict[str, CacheEntry] = {}
        self.logger = logging.getLogger(__name__)
        
        # Provider model endpoints configuration
        self.provider_config = {
            "openai": {
                "base_url": "https://api.openai.com/v1",
                "models_endpoint": "/models",
                "auth_method": "bearer_token",
                "discovery_method": "api_endpoint"
            },
            "anthropic": {
                "base_url": "https://api.anthropic.com/v1", 
                "models_endpoint": None,  # Uses trial-and-error
                "auth_method": "x_api_key",
                "discovery_method": "trial_and_error"
            },
            "google": {
                "base_url": "https://generativelanguage.googleapis.com/v1",
                "models_endpoint": "/models",
                "auth_method": "api_key",
                "discovery_method": "api_endpoint"
            }
        }
        
        # Fallback model lists
        self.fallback_models = {
            "openai": [
                ModelInfo("gpt-4o", "GPT-4 Optimized", "openai", "Latest GPT-4 model", 4096, 128000, True, True, True),
                ModelInfo("gpt-4o-mini", "GPT-4 Mini", "openai", "Smaller, faster GPT-4", 4096, 128000, True, True, True),
                ModelInfo("gpt-3.5-turbo", "GPT-3.5 Turbo", "openai", "Fast and capable", 4096, 16385, True, False, True)
            ],
            "anthropic": [
                ModelInfo("claude-3-5-sonnet-20241022", "Claude 3.5 Sonnet", "anthropic", "Most capable Claude model", 8192, 200000, True, True, False),
                ModelInfo("claude-3-haiku-20240307", "Claude 3 Haiku", "anthropic", "Fast and efficient", 4096, 200000, True, True, False)
            ],
            "google": [
                ModelInfo("gemini-1.5-pro", "Gemini 1.5 Pro", "google", "Most capable multimodal model", 8192, 1048576, True, True, True),
                ModelInfo("gemini-1.5-flash", "Gemini 1.5 Flash", "google", "Fast and versatile", 8192, 1048576, True, True, True)
            ]
        }
    
    async def fetch_available_models(self, provider: str, api_key: str) -> List[ModelInfo]:
        """
        Fetch available models for a provider.
        
        Args:
            provider: LLM provider name ("openai", "anthropic", "google")
            api_key: API key for the provider
            
        Returns:
            List of ModelInfo objects
            
        Raises:
            ValueError: If provider is not supported
            Exception: If API call fails
        """
        if provider not in self.provider_config:
            raise ValueError(f"Unsupported provider: {provider}")
        
        # Check cache first
        cached_models = self.get_cached_models(provider)
        if cached_models:
            self.logger.info(f"Using cached models for {provider}")
            return cached_models
        
        try:
            # Fetch models based on provider
            if provider == "openai":
                models = await self._fetch_openai_models(api_key)
            elif provider == "anthropic":
                models = await self._fetch_anthropic_models(api_key)
            elif provider == "google":
                models = await self._fetch_google_models(api_key)
            else:
                models = self.fallback_models.get(provider, [])
            
            # Cache the results
            self.cache_models(provider, models)
            
            self.logger.info(f"Successfully fetched {len(models)} models for {provider}")
            return models
            
        except Exception as e:
            self.logger.error(f"Failed to fetch models for {provider}: {str(e)}")
            # Return fallback models
            fallback = self.fallback_models.get(provider, [])
            if fallback:
                self.logger.info(f"Using fallback models for {provider}")
            return fallback
    
    async def _fetch_openai_models(self, api_key: str) -> List[ModelInfo]:
        """Fetch models from OpenAI API."""
        if not openai:
            raise ImportError("OpenAI library not installed")
        
        try:
            client = openai.OpenAI(api_key=api_key)
            response = client.models.list()
            
            models = []
            for model in response.data:
                # Filter for chat/text models
                if any(prefix in model.id.lower() for prefix in ['gpt-', 'text-', 'davinci']):
                    # Get model capabilities
                    capabilities = self._get_openai_model_capabilities(model.id)
                    
                    model_info = ModelInfo(
                        id=model.id,
                        name=capabilities.get('name', model.id),
                        provider="openai",
                        description=capabilities.get('description', ''),
                        max_tokens=capabilities.get('max_tokens', 4096),
                        context_window=capabilities.get('context_window', 16385),
                        supports_functions=capabilities.get('supports_functions', True),
                        supports_vision=capabilities.get('supports_vision', False),
                        supports_json_mode=capabilities.get('supports_json_mode', True),
                        temperature_range=(0.0, 2.0),
                        pricing=capabilities.get('pricing'),
                        deprecated=capabilities.get('deprecated', False),
                        version=capabilities.get('version'),
                        created_at=datetime.fromtimestamp(model.created).isoformat() if hasattr(model, 'created') else None
                    )
                    models.append(model_info)
            
            return sorted(models, key=lambda x: x.id)
            
        except Exception as e:
            self.logger.error(f"OpenAI API error: {str(e)}")
            raise
    
    async def _fetch_anthropic_models(self, api_key: str) -> List[ModelInfo]:
        """Fetch models from Anthropic using trial-and-error approach."""
        if not anthropic:
            raise ImportError("Anthropic library not installed")
        
        # Anthropic doesn't have a models endpoint, so we use known models
        # and test them with a simple API call
        known_models = [
            "claude-3-5-sonnet-20241022",
            "claude-3-opus-20240229", 
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307"
        ]
        
        available_models = []
        client = anthropic.Anthropic(api_key=api_key)
        
        for model_id in known_models:
            try:
                # Test the model with a minimal request
                response = client.messages.create(
                    model=model_id,
                    max_tokens=1,
                    messages=[{"role": "user", "content": "test"}]
                )
                
                # If successful, add to available models
                capabilities = self._get_anthropic_model_capabilities(model_id)
                
                model_info = ModelInfo(
                    id=model_id,
                    name=capabilities.get('name', model_id),
                    provider="anthropic",
                    description=capabilities.get('description', ''),
                    max_tokens=capabilities.get('max_tokens', 8192),
                    context_window=capabilities.get('context_window', 200000),
                    supports_functions=capabilities.get('supports_functions', True),
                    supports_vision=capabilities.get('supports_vision', True),
                    supports_json_mode=capabilities.get('supports_json_mode', False),
                    temperature_range=(0.0, 1.0),
                    pricing=capabilities.get('pricing'),
                    deprecated=capabilities.get('deprecated', False),
                    version=capabilities.get('version')
                )
                available_models.append(model_info)
                
            except Exception as e:
                self.logger.debug(f"Model {model_id} not available: {str(e)}")
                continue
        
        return available_models
    
    async def _fetch_google_models(self, api_key: str) -> List[ModelInfo]:
        """Fetch models from Google Gemini API."""
        if not genai:
            raise ImportError("Google GenerativeAI library not installed")
        
        try:
            genai.configure(api_key=api_key)
            
            # Use the models API
            models_list = genai.list_models()
            
            models = []
            for model in models_list:
                # Filter for generation models
                if 'generateContent' in getattr(model, 'supported_generation_methods', []):
                    # Extract model ID from full name
                    model_id = model.name.split('/')[-1] if '/' in model.name else model.name
                    
                    capabilities = self._get_google_model_capabilities(model_id)
                    
                    model_info = ModelInfo(
                        id=model_id,
                        name=capabilities.get('name', getattr(model, 'display_name', model_id)),
                        provider="google",
                        description=capabilities.get('description', getattr(model, 'description', '')),
                        max_tokens=capabilities.get('max_tokens', 8192),
                        context_window=capabilities.get('context_window', getattr(model, 'input_token_limit', 1048576)),
                        supports_functions=capabilities.get('supports_functions', True),
                        supports_vision=capabilities.get('supports_vision', True),
                        supports_json_mode=capabilities.get('supports_json_mode', True),
                        temperature_range=(0.0, 2.0),
                        pricing=capabilities.get('pricing'),
                        deprecated=capabilities.get('deprecated', False),
                        version=capabilities.get('version', getattr(model, 'version', None))
                    )
                    models.append(model_info)
            
            return sorted(models, key=lambda x: x.id)
            
        except Exception as e:
            self.logger.error(f"Google API error: {str(e)}")
            raise
    
    def _get_openai_model_capabilities(self, model_id: str) -> Dict[str, Any]:
        """Get OpenAI model capabilities."""
        capabilities_map = {
            "gpt-4o": {
                "name": "GPT-4 Optimized",
                "description": "Latest GPT-4 model with improved performance",
                "max_tokens": 4096,
                "context_window": 128000,
                "supports_functions": True,
                "supports_vision": True,
                "supports_json_mode": True,
                "pricing": {"input_per_1k": 0.005, "output_per_1k": 0.015},
                "version": "2024-05-13"
            },
            "gpt-4o-mini": {
                "name": "GPT-4 Mini",
                "description": "Smaller, faster GPT-4 model",
                "max_tokens": 4096,
                "context_window": 128000,
                "supports_functions": True,
                "supports_vision": True,
                "supports_json_mode": True,
                "pricing": {"input_per_1k": 0.00015, "output_per_1k": 0.0006},
                "version": "2024-07-18"
            },
            "gpt-3.5-turbo": {
                "name": "GPT-3.5 Turbo",
                "description": "Fast and capable model",
                "max_tokens": 4096,
                "context_window": 16385,
                "supports_functions": True,
                "supports_vision": False,
                "supports_json_mode": True,
                "pricing": {"input_per_1k": 0.0005, "output_per_1k": 0.0015},
                "version": "0125"
            }
        }
        
        return capabilities_map.get(model_id, {
            "name": model_id,
            "description": "OpenAI model",
            "max_tokens": 4096,
            "context_window": 16385,
            "supports_functions": True,
            "supports_vision": False,
            "supports_json_mode": True
        })
    
    def _get_anthropic_model_capabilities(self, model_id: str) -> Dict[str, Any]:
        """Get Anthropic model capabilities."""
        capabilities_map = {
            "claude-3-5-sonnet-20241022": {
                "name": "Claude 3.5 Sonnet",
                "description": "Most capable Claude model",
                "max_tokens": 8192,
                "context_window": 200000,
                "supports_functions": True,
                "supports_vision": True,
                "supports_json_mode": False,
                "pricing": {"input_per_1k": 0.003, "output_per_1k": 0.015},
                "version": "2024-10-22"
            },
            "claude-3-haiku-20240307": {
                "name": "Claude 3 Haiku",
                "description": "Fast and efficient Claude model",
                "max_tokens": 4096,
                "context_window": 200000,
                "supports_functions": True,
                "supports_vision": True,
                "supports_json_mode": False,
                "pricing": {"input_per_1k": 0.00025, "output_per_1k": 0.00125},
                "version": "2024-03-07"
            }
        }
        
        return capabilities_map.get(model_id, {
            "name": model_id,
            "description": "Anthropic Claude model",
            "max_tokens": 4096,
            "context_window": 200000,
            "supports_functions": True,
            "supports_vision": True,
            "supports_json_mode": False
        })
    
    def _get_google_model_capabilities(self, model_id: str) -> Dict[str, Any]:
        """Get Google model capabilities."""
        capabilities_map = {
            "gemini-1.5-pro": {
                "name": "Gemini 1.5 Pro",
                "description": "Most capable multimodal model",
                "max_tokens": 8192,
                "context_window": 1048576,
                "supports_functions": True,
                "supports_vision": True,
                "supports_json_mode": True,
                "pricing": {"input_per_1k": 0.00125, "output_per_1k": 0.005},
                "version": "001"
            },
            "gemini-1.5-flash": {
                "name": "Gemini 1.5 Flash",
                "description": "Fast and versatile multimodal model",
                "max_tokens": 8192,
                "context_window": 1048576,
                "supports_functions": True,
                "supports_vision": True,
                "supports_json_mode": True,
                "pricing": {"input_per_1k": 0.000075, "output_per_1k": 0.0003},
                "version": "001"
            }
        }
        
        return capabilities_map.get(model_id, {
            "name": model_id,
            "description": "Google Gemini model",
            "max_tokens": 8192,
            "context_window": 1048576,
            "supports_functions": True,
            "supports_vision": True,
            "supports_json_mode": True
        })
    
    def cache_models(self, provider: str, models: List[ModelInfo]) -> None:
        """Cache models for a provider."""
        expires_at = datetime.now() + timedelta(hours=self.cache_expiry_hours)
        
        cache_entry = CacheEntry(
            models=models,
            cached_at=datetime.now(),
            expires_at=expires_at,
            provider=provider
        )
        
        self._cache[provider] = cache_entry
        self.logger.debug(f"Cached {len(models)} models for {provider} until {expires_at}")
    
    def get_cached_models(self, provider: str) -> Optional[List[ModelInfo]]:
        """Get cached models for a provider if not expired."""
        if provider not in self._cache:
            return None
        
        cache_entry = self._cache[provider]
        
        if datetime.now() > cache_entry.expires_at:
            # Cache expired
            del self._cache[provider]
            self.logger.debug(f"Cache expired for {provider}")
            return None
        
        self.logger.debug(f"Cache hit for {provider} - {len(cache_entry.models)} models")
        return cache_entry.models
    
    def invalidate_cache(self, provider: Optional[str] = None) -> None:
        """Invalidate cache for a provider or all providers."""
        if provider:
            if provider in self._cache:
                del self._cache[provider]
                self.logger.info(f"Invalidated cache for {provider}")
        else:
            self._cache.clear()
            self.logger.info("Invalidated all model caches")
    
    async def discover_model_capabilities(self, provider: str, model_id: str, api_key: str) -> Optional[ModelInfo]:
        """
        Discover detailed capabilities for a specific model.
        
        Args:
            provider: LLM provider name
            model_id: Model identifier
            api_key: API key for the provider
            
        Returns:
            ModelInfo object with detailed capabilities or None if not found
        """
        try:
            models = await self.fetch_available_models(provider, api_key)
            
            for model in models:
                if model.id == model_id:
                    return model
            
            self.logger.warning(f"Model {model_id} not found for provider {provider}")
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to discover capabilities for {model_id}: {str(e)}")
            return None
    
    def get_recommended_models(self, provider: str, requirements: Dict[str, Any]) -> List[ModelInfo]:
        """
        Get recommended models based on requirements.
        
        Args:
            provider: LLM provider name
            requirements: Dict with requirements like max_tokens, supports_vision, etc.
            
        Returns:
            List of recommended ModelInfo objects
        """
        cached_models = self.get_cached_models(provider)
        if not cached_models:
            return self.fallback_models.get(provider, [])
        
        recommended = []
        
        for model in cached_models:
            # Check requirements
            meets_requirements = True
            
            if 'min_context_window' in requirements:
                if not model.context_window or model.context_window < requirements['min_context_window']:
                    meets_requirements = False
            
            if 'supports_vision' in requirements:
                if requirements['supports_vision'] and not model.supports_vision:
                    meets_requirements = False
            
            if 'supports_functions' in requirements:
                if requirements['supports_functions'] and not model.supports_functions:
                    meets_requirements = False
            
            if 'max_cost_per_1k' in requirements and model.pricing:
                if model.pricing.get('input_per_1k', 0) > requirements['max_cost_per_1k']:
                    meets_requirements = False
            
            if meets_requirements and not model.deprecated:
                recommended.append(model)
        
        # Sort by context window (higher is better) and then by cost (lower is better)
        recommended.sort(key=lambda x: (
            -(x.context_window or 0),
            x.pricing.get('input_per_1k', 0) if x.pricing else 0
        ))
        
        return recommended
    
    def export_cache_to_dict(self) -> Dict[str, Any]:
        """Export cache to dictionary for serialization."""
        cache_dict = {}
        
        for provider, cache_entry in self._cache.items():
            cache_dict[provider] = {
                "models": [asdict(model) for model in cache_entry.models],
                "cached_at": cache_entry.cached_at.isoformat(),
                "expires_at": cache_entry.expires_at.isoformat(),
                "provider": cache_entry.provider
            }
        
        return cache_dict
    
    def import_cache_from_dict(self, cache_dict: Dict[str, Any]) -> None:
        """Import cache from dictionary."""
        for provider, cache_data in cache_dict.items():
            try:
                models = [ModelInfo(**model_data) for model_data in cache_data["models"]]
                
                cache_entry = CacheEntry(
                    models=models,
                    cached_at=datetime.fromisoformat(cache_data["cached_at"]),
                    expires_at=datetime.fromisoformat(cache_data["expires_at"]),
                    provider=cache_data["provider"]
                )
                
                # Only import if not expired
                if datetime.now() <= cache_entry.expires_at:
                    self._cache[provider] = cache_entry
                    self.logger.info(f"Imported cache for {provider}")
                
            except Exception as e:
                self.logger.error(f"Failed to import cache for {provider}: {str(e)}")


# Global instance for easy access
_model_discovery_service: Optional[ModelDiscoveryService] = None


def get_model_discovery_service() -> ModelDiscoveryService:
    """Get or create the global model discovery service instance."""
    global _model_discovery_service
    
    if _model_discovery_service is None:
        _model_discovery_service = ModelDiscoveryService()
    
    return _model_discovery_service


async def discover_models_for_provider(provider: str, api_key: str) -> List[ModelInfo]:
    """
    Convenience function to discover models for a provider.
    
    Args:
        provider: LLM provider name
        api_key: API key for the provider
        
    Returns:
        List of ModelInfo objects
    """
    service = get_model_discovery_service()
    return await service.fetch_available_models(provider, api_key)


def get_cached_models_for_provider(provider: str) -> Optional[List[ModelInfo]]:
    """
    Convenience function to get cached models for a provider.
    
    Args:
        provider: LLM provider name
        
    Returns:
        List of cached ModelInfo objects or None if not cached
    """
    service = get_model_discovery_service()
    return service.get_cached_models(provider)