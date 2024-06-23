import tempfile
import os
from langchain.document_loaders import PyPDFLoader 
import docx2txt
from pypdf import EmptyFileError  # Make sure to import EmptyFileError
import streamlit as st

def process_uploaded_files(uploaded_files):
    """Processes uploaded files to extract text content."""
    all_text = ""
    for file_info in uploaded_files:
        filename, uploaded_file = file_info
        all_text += extract_text_from_file(uploaded_file) + "\n\n" 
    return all_text

def extract_text_from_file(uploaded_file):
    """Extracts text from different file types with improved error handling."""

    text = ""
    try: 
        if uploaded_file.name.endswith(".pdf"):
            if uploaded_file.size == 0:  # Check for empty file before processing
                st.warning(f"The uploaded PDF '{uploaded_file.name}' is empty. Please upload a valid file.")
                return ""

            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(uploaded_file.read())
                temp_file_path = temp_file.name

            try:
                loader = PyPDFLoader(temp_file_path)
                pages = loader.load_and_split()
                text = "\n\n".join([page.page_content for page in pages])
            except EmptyFileError:
                st.warning(f"The uploaded PDF '{uploaded_file.name}' appears to be empty or corrupted. Please check the file and try again.")
                return ""
            finally:
                os.remove(temp_file_path)  # Ensure file deletion

        elif uploaded_file.name.endswith((".doc", ".docx")):
            text = docx2txt.process(uploaded_file)
        else:
            st.warning(f"Unsupported file type: {uploaded_file.name}")
            return ""
    
    except Exception as e:  # Catch general exceptions during processing
        st.error(f"An error occurred while processing '{uploaded_file.name}': {e}")
        return ""  

    return text