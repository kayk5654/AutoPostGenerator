def extract_text_from_uploads(uploaded_files: list) -> str:
    """
    Extract text from uploaded files.
    
    Args:
        uploaded_files: List of Streamlit UploadedFile objects
        
    Returns:
        str: Concatenated text content from all files
    """
    if not uploaded_files:
        return ""
    
    extracted_texts = []
    
    for file in uploaded_files:
        file_extension = file.name.lower().split('.')[-1]
        
        if file_extension in ['txt', 'md']:
            text = _read_txt_file(file)
        elif file_extension == 'docx':
            text = _read_docx_file(file)
        elif file_extension == 'pdf':
            text = _read_pdf_file(file)
        else:
            raise ValueError(f"Unsupported file type: .{file_extension}")
        
        extracted_texts.append(text)
    
    return "\n\n".join(extracted_texts)


def extract_posts_from_history(history_file) -> list[str]:
    """
    Extract post text from Excel history file.
    
    Args:
        history_file: Streamlit UploadedFile object (.xlsx)
        
    Returns:
        list[str]: List of post text strings from history
    """
    import pandas as pd
    import io
    
    # Read the Excel file using pandas
    file_content = history_file.read()
    df = pd.read_excel(io.BytesIO(file_content))
    
    # Handle empty file
    if df.empty:
        return []
    
    # Check if required columns exist
    if 'Post Text' not in df.columns:
        raise KeyError("Required column 'Post Text' not found in Excel file")
    
    # Extract the post text column and convert to list
    posts = df['Post Text'].tolist()
    
    return posts


def _read_txt_file(file) -> str:
    """Read plain text files (.txt, .md)"""
    content = file.read()
    
    # Handle both bytes and string content
    if isinstance(content, bytes):
        try:
            return content.decode('utf-8')
        except UnicodeDecodeError:
            # Try with different encodings if UTF-8 fails
            try:
                return content.decode('latin-1')
            except UnicodeDecodeError:
                return content.decode('ascii', errors='ignore')
    
    return content


def _read_docx_file(file) -> str:
    """Read Word documents using python-docx"""
    from docx import Document
    import io
    
    # Read the file content into BytesIO
    file_content = file.read()
    doc_stream = io.BytesIO(file_content)
    
    # Load the document
    doc = Document(doc_stream)
    
    # Extract text from paragraphs
    paragraphs = []
    for paragraph in doc.paragraphs:
        if paragraph.text.strip():
            paragraphs.append(paragraph.text)
    
    # Extract text from tables
    for table in doc.tables:
        for row in table.rows:
            row_text = []
            for cell in row.cells:
                if cell.text.strip():
                    row_text.append(cell.text.strip())
            if row_text:
                paragraphs.append(" | ".join(row_text))
    
    return "\n".join(paragraphs)


def _read_pdf_file(file) -> str:
    """Read PDF files using PyMuPDF/fitz"""
    import fitz  # PyMuPDF
    import io
    
    # Read the file content
    file_content = file.read()
    
    # Open the PDF from bytes
    pdf_document = fitz.open(stream=file_content, filetype="pdf")
    
    # Check if the document requires a password
    if pdf_document.needs_pass:
        pdf_document.close()
        raise Exception("PDF file is password protected")
    
    # Extract text from all pages
    text_content = []
    for page_num in range(pdf_document.page_count):
        page = pdf_document[page_num]
        text = page.get_text()
        if text.strip():
            text_content.append(text.strip())
    
    pdf_document.close()
    
    return "\n\n".join(text_content)