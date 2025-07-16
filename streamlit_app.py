import streamlit as st
import tempfile
import os
from datetime import datetime

from config import Config
from utils.pdf_processor import AdvancedPDFProcessor
from core.rag_engine import OptimizedRAGEngine
from core.chat_agent import AdvancedChatAgent

# Page configuration
st.set_page_config(
    page_title=Config.PAGE_TITLE,
    page_icon=Config.PAGE_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Light mode optimized CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Light mode optimized background */
    .stApp {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        font-family: 'Inter', sans-serif;
    }
    
    /* Header with better contrast for light mode */
    .main-header {
        background: linear-gradient(135deg, #495057 0%, #6c757d 100%);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem 0;
        text-align: center;
        color: white;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        border: 1px solid #dee2e6;
    }
    
    .logo-text {
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        color: #ffffff;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
    }
    
    .tagline {
        font-size: 1.2rem;
        font-weight: 400;
        color: #f8f9fa;
        margin-bottom: 1rem;
    }
    
    .feature-badges {
        display: flex;
        justify-content: center;
        gap: 1rem;
        flex-wrap: wrap;
    }
    
    .badge {
        background: rgba(255, 255, 255, 0.9);
        color: #495057;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 600;
        border: 1px solid #dee2e6;
        margin: 0.25rem;
    }
    
    /* Main content with proper light mode colors */
    .main-content {
        background: #ffffff;
        border-radius: 20px;
        margin: 2rem 0;
        padding: 2rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        border: 1px solid #e9ecef;
    }
    
    /* Sidebar with light mode optimization */
    .upload-area {
        background: #ffffff;
        border: 2px dashed #6c757d;
        border-radius: 15px;
        padding: 2rem;
        text-align: center;
        margin: 1rem 0;
        transition: all 0.3s ease;
    }
    
    .upload-area:hover {
        border-color: #495057;
        background: #f8f9fa;
    }
    
    .doc-info {
        background: linear-gradient(135deg, #495057 0%, #6c757d 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }
    
    .info-row {
        display: flex;
        justify-content: space-between;
        margin: 0.5rem 0;
        padding: 0.5rem 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.3);
    }
    
    .info-row:last-child {
        border-bottom: none;
    }
    
    /* Chat interface with high contrast */
    .chat-container {
        background: #f8f9fa;
        border-radius: 15px;
        padding: 2rem;
        margin: 1rem 0;
        min-height: 400px;
        border: 1px solid #e9ecef;
    }
    
    .message-user {
        background: linear-gradient(135deg, #495057 0%, #6c757d 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 18px 18px 5px 18px;
        margin: 1rem 0;
        margin-left: 3rem;
        box-shadow: 0 4px 15px rgba(73, 80, 87, 0.3);
        font-weight: 500;
    }
    
    .message-assistant {
        background: #ffffff;
        color: #212529;
        padding: 1rem 1.5rem;
        border-radius: 18px 18px 18px 5px;
        margin: 1rem 0;
        margin-right: 3rem;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        border-left: 4px solid #495057;
        border: 1px solid #e9ecef;
    }
    
    /* Feature cards with better visibility */
    .feature-card {
        background: #ffffff;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        text-align: center;
        margin: 1rem 0;
        transition: transform 0.3s ease;
        border: 1px solid #e9ecef;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
    }
    
    .feature-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
    }
    
    .feature-title {
        font-size: 1.3rem;
        font-weight: 600;
        color: #212529;
        margin-bottom: 1rem;
    }
    
    .feature-description {
        color: #495057;
        line-height: 1.6;
        font-weight: 400;
    }
    
    /* Welcome section with dark text */
    .welcome-container {
        text-align: center;
        padding: 3rem 1rem;
    }
    
    .welcome-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #212529;
        margin-bottom: 1rem;
    }
    
    .welcome-subtitle {
        font-size: 1.2rem;
        color: #495057;
        margin-bottom: 2rem;
        font-weight: 400;
    }
    
    /* Button styling for light mode */
    .stButton > button {
        background: linear-gradient(45deg, #495057, #6c757d);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
    
    .stButton > button:hover {
        background: linear-gradient(45deg, #343a40, #495057);
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }
    
    /* Input field styling */
    .stTextInput > div > div > input {
        background: #ffffff;
        border: 2px solid #e9ecef;
        border-radius: 10px;
        color: #212529;
        font-weight: 500;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #495057;
        box-shadow: 0 0 0 0.2rem rgba(73, 80, 87, 0.25);
    }
    
    /* Sidebar text colors */
    .stSidebar {
        background: #ffffff;
    }
    
    .stSidebar [data-testid="stSidebarNav"] {
        background: #f8f9fa;
    }
    
    /* Success and error messages */
    .stSuccess {
        background: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
    }
    
    .stError {
        background: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
    }
    
    /* Hide Streamlit elements */
    .stDeployButton {
        display: none;
    }
    
    .stDecoration {
        display: none;
    }
    
    .stToolbar {
        display: none !important;
    }
    
    /* File uploader styling */
    .stFileUploader > div > button {
        background: linear-gradient(45deg, #495057, #6c757d);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 1.5rem;
        font-weight: 500;
    }
    
    .stFileUploader > div > button:hover {
        background: linear-gradient(45deg, #343a40, #495057);
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

def display_header():
    """Display main header"""
    st.markdown("""
    <div class="main-header">
        <div class="logo-text">🤖 DocuGPT</div>
        <div class="tagline">Transform Your Documents Into Interactive AI Assistants</div>
        <div class="feature-badges">
            <span class="badge">🚀 AI-Powered</span>
            <span class="badge">📄 PDF Processing</span>
            <span class="badge">💬 Interactive Chat</span>
            <span class="badge">⚡ Instant Answers</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def display_sidebar():
    """Display sidebar with document upload and controls"""
    with st.sidebar:
        st.markdown("""
        <div class="upload-area">
            <h3 style="color: #2c3e50;">📄 Upload Document</h3>
            <p style="color: #6c757d;">Upload your PDF to get started</p>
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "Choose a PDF file",
            type=['pdf'],
            help=f"Maximum file size: {Config.MAX_FILE_SIZE}MB",
            label_visibility="collapsed"
        )
        
        if uploaded_file is not None:
            file_size = len(uploaded_file.getvalue()) / (1024 * 1024)
            
            if file_size > Config.MAX_FILE_SIZE:
                st.error(f"📋 File size ({file_size:.1f}MB) exceeds maximum allowed size ({Config.MAX_FILE_SIZE}MB)")
                return
            
            st.success(f"✅ File loaded: {file_size:.1f}MB")
            
            if st.button("🚀 Process Document", type="primary", use_container_width=True):
                with st.spinner("Processing document..."):
                    try:
                        document_data = st.session_state.pdf_processor.extract_text_with_structure(uploaded_file)
                        
                        if document_data:
                            chunks = st.session_state.pdf_processor.create_intelligent_chunks(document_data)
                            st.session_state.rag_engine.create_embeddings(chunks)
                            st.session_state.chat_agent.set_document(document_data)
                            st.session_state.current_document = document_data
                            st.session_state.document_processed = True
                            st.session_state.messages = []
                            
                            st.success("✅ Document processed successfully!")
                            st.rerun()
                        
                    except Exception as e:
                        st.error(f"Error processing document: {str(e)}")
        
        # Document information
        if st.session_state.document_processed and st.session_state.current_document:
            doc = st.session_state.current_document
            
            st.markdown(f"""
            <div class="doc-info">
                <h3 style="text-align: center; margin-bottom: 1rem;">📋 Document Information</h3>
                <div class="info-row">
                    <strong>Title:</strong>
                    <span>{doc['metadata']['title']}</span>
                </div>
                <div class="info-row">
                    <strong>Pages:</strong>
                    <span>{doc['metadata']['total_pages']}</span>
                </div>
                <div class="info-row">
                    <strong>Sections:</strong>
                    <span>{len(doc['sections'])}</span>
                </div>
                <div class="info-row">
                    <strong>Chunks:</strong>
                    <span>{len(st.session_state.rag_engine.chunks)}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Quick actions
            st.markdown("### ⚡ Quick Actions")
            
            quick_questions = [
                "What is this document about?",
                "How do I get started?",
                "What are the main features?",
                "Show me examples"
            ]
            
            for question in quick_questions:
                if st.button(question, key=f"quick_{question}", use_container_width=True):
                    st.session_state.messages.append({"role": "user", "content": question})
                    response = st.session_state.chat_agent.generate_response(question)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    st.rerun()

def display_chat_interface():
    """Display chat interface"""
    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    
    if not st.session_state.document_processed:
        st.markdown("""
        <div class="welcome-container">
            <div class="welcome-title">Welcome to DocuGPT</div>
            <div class="welcome-subtitle">Upload a PDF document to start having intelligent conversations with your content</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Feature cards using columns
        st.markdown("### ✨ Key Features")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">🤖</div>
                <div class="feature-title">AI-Powered Intelligence</div>
                <div class="feature-description">Advanced AI understands your documents and provides contextual answers</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">⚡</div>
                <div class="feature-title">Instant Responses</div>
                <div class="feature-description">Get immediate answers to your questions without manual searching</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">📄</div>
                <div class="feature-title">Smart Processing</div>
                <div class="feature-description">Handles complex documents with intelligent chunking and analysis</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    # Chat interface
    st.markdown("## 💬 Chat with Your Document")
    
    # Display chat messages
    if st.session_state.messages:
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f"""
                <div class="message-user">
                    <strong>You:</strong> {message["content"]}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="message-assistant">
                    <strong>DocuGPT:</strong> {message["content"]}
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Chat input
    user_input = st.text_input(
        "Ask your question:",
        placeholder="Type your question about the document here...",
        key="user_input"
    )
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if st.button("💬 Send Message", type="primary", use_container_width=True):
            if user_input.strip():
                st.session_state.messages.append({"role": "user", "content": user_input})
                
                with st.spinner("DocuGPT is thinking..."):
                    try:
                        response = st.session_state.chat_agent.generate_response(user_input)
                        st.session_state.messages.append({"role": "assistant", "content": response})
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error generating response: {str(e)}")
    
    with col2:
        if st.button("🧹 Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.chat_agent.conversation_history = []
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def main():
    """Main application function"""
    initialize_session_state()
    display_header()
    display_sidebar()
    display_chat_interface()

if __name__ == "__main__":
    main()
