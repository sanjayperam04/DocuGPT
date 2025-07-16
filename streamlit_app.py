import streamlit as st
from config import Config
from utils.pdf_processor import AdvancedPDFProcessor
from core.rag_engine import OptimizedRAGEngine
from core.chat_agent import AdvancedChatAgent

# Page configuration
st.set_page_config(
    page_title="DocuGPT",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Inject CSS that actually works with Streamlit
st.markdown("""
<style>
    .stApp {
        background-color: #212121 !important;
    }
    
    .main .block-container {
        padding-top: 0 !important;
        padding-bottom: 0 !important;
        max-width: 100% !important;
    }
    
    .stDeployButton {
        display: none !important;
    }
    
    .stDecoration {
        display: none !important;
    }
    
    .stToolbar {
        display: none !important;
    }
    
    .stMainBlockContainer {
        padding: 0 !important;
    }
    
    .stApp > header {
        display: none !important;
    }
    
    .stApp > div:first-child {
        display: none !important;
    }
    
    body {
        background-color: #212121 !important;
        color: #ffffff !important;
    }
    
    .chatgpt-header {
        background-color: #343541;
        padding: 1rem 2rem;
        border-bottom: 1px solid #4e4e4e;
        color: white;
        font-size: 1.5rem;
        font-weight: 600;
        text-align: center;
    }
    
    .chat-message {
        display: flex;
        gap: 1rem;
        margin-bottom: 1.5rem;
        padding: 1rem;
        background-color: #343541;
        border-radius: 8px;
        color: white;
    }
    
    .message-avatar {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        background-color: #10a37f;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        flex-shrink: 0;
    }
    
    .assistant-avatar {
        background-color: #ab68ff;
    }
    
    .message-content {
        flex: 1;
        line-height: 1.5;
    }
    
    .welcome-section {
        text-align: center;
        padding: 4rem 2rem;
        color: white;
    }
    
    .welcome-title {
        font-size: 2.5rem;
        margin-bottom: 1rem;
        color: white;
    }
    
    .welcome-subtitle {
        font-size: 1.2rem;
        color: #8e8ea0;
        margin-bottom: 2rem;
    }
    
    .stButton button {
        background-color: #10a37f !important;
        color: white !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 600 !important;
        width: 100% !important;
    }
    
    .stButton button:hover {
        background-color: #0d8c6a !important;
    }
    
    .stTextInput input {
        background-color: #40414f !important;
        border: 1px solid #565869 !important;
        color: white !important;
        border-radius: 8px !important;
        padding: 1rem !important;
    }
    
    .stFileUploader {
        background-color: #343541 !important;
        border: 1px solid #565869 !important;
        border-radius: 8px !important;
        padding: 2rem !important;
    }
    
    .stFileUploader label {
        color: white !important;
    }
    
    .stSuccess {
        background-color: rgba(16, 163, 127, 0.2) !important;
        border: 1px solid #10a37f !important;
        color: #10a37f !important;
    }
    
    .stError {
        background-color: rgba(239, 68, 68, 0.2) !important;
        border: 1px solid #ef4444 !important;
        color: #ef4444 !important;
    }
    
    .stSpinner {
        color: #10a37f !important;
    }
    
    .chat-container {
        max-width: 800px;
        margin: 0 auto;
        padding: 2rem 1rem;
        min-height: 60vh;
    }
    
    .input-container {
        max-width: 800px;
        margin: 0 auto;
        padding: 1rem;
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background-color: #212121;
        border-top: 1px solid #4e4e4e;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'pdf_processor' not in st.session_state:
        st.session_state.pdf_processor = AdvancedPDFProcessor()
    
    if 'rag_engine' not in st.session_state:
        st.session_state.rag_engine = OptimizedRAGEngine()
    
    if 'chat_agent' not in st.session_state:
        st.session_state.chat_agent = AdvancedChatAgent(st.session_state.rag_engine)
    
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    if 'document_processed' not in st.session_state:
        st.session_state.document_processed = False
    
    if 'current_document' not in st.session_state:
        st.session_state.current_document = None
    
    if 'show_upload' not in st.session_state:
        st.session_state.show_upload = False

def main():
    """Main application function"""
    initialize_session_state()
    
    # Header
    st.markdown('<div class="chatgpt-header">🤖 DocuGPT</div>', unsafe_allow_html=True)
    
    # Main content container
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    # Show upload section if no document is processed
    if not st.session_state.document_processed:
        st.markdown("""
        <div class="welcome-section">
            <h1 class="welcome-title">Welcome to DocuGPT</h1>
            <p class="welcome-subtitle">Upload a PDF document to start having intelligent conversations</p>
        </div>
        """, unsafe_allow_html=True)
        
        # File upload
        uploaded_file = st.file_uploader(
            "Choose a PDF file",
            type=['pdf'],
            help="Upload your PDF document"
        )
        
        if uploaded_file is not None:
            file_size = len(uploaded_file.getvalue()) / (1024 * 1024)
            st.success(f"✅ File loaded: {file_size:.1f}MB")
            
            if st.button("🚀 Process Document"):
                with st.spinner("Processing document..."):
                    try:
                        document_data = st.session_state.pdf_processor.extract_text_with_structure(uploaded_file)
                        
                        if document_data:
                            chunks = st.session_state.pdf_processor.create_intelligent_chunks(document_data)
                            st.session_state.rag_engine.create_embeddings(chunks)
                            st.session_state.chat_agent.set_document(document_data)
                            st.session_state.current_document = document_data
                            st.session_state.document_processed = True
                            st.success("✅ Document processed successfully!")
                            st.rerun()
                        
                    except Exception as e:
                        st.error(f"Error processing document: {str(e)}")
    
    # Show chat messages if document is processed
    if st.session_state.document_processed:
        # Display messages
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f"""
                <div class="chat-message">
                    <div class="message-avatar">U</div>
                    <div class="message-content">{message["content"]}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-message">
                    <div class="message-avatar assistant-avatar">🤖</div>
                    <div class="message-content">{message["content"]}</div>
                </div>
                """, unsafe_allow_html=True)
        
        # Document info
        if st.session_state.current_document:
            doc = st.session_state.current_document
            st.info(f"📄 Document: {doc['metadata']['title']} | Pages: {doc['metadata']['total_pages']} | Sections: {len(doc['sections'])}")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Chat input at bottom
    st.markdown('<div class="input-container">', unsafe_allow_html=True)
    
    col1, col2 = st.columns([6, 1])
    
    with col1:
        user_input = st.text_input(
            "",
            placeholder="Message DocuGPT...",
            key="chat_input",
            label_visibility="collapsed"
        )
    
    with col2:
        send_button = st.button("Send")
    
    if send_button and user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        if st.session_state.document_processed:
            with st.spinner("Thinking..."):
                try:
                    response = st.session_state.chat_agent.generate_response(user_input)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        else:
            st.session_state.messages.append({
                "role": "assistant", 
                "content": "Please upload a PDF document first."
            })
        
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Add some padding at bottom
    st.markdown('<div style="height: 120px;"></div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
