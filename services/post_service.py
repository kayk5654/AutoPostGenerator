import logging
from . import file_service
from . import llm_service


def generate_posts_workflow(source_files, brand_guide, history_file, provider: str, api_key: str, platform: str, count: int) -> list[str]:
    """
    Main orchestration function for post generation workflow.
    
    Args:
        source_files: List of uploaded source files
        brand_guide: Brand guide file
        history_file: Post history file
        provider: LLM provider name
        api_key: API key for authentication
        platform: Target platform
        count: Number of posts to generate
        
    Returns:
        list[str]: List of generated posts
    """
    
    # Input validation
    if source_files is None:
        raise ValueError("source_files cannot be None")
    if not provider:
        raise ValueError("provider cannot be empty")
    if not api_key:
        raise ValueError("api_key cannot be empty")
    if count <= 0:
        raise ValueError("count must be positive")
    
    logging.info(f"Starting post generation workflow: {count} posts for {platform} using {provider}")
    
    try:
        # Step 1: Extract text from source files
        logging.info("Extracting text from source files")
        source_text = file_service.extract_text_from_uploads(source_files)
        
        # Step 2: Extract text from brand guide
        logging.info("Extracting brand guide content")
        brand_guide_text = file_service.extract_text_from_uploads([brand_guide]) if brand_guide else ""
        
        # Step 3: Extract post history
        logging.info("Extracting post history")
        post_history = file_service.extract_posts_from_history(history_file) if history_file else []
        
        # Step 4: Build master prompt
        logging.info("Building master prompt")
        prompt = llm_service.build_master_prompt(source_text, brand_guide_text, post_history, platform, count)
        
        # Step 5: Call LLM to generate content
        logging.info(f"Calling {provider} API")
        response = llm_service.call_llm(provider, api_key, prompt)
        
        # Step 6: Parse LLM response into individual posts
        logging.info("Parsing LLM response")
        posts = llm_service.parse_llm_response(response)
        
        logging.info(f"Successfully generated {len(posts)} posts")
        return posts
        
    except Exception as e:
        logging.error(f"Error in post generation workflow: {str(e)}")
        raise