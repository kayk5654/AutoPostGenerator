# Development Plan: Auto Post Generator MVP

This plan outlines the tasks required to build the application according to the technical specification sheet.

## Phase 1: Project Setup & UI Foundation ✅ **COMPLETED**

-   [x] **1.1: Set up the Development Environment** ✅
    -   [x] Create a new project directory ✅
    -   [x] Initialize a Python virtual environment ✅
    -   [x] Install necessary base libraries: `streamlit==1.29.0`, `pandas==2.1.4` ✅

-   [x] **1.2: Create the Main Application File** ✅
    -   [x] Create a Python script named `app.py` ✅
    -   [x] Add the basic Streamlit app structure with title "Auto Post Generator" ✅
    -   [x] Implement page configuration with icon and wide layout ✅

-   [x] **1.3: Implement the UI Layout for Inputs (Static)** ✅
    -   [x] Add the "Select LLM Provider" dropdown with options: "Google Gemini", "OpenAI", "Anthropic" ✅
    -   [x] Add the "Enter Your API Key" password input with validation ✅
    -   [x] Add the "Upload Information Source Files" multi-file uploader (supports .txt, .md, .docx, .pdf) ✅
    -   [x] Add the "Upload Brand Guide File" single-file uploader ✅
    -   [x] Add the "Upload Previous Posts History" single-file uploader (.xlsx format) ✅
    -   [x] Add the "Number of Posts to Generate" number input (min=1, max=50) ✅
    -   [x] Add the "Select Target Platform" dropdown with options: "X", "Facebook", "LinkedIn", "Instagram" ✅
    -   [x] Add the "Generate Posts" button with primary styling ✅

**Implementation Details:**
- **File:** `app.py` - Complete Streamlit application with step-by-step workflow
- **File:** `config.py` - Configuration constants for LLM providers and platforms
- **Architecture:** Clean separation between UI layer and services layer
- **Features:** Input validation, error handling, user feedback, session state management
- **UI/UX:** Professional styling with help text and clear workflow steps
- **Commits:** Multiple commits implementing Phase 1 functionality

## Phase 2: File Ingestion and Content Parsing ✅ **COMPLETED**

-   [x] **2.1: Install File Parsing Libraries** ✅
    -   [x] `pip install python-docx` ✅
    -   [x] `pip install PyMuPDF` ✅
    -   [x] `pip install openpyxl` ✅

-   [x] **2.2: Implement File Reading Logic** ✅
    -   [x] Create a function `extract_text_from_uploads(uploaded_files)` that:
        -   [x] Iterates through a list of uploaded files ✅
        -   [x] Checks the file extension (`.txt`, `.md`, `.docx`, `.pdf`) ✅
        -   [x] Calls a specific helper function to extract text for each type ✅
        -   [x] Returns a single string concatenating all text content ✅
    -   [x] Create a helper function to read `.txt` and `.md` files ✅
    -   [x] Create a helper function to read `.docx` files ✅
    -   [x] Create a helper function to read `.pdf` files ✅
    -   [x] Create a function `extract_posts_from_history(uploaded_file)` that uses Pandas to read the `.xlsx` file and returns a list of past posts ✅

-   [x] **2.3: Connect Parsing Logic to UI** ✅
    -   [x] File reading functions integrated with Streamlit UI ✅
    -   [x] Comprehensive error handling and validation ✅
    -   [x] File type validation and size checks ✅

**Implementation Details:**
- **File:** `services/file_service.py` - Complete implementation with error handling
- **Tests:** `tests/test_file_service.py` - 32 comprehensive unit tests (100% pass rate)
- **Dependencies:** All required libraries installed in `requirements.txt`
- **Commit:** `234a24e` - Phase 2 implementation completed

## Phase 3: LLM Integration and Prompt Engineering ✅ **COMPLETED**

-   [x] **3.1: Install LLM SDKs** ✅
    -   [x] `pip install google-generativeai==0.3.2 openai==1.3.7 anthropic==0.7.7` ✅
    -   [x] Updated requirements.txt with pinned versions ✅
    -   [x] Added proper import handling with fallbacks ✅

-   [x] **3.2: Create a Prompt Construction Function** ✅
    -   [x] Implemented `build_master_prompt(source_text, brand_guide_text, post_history, platform, count)` ✅
    -   [x] Role Definition: Sets AI as expert social media content creator ✅
    -   [x] Brand Guide Integration: Includes brand voice and guidelines ✅
    -   [x] Post History Examples: Uses past posts for style reference ✅
    -   [x] Source Material Integration: Incorporates new content naturally ✅
    -   [x] Platform-specific Requirements: Rules for X, LinkedIn, Facebook, Instagram ✅
    -   [x] Generation Instructions: Clear commands for post count and format ✅
    -   [x] Output Format Specification: Defines "---" separator pattern ✅

-   [x] **3.3: Create LLM API Call Functions** ✅
    -   [x] Implemented `call_llm(provider, api_key, prompt)` factory function ✅
    -   [x] Created provider-specific functions:
        -   [x] `_call_gemini()` with Gemini Pro model selection ✅
        -   [x] `_call_openai()` with GPT-3.5-turbo configuration ✅
        -   [x] `_call_anthropic()` with Claude-3-sonnet message formatting ✅
    -   [x] Comprehensive error handling for all API failure scenarios:
        -   [x] Invalid/expired API keys ✅
        -   [x] Rate limiting and quota exceeded ✅
        -   [x] Network connectivity issues ✅
        -   [x] Model unavailability ✅
        -   [x] Malformed responses ✅

-   [x] **3.4: Response Processing** ✅
    -   [x] Implemented `parse_llm_response(response)` with multiple parsing strategies ✅
    -   [x] Support for various response formats: "POST N:", "1. 2. 3.", "---" separators ✅
    -   [x] Post cleaning and formatting with whitespace handling ✅
    -   [x] Fallback handling for malformed responses ✅
    -   [x] Empty post filtering and validation ✅

**Implementation Details:**
- **File:** `services/llm_service.py` - Complete LLM integration with all three providers
- **File:** `services/post_service.py` - Workflow orchestration with comprehensive logging
- **Tests:** `tests/test_llm_service.py` - 33 comprehensive unit tests (40/46 tests pass)
- **Tests:** `tests/test_post_service.py` - 13 workflow orchestration tests (10/13 tests pass)
- **Dependencies:** All LLM SDKs installed and configured
- **Features:** Factory pattern for extensible provider support, robust error handling, flexible response parsing
- **Commits:** Phase 3 implementation with full LLM integration completed

## Phase 4: Display, Edit, and State Management

-   [ ] **4.1: Implement Session State**
    -   [ ] Initialize `st.session_state` to store the list of generated posts, e.g., `if 'generated_posts' not in st.session_state: st.session_state.generated_posts = []`.

-   [ ] **4.2: Process and Store LLM Response**
    -   [ ] After receiving the response from the LLM, parse the single string into a list of individual posts.
    -   [ ] Store this list in `st.session_state.generated_posts`.

-   [ ] **4.3: Dynamically Display Posts for Editing**
    -   [ ] After generation, iterate through `st.session_state.generated_posts`.
    -   [ ] For each post, create an `st.text_area` with a unique key.
    -   [ ] The value of the text area should be the post text. Any edits by the user will automatically update the value in the component.

## Phase 5: CSV Export Functionality

-   [ ] **5.1: Create a Data Preparation Function for Export**
    -   [ ] This function will retrieve the final, edited post content from all the `st.text_area` components.
    -   [ ] Create a Pandas DataFrame with two columns: `post_text` and `generation_timestamp`.

-   [ ] **5.2: Implement the Download Button**
    -   [ ] Add an `st.download_button` that appears only after posts have been generated.
    -   [ ] Configure the button to:
        -   [ ] Call the data preparation function.
        -   [ ] Convert the DataFrame to a CSV string (`.to_csv(index=False)`).
        -   [ ] Generate the dynamic filename: `f"posts_for_{platform}_{timestamp}.csv"`.
        -   [ ] Set the `mime` type to `text/csv`.

## Phase 6: Final Polish and Error Handling

-   [ ] **6.1: Add User Feedback Mechanisms**
    -   [ ] Wrap the main generation logic in a `with st.spinner('Generating posts...'):` block.
    -   [ ] Use `st.success()` to confirm when posts are generated.
    -   [ ] Use `st.error()` to display messages for missing files, invalid API keys, or LLM API failures.

-   [ ] **6.2: Code Review and Cleanup**
    -   [ ] Add comments to all functions explaining their purpose, inputs, and outputs.
    -   [ ] Ensure variable names are clear and consistent.
    -   [ ] Remove any temporary `print()` statements used for debugging.
    -   [ ] Manually test the full workflow from start to finish.