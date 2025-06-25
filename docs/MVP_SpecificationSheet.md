# Auto Post Generator MVP - Technical Specification v1.0

### **1. Project Goal**

To create a locally-run desktop application with a web interface that generates social media posts based on user-provided source material, brand guidelines, and post history. The MVP will focus on core generation and export functionality.

### **2. Core Technology Stack**

* **Application Framework:** Python
* **User Interface:** Streamlit
* **Data Handling:** Pandas
* **File Parsing:** `python-docx` (for .docx), `PyMuPDF`/`pypdf2` (for .pdf)
* **LLM Interaction:** Vendor-specific Python libraries (e.g., `google-generativeai`, `openai`, `anthropic`)

### **3. User Interface (UI) & Workflow**

The application will be a single-page Streamlit interface. The user will perform the following steps in order from top to bottom:

**Step 1: Configure LLM Provider**
* **UI Component:** A dropdown menu labeled "**Select LLM Provider**".
* **Options:** Google Gemini, OpenAI, Anthropic.
* **UI Component:** A password-style text input box labeled "**Enter Your API Key**". This key will be used for the current session only and will not be stored anywhere.

**Step 2: Provide Inputs**
* **UI Component:** A multi-file uploader labeled "**1. Upload Information Source Files**".
    * *Accepted Formats:* `.txt`, `.docx`, `.pdf`, `.md`.
* **UI Component:** A single-file uploader labeled "**2. Upload Brand Guide File**".
    * *Accepted Formats:* `.txt`, `.docx`, `.pdf`, `.md`.
* **UI Component:** A single-file uploader labeled "**3. Upload Previous Posts History**".
    * *Accepted Formats:* `.xlsx`.

**Step 3: Define Generation Parameters**
* **UI Component:** A number input labeled "**4. Number of Posts to Generate**".
* **UI Component:** A dropdown menu labeled "**5. Select Target Platform**".
    * *Options:* X, Facebook, LinkedIn, Instagram.

**Step 4: Generate**
* **UI Component:** A primary button labeled "**Generate Posts**".
* **Action:** Clicking this button will trigger the backend to read all files and call the selected LLM API. A loading spinner will be displayed during this process.

**Step 5: Preview, Edit, and Export**
* This section appears only after posts are generated.
* **UI Component:** For each generated post, a multi-line text area will be displayed, pre-filled with the AI-generated text. The user can **directly edit the text** in these boxes to make refinements.
* **UI Component:** A download button labeled "**Export to CSV**".
    * **Action:** When clicked, it will generate and download a CSV file containing the final (edited) posts.

### **4. Backend Logic**

1.  **File Handling:** The backend will read the uploaded files into memory. It will extract plain text from all source documents and the brand guide. It will use Pandas to read the `Post Text` and `Timestamp` columns from the `previous posts` XLSX file.
2.  **Prompt Engineering:** Upon clicking "Generate Posts," the system will dynamically construct a detailed prompt for the LLM. The prompt will be structured to define the role/persona, provide past post examples, include the new source information, and give a clear command to generate a specific number of posts for the target platform.
3.  **LLM API Call:** The system will use the selected provider's Python library to send the prompt and the user's API key to the LLM.
4.  **Parsing Response:** The LLM's response will be parsed to separate the generated text into individual posts.
5.  **State Management:** The list of generated posts will be stored in Streamlit's session state, allowing them to be displayed for editing and later retrieved for export.

### **5. Output Specification**

* **Format:** CSV (Comma-Separated Values).
* **Filename Convention:** The filename will be dynamically generated based on the target platform and the current date.
    * *Example:* `posts_for_LinkedIn_20250625.csv`
* **Columns:**
    * `post_text`: The final, user-edited version of the post.
    * `generation_timestamp`: The date and time the CSV was exported.