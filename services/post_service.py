"""
Post Service Module - Phase 6.2 Enhanced

This module orchestrates the complete post generation workflow with enhanced
error handling, logging, and input validation for production use.

Architecture:
- Coordinates between file_service and llm_service
- Implements comprehensive error handling patterns
- Provides detailed logging for debugging and monitoring
- Validates all inputs before processing
"""

import logging
import time
from typing import List, Optional, Dict, Any
from . import file_service
from . import llm_service

# Configure logging for this module
logger = logging.getLogger(__name__)


def generate_posts_workflow(
    source_files,
    brand_guide,
    history_file,
    provider: str,
    api_key: str,
    platform: str,
    count: int,
    advanced_settings: Optional[Dict[str, Any]] = None,
    selected_model: Optional[str] = None
) -> List[str]:
    """
    Main orchestration function for post generation workflow.
    
    This function coordinates the entire post generation process, from file processing
    to final post creation, with comprehensive error handling and validation.
    
    Args:
        source_files: List of uploaded source files containing content to share
        brand_guide: Optional brand guide file for voice/tone consistency
        history_file: Optional post history file for style learning
        provider (str): LLM provider name ('OpenAI', 'Google Gemini', 'Anthropic')
        api_key (str): API key for authentication with the LLM provider
        platform (str): Target social media platform ('X', 'LinkedIn', etc.)
        count (int): Number of posts to generate (1-50)
        advanced_settings (dict, optional): Advanced generation preferences including:
            - creativity_level: 'Conservative', 'Balanced', 'Creative', 'Innovative'
            - include_hashtags: bool
            - include_emojis: bool  
            - content_tone: 'Professional', 'Casual', 'Friendly', etc.
            - call_to_action: bool
            - avoid_controversy: bool
            - custom_instructions: str (Phase 8 feature) - User-provided custom instructions
        selected_model (str, optional): Phase 9 feature - Specific model to use for generation
        
    Returns:
        List[str]: List of generated social media posts
        
    Raises:
        ValueError: If required inputs are missing or invalid
        FileProcessingError: If file processing fails
        LLMServiceError: If LLM generation fails
        NetworkError: If API communication fails
        
    Example:
        >>> posts = generate_posts_workflow(
        ...     source_files=[file1, file2],
        ...     brand_guide=None,
        ...     history_file=None,
        ...     provider='OpenAI',
        ...     api_key='sk-...',
        ...     platform='LinkedIn',
        ...     count=5
        ... )
        >>> len(posts)
        5
    """
    start_time = time.time()
    workflow_id = f"{platform}_{count}_{int(start_time)}"
    
    logger.info(f"[{workflow_id}] Starting post generation workflow: {count} posts for {platform} using {provider}")
    
    # Enhanced input validation
    validation_errors = _validate_workflow_inputs(
        source_files, brand_guide, history_file, provider, api_key, platform, count, advanced_settings
    )
    
    if validation_errors:
        error_msg = f"Input validation failed: {'; '.join(validation_errors)}"
        logger.error(f"[{workflow_id}] {error_msg}")
        raise ValueError(error_msg)
    
    try:
        # Step 1: Extract text from source files with error handling
        logger.info(f"[{workflow_id}] Step 1: Extracting text from {len(source_files)} source files")
        try:
            source_text = file_service.extract_text_from_uploads(source_files)
            if not source_text or not source_text.strip():
                raise ValueError("Source files contain no readable text content")
            logger.info(f"[{workflow_id}] Extracted {len(source_text)} characters from source files")
        except Exception as e:
            logger.error(f"[{workflow_id}] Source file processing failed: {str(e)}")
            raise FileProcessingError(f"Failed to process source files: {str(e)}") from e
        
        # Step 2: Extract text from brand guide with graceful handling
        logger.info(f"[{workflow_id}] Step 2: Processing brand guide")
        brand_guide_text = ""
        if brand_guide:
            try:
                brand_guide_text = file_service.extract_text_from_uploads([brand_guide])
                logger.info(f"[{workflow_id}] Extracted {len(brand_guide_text)} characters from brand guide")
            except Exception as e:
                logger.warning(f"[{workflow_id}] Brand guide processing failed, continuing without it: {str(e)}")
                # Continue without brand guide rather than failing
        
        # Step 3: Extract post history with graceful handling
        logger.info(f"[{workflow_id}] Step 3: Processing post history")
        post_history = []
        if history_file:
            try:
                post_history = file_service.extract_posts_from_history(history_file)
                logger.info(f"[{workflow_id}] Extracted {len(post_history)} posts from history")
            except Exception as e:
                logger.warning(f"[{workflow_id}] Post history processing failed, continuing without it: {str(e)}")
                # Continue without post history rather than failing
        
        # Step 4: Build master prompt with advanced settings and custom instructions
        logger.info(f"[{workflow_id}] Step 4: Building master prompt")
        
        # Phase 8.3: Extract custom instructions from advanced settings
        custom_instructions = ""
        if advanced_settings and 'custom_instructions' in advanced_settings:
            custom_instructions = advanced_settings['custom_instructions']
            if custom_instructions:
                logger.info(f"[{workflow_id}] Custom instructions provided: {len(custom_instructions)} characters")
                logger.debug(f"[{workflow_id}] Custom instructions: {custom_instructions[:100]}...")
        
        try:
            prompt = llm_service.build_master_prompt(
                source_text, 
                brand_guide_text, 
                post_history, 
                platform, 
                count,
                advanced_settings,
                custom_instructions
            )
            logger.info(f"[{workflow_id}] Built prompt with {len(prompt)} characters")
            
            # Log prompt structure for debugging (first 500 chars)
            logger.debug(f"[{workflow_id}] Prompt preview: {prompt[:500]}...")
            
        except Exception as e:
            logger.error(f"[{workflow_id}] Prompt building failed: {str(e)}")
            raise PromptBuildingError(f"Failed to build generation prompt: {str(e)}") from e
        
        # Step 5: Call LLM to generate content with retry logic
        logger.info(f"[{workflow_id}] Step 5: Calling {provider} API" + (f" with model {selected_model}" if selected_model else ""))
        try:
            response = llm_service.call_llm(provider, api_key, prompt, model=selected_model)
            logger.info(f"[{workflow_id}] Received response from {provider}")
        except Exception as e:
            logger.error(f"[{workflow_id}] LLM API call failed: {str(e)}")
            raise LLMServiceError(f"Failed to generate content using {provider}: {str(e)}") from e
        
        # Step 6: Parse LLM response into individual posts
        logger.info(f"[{workflow_id}] Step 6: Parsing LLM response into posts")
        try:
            posts = llm_service.parse_llm_response(response)
            if not posts:
                raise ValueError("No posts were generated from the LLM response")
            
            # Validate post count matches request
            if len(posts) != count:
                logger.warning(f"[{workflow_id}] Generated {len(posts)} posts, expected {count}")
            
            logger.info(f"[{workflow_id}] Successfully generated {len(posts)} posts")
            
        except Exception as e:
            logger.error(f"[{workflow_id}] Response parsing failed: {str(e)}")
            raise ResponseParsingError(f"Failed to parse LLM response: {str(e)}") from e
        
        # Log workflow completion
        elapsed_time = time.time() - start_time
        logger.info(f"[{workflow_id}] Workflow completed successfully in {elapsed_time:.2f} seconds")
        
        return posts
        
    except (FileProcessingError, LLMServiceError, PromptBuildingError, ResponseParsingError):
        # Re-raise custom exceptions as-is
        raise
    except Exception as e:
        # Log and wrap unexpected errors
        elapsed_time = time.time() - start_time
        logger.error(f"[{workflow_id}] Unexpected error after {elapsed_time:.2f} seconds: {str(e)}")
        raise WorkflowError(f"Post generation workflow failed: {str(e)}") from e


# Custom Exception Classes for Better Error Handling

class WorkflowError(Exception):
    """Base exception for workflow-related errors."""
    pass


class FileProcessingError(WorkflowError):
    """Exception raised when file processing fails."""
    pass


class LLMServiceError(WorkflowError):
    """Exception raised when LLM service calls fail."""
    pass


class PromptBuildingError(WorkflowError):
    """Exception raised when prompt building fails."""
    pass


class ResponseParsingError(WorkflowError):
    """Exception raised when response parsing fails."""
    pass


# Helper Functions

def _validate_workflow_inputs(
    source_files,
    brand_guide,
    history_file,
    provider: str,
    api_key: str,
    platform: str,
    count: int,
    advanced_settings: Optional[Dict[str, Any]]
) -> List[str]:
    """
    Validate all workflow inputs and return list of validation errors.
    
    Args:
        source_files: Source files to validate
        brand_guide: Brand guide file to validate
        history_file: History file to validate
        provider: LLM provider name
        api_key: API key string
        platform: Target platform
        count: Post count
        advanced_settings: Advanced settings dict
        
    Returns:
        List[str]: List of validation error messages (empty if all valid)
    """
    errors = []
    
    # Validate source files
    if source_files is None:
        errors.append("source_files cannot be None")
    elif not source_files:
        errors.append("At least one source file is required")
    else:
        for i, file in enumerate(source_files):
            if not hasattr(file, 'name') or not hasattr(file, 'read'):
                errors.append(f"Source file {i+1} is not a valid file object")
    
    # Validate provider
    if not provider or not isinstance(provider, str):
        errors.append("provider must be a non-empty string")
    elif provider not in ['OpenAI', 'Google Gemini', 'Anthropic']:
        errors.append(f"Unsupported provider: {provider}")
    
    # Validate API key
    if not api_key or not isinstance(api_key, str):
        errors.append("api_key must be a non-empty string")
    elif len(api_key.strip()) < 10:
        errors.append("api_key appears to be too short")
    
    # Validate platform
    if not platform or not isinstance(platform, str):
        errors.append("platform must be a non-empty string")
    elif platform not in ['X', 'LinkedIn', 'Facebook', 'Instagram']:
        errors.append(f"Unsupported platform: {platform}")
    
    # Validate count
    if not isinstance(count, int):
        errors.append("count must be an integer")
    elif count <= 0:
        errors.append("count must be positive")
    elif count > 50:
        errors.append("count cannot exceed 50")
    
    # Validate advanced settings if provided
    if advanced_settings is not None:
        if not isinstance(advanced_settings, dict):
            errors.append("advanced_settings must be a dictionary")
        else:
            # Validate known advanced settings (Phase 8: Added custom_instructions)
            valid_keys = {'creativity_level', 'include_hashtags', 'include_emojis', 'content_tone', 'call_to_action', 'avoid_controversy', 'custom_instructions'}
            unknown_keys = set(advanced_settings.keys()) - valid_keys
            if unknown_keys:
                errors.append(f"Unknown advanced settings: {', '.join(unknown_keys)}")
    
    return errors


def get_workflow_status() -> Dict[str, Any]:
    """
    Get current workflow status and metrics.
    
    Returns:
        Dict with workflow status information
    """
    return {
        'service_name': 'post_service',
        'version': '6.2.0',
        'supported_providers': ['OpenAI', 'Google Gemini', 'Anthropic'],
        'supported_platforms': ['X', 'LinkedIn', 'Facebook', 'Instagram'],
        'max_post_count': 50,
        'features': [
            'multi_file_processing',
            'brand_guide_integration',
            'post_history_learning',
            'advanced_settings',
            'comprehensive_logging',
            'graceful_error_handling'
        ]
    }