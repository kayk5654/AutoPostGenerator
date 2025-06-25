# Codebase Architecture Plan: Auto Post Generator

This document outlines the planned architecture for the Auto Post Generator project. The structure is based on the principles of Clean Architecture and SOLID to ensure the codebase is maintainable, scalable, and easy to test.

## 1. Directory & File Structure

The project will be organized into the following directory structure:

auto_post_generator/
├── venv/
├── app.py
├── requirements.txt
├── config.py
|
├── services/
│   ├── init.py
│   ├── file_service.py
│   ├── llm_service.py
│   └── post_service.py
|
└── utils/
├── init.py
└── data_exporter.py

## 2. Component Breakdown & Responsibilities

### `app.py` (UI Layer)

* **Responsibility**: This is the main entry point of the application. Its sole responsibility is to manage the user interface using the Streamlit library. It should contain all `st.*` calls.
* **Functionality**:
    * Render all UI components (file uploaders, buttons, dropdowns, text areas).
    * Capture user input from these components.
    * Act as a "controller" that calls functions from the `services` layer to perform business logic. It should not contain any business logic itself.
    * Receive data back from the services and display it to the user.
* **Design Principle**: Adheres to the **Single Responsibility Principle**. It only handles the "view".

### `config.py` (Configuration)

* **Responsibility**: Holds static configuration data for the application.
* **Functionality**:
    * Define constant variables for UI elements, such as the list of LLM providers or target platforms.
    * Example: `LLM_PROVIDERS = ["Google Gemini", "OpenAI", "Anthropic"]`.
* **Benefit**: Centralizes configuration, making it easy to update options without searching through code.

### `services/` (Core Logic Layer)

This package contains the core business logic of the application, completely decoupled from the Streamlit UI.

#### `services/file_service.py`

* **Responsibility**: Handles all file reading and parsing operations.
* **Key Functions**:
    * `extract_text_from_uploads(uploaded_files: list) -> str`: A function that takes a list of Streamlit `UploadedFile` objects, determines their type (`.txt`, `.docx`, `.pdf`), and uses the appropriate parsing library to extract and return all content as a single string.
    * `extract_posts_from_history(history_file) -> list[str]`: A function that takes the `.xlsx` history file, reads it with Pandas, and returns a list of post text strings.

#### `services/llm_service.py`

* **Responsibility**: Manages all interactions with external Large Language Model APIs.
* **Key Functions**:
    * `build_master_prompt(...) -> str`: A function that takes all the text inputs (source text, brand guide, post history) and formats them into a single, detailed prompt string for the LLM.
    * `call_llm(provider: str, api_key: str, prompt: str) -> str`: A "factory" function that acts as a gateway. Based on the `provider` string, it instantiates the correct client (Gemini, OpenAI, etc.), sends the request, and returns the raw text response from the API.
* **Design Principle**: Adheres to the **Open/Closed Principle**. To support a new LLM, you can add a new condition within `call_llm` without breaking the existing logic.

#### `services/post_service.py`

* **Responsibility**: Orchestrates the main application workflow, acting as the primary "use case" handler.
* **Key Functions**:
    * `generate_posts_workflow(...) -> list[str]`: The main orchestration function called by `app.py`. It will:
        1.  Invoke `file_service` to get content from the uploaded files.
        2.  Invoke `llm_service.build_master_prompt` to create the prompt.
        3.  Invoke `llm_service.call_llm` to get the LLM's response.
        4.  Perform any necessary parsing/cleaning of the response to create a list of individual post strings.
        5.  Return the final list of posts to `app.py`.

### `utils/` (Utility Layer)

This package contains generic, reusable helper functions that are not part of the core business logic.

#### `utils/data_exporter.py`

* **Responsibility**: Handles the creation and formatting of data for export.
* **Key Functions**:
    * `create_csv_export(posts: list, platform: str) -> tuple[str, str]`:
        1.  Takes the final list of (potentially user-edited) posts.
        2.  Creates a Pandas DataFrame with `post_text` and `generation_timestamp` columns.
        3.  Generates a dynamic filename based on the platform and current date (e.g., `posts_for_X_20250625.csv`).
        4.  Converts the DataFrame to a CSV formatted string.
        5.  Returns the CSV string and the filename, ready for Streamlit's download button.