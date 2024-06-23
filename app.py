import streamlit as st
import os
import io
import tempfile
import docx2txt
from langchain_community.document_loaders import PyPDFLoader 
from ai_functions import analyze_syllabus, generate_roadmap, get_answer_and_explanation
from dotenv import load_dotenv

load_dotenv()
def process_uploaded_files(uploaded_files):
    """Processes uploaded files to extract text content."""
    all_text = ""
    for file_info in uploaded_files:
        filename, uploaded_file = file_info
        all_text += extract_text_from_file(uploaded_file) + "\n\n" 
    return all_text

def extract_text_from_file(uploaded_file):
    """Extracts text from different file types."""
    text = ""
    try:
        if uploaded_file.name.endswith(".pdf"):
            if uploaded_file.size == 0:
                st.warning(f"The uploaded PDF '{uploaded_file.name}' is empty. Please upload a valid file.")
                return ""

            # Read PDF content into an in-memory BytesIO object
            pdf_content = io.BytesIO(uploaded_file.read())

            try:
                loader = PyPDFLoader(pdf_content)  # Use BytesIO object directly
                pages = loader.load_and_split()
                text = "\n\n".join([page.page_content for page in pages])
            except:
                st.warning(f"The uploaded PDF '{uploaded_file.name}' appears to be empty or corrupted. Please check the file and try again.")
                return ""

        elif uploaded_file.name.endswith((".doc", ".docx")):
            # For DOCX, you still need to process the file object
            text = docx2txt.process(uploaded_file) 
        else:
            st.warning(f"Unsupported file type: {uploaded_file.name}")
            return ""

    except Exception as e:
        st.error(f"An error occurred while processing '{uploaded_file.name}': {e}")
        return ""

    return text



# --- Google Gemini Pro API Configuration --- (Keep in app.py)
os.environ["GOOGLE_CLOUD_PROJECT"] = "studybuddy-427219"
from google.oauth2 import service_account
credentials = service_account.Credentials.from_service_account_file(
    'C:/Users/spunk/CODEITBITCH 2.0/tutorAI/state.json'
)

# --- Streamlit Setup ---
st.set_page_config(page_title="AI Study Buddy", page_icon=":books:", layout="wide")

# --- Global Variables and State ---
if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files = []
if 'syllabus_analysis' not in st.session_state:
    st.session_state.syllabus_analysis = None
if 'roadmap' not in st.session_state:
    st.session_state.roadmap = None

# --- Sidebar --- 
st.sidebar.title("Study Material Upload")
uploaded_files = st.sidebar.file_uploader(
    "Upload course materials (PDF/DOC)", 
    type=["pdf", "doc", "docx"], 
    accept_multiple_files=True
)
create_chatbot_button = st.sidebar.button("Create Chatbot")

# --- Main Content Area ---
st.title("Your AI Study Companion")

# --- 1. File Upload and Processing --- 
if uploaded_files:
    for uploaded_file in uploaded_files:
        if uploaded_file.name not in [file_info[0] for file_info in st.session_state.uploaded_files]:
            st.session_state.uploaded_files.append((uploaded_file.name, uploaded_file))

    # --- Option to Upload Syllabus ---
    upload_syllabus = st.checkbox("Do you want to upload a syllabus?")
    if upload_syllabus:
        uploaded_syllabus = st.file_uploader("Upload Syllabus (PDF/DOC)", type=["pdf", "doc", "docx"])
        if uploaded_syllabus:
            syllabus_text = extract_text_from_file(uploaded_syllabus)
            if syllabus_text:
                try:
                    with st.spinner("Analyzing syllabus..."):
                        st.session_state.syllabus_analysis = analyze_syllabus(syllabus_text, credentials)
                        st.success("Syllabus analyzed!")
                except Exception as e:
                    st.error(f"An error occurred while analyzing the syllabus: {e}")

# --- 2. Chatbot Creation ---
if create_chatbot_button:
    if st.session_state.uploaded_files:
        with st.spinner("Creating your chatbot..."):
            all_text = process_uploaded_files(st.session_state.uploaded_files)

            # --- (Optional) Roadmap Generation ---
            if st.session_state.syllabus_analysis:
                try:
                    with st.spinner("Generating roadmap..."): 
                        st.session_state.roadmap = generate_roadmap(
                            st.session_state.syllabus_analysis,
                            all_text,
                            credentials
                        )
                        st.success("Roadmap generated!")
                        st.write(st.session_state.roadmap)  # Display the roadmap
                except Exception as e:
                    st.error(f"An error occurred while generating the roadmap: {e}")
        st.success("Chatbot ready!")

        # --- 3. Chat Interface --- 
        st.header("Ask Your Study Questions")
        user_question = st.text_input("Your Question:")
        if user_question:
            try: 
                with st.spinner("Thinking..."):
                    response = get_answer_and_explanation(
                        user_question, all_text, credentials
                    )
                    st.write("Chatbot:", response)
            except Exception as e:
                st.error(f"An error occurred while processing your question: {e}") 
    else:
        st.info("Please upload at least one course material file.")