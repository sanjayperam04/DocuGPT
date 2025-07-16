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

# Clean ChatGPT-style CSS
st.markdown("""
<style>
    /* Hide Streamlit elements */
    .stDeployButton, .stDecoration, .stToolbar, .stMainBlockContainer > div:first-child {
        display: none !important;
    }
    
    /* Main app styling */
    .stApp {
        background-color: #212121;
        color: #ffffff;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    
    /* Header */
    .main-header {
        background: #343541;
        padding: 1rem 2rem;
        border-bottom: 1px solid #4d4d4f;
        position: sticky;
        top: 0;
        z-index: 100;
    }
    
    .header-content {
        max-width: 800px;
        margin: 0 auto;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .header-title {
        font-size: 1.5rem;
        font-weight: 600;
        color: #ffffff;
    }
    
    .header-actions {
        display: flex;
        gap: 1rem;
    }
    
    .header-btn {
        background: #40414f;
        color: #ffffff;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 6px;
        cursor: pointer;
        font-size: 0.9rem;
        transition: background-color 0.2s;
    }
    
    .header-btn:hover {
        background: #565869;
    }
    
    /* Chat container */
    .chat-container {
        max-width: 800px;
        margin: 0 auto;
        padding: 2rem 1rem;
        min-height: 70vh;
    }
    
    /* Messages */
    .message {
        margin-bottom: 2rem;
        display: flex;
        gap: 1rem;
        align-items: flex-start;
    }
    
    .message-avatar {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1rem;
        font-weight: 600;
        flex-shrink: 0;
    }
    
    .user-avatar {
        background: #10a37f;
        color: white;
    }
    
    .assistant-avatar {
        background: #ab68ff;
        color: white;
    }
    
    .message-content {
        flex: 1;
        line-height: 1.6;
        color: #ffffff;
    }
    
    .message-content p {
        margin: 0 0 1rem 0;
    }
    
    .message-content pre {
        background: #2d2d2d;
        padding: 1rem;
        border-radius: 6px;
        overflow-x: auto;
        margin: 1rem 0;
    }
    
    .message-content code {
        background: #2d2d2d;
        padding: 0.2rem 0.4rem;
        border-radius: 4px;
    }
    
    /* Welcome screen */
    .welcome-container {
        max-width: 600px;
        margin: 4rem auto;
        text-align: center;
        padding: 2rem;
    }
    
    .welcome-title {
        font-size: 2.5rem;
        font-weight: 600;
        margin-bottom: 1rem;
        color: #ffffff;
    }
    
    .welcome-subtitle {
        font-size: 1.2rem;
        color: #8e8ea0;
        margin-bottom: 3rem;
    }
    
    .example-prompts {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 1rem;
        margin-bottom: 2rem;
    }
    
    .example-prompt {
        background: #343541;
        border: 1px solid #4d4d4f;
        border-radius: 8px;
        padding: 1.5rem;
        cursor: pointer;
        transition: all 0.2s;
        text-align: left;
    }
    
    .example-prompt:hover {
        background: #40414f;
        border-color: #10a37f;
    }
    
    .example-prompt-title {
        font-weight: 600;
        color: #ffffff;
        margin-bottom: 0.5rem;
        font-size: 1rem;
    }
    
    .example-prompt-text {
        color: #8e8ea0;
        font-size: 0.9rem;
    }
    
    /* Input section */
    .input-section {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: #212121;
        padding: 1rem 2rem 2rem;
        border-top: 1px solid #4d4d4f;
    }
    
    .input-container {
        max-width: 800px;
        margin: 0 auto;
        position: relative;
    }
    
    .input-wrapper {
        background: #343541;
        border: 1px solid #4d4d4f;
        border-radius: 12px;
        padding: 1rem;
        display: flex;
        align-items: end;
        gap: 0.75rem;
        transition: border-color 0.2s;
    }
    
    .input-wrapper:focus-within {
        border-color: #10a37f;
    }
    
    .stTextInput > div > div > input {
        background: transparent !important;
        border: none !important;
        color: #ffffff !important;
        font-size: 1rem !important;
        padding: 0 !important;
        outline: none !important;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: #8e8ea0 !important;
    }
    
    .stTextInput > div {
        border: none !important;
    }
    
    .stTextInput {
        flex: 1;
    }
    
    .stButton > button {
        background: #10a37f !important;
        color: white !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 600 !important;
        cursor: pointer !important;
        transition: background-color 0.2s !important;
    }
    
    .stButton > button:hover {
        background: #0d8c6a !important;
    }
    
    .stButton > button:disabled {
        background: #4d4d4f !important;
        cursor: not-allowed !important;
    }
    
    /* File uploader */
    .stFileUploader {
        background: #343541;
        border: 1px solid #4d4d4f;
        border-radius: 8px;
        padding: 2rem;
        text-align: center;
        margin: 2rem 0;
    }
    
    .stFileUploader > div {
        border: none !important;
    }
    
    .stFileUploader button {
        background: #10a37f !important;
        color: white !important;
        border: none !important;
        padding: 0.75rem 1.5rem !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
    }
    
    /* Success/Error messages */
    .stSuccess {
        background: rgba(16, 163, 127, 0.1) !important;
        border: 1px solid #10a37f !important;
        color: #10a37f !important;
    }
    
    .stError {
        background: rgba(239, 68, 68, 0.1) !important;
        border: 1px solid #ef4444 !important;
        color: #ef4444 !important;
    }
    
    /* Spinner */
    .stSpinner {
        color: #10a37f !important;
    }
    
    /* Upload modal */
    .upload-modal {
        background: #343541;
        border: 1px solid #4d4d4f;
        border-radius: 12px;
        padding: 2rem;
        margin: 2rem 0;
    }
    
    .upload-modal h3 {
        color: #ffffff;
        margin-bottom: 1rem;
    }
    
    .document-info {
        background: #2d2d2d;
        padding: 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .info-item {
        display: flex;
        justify-content: space-between;
        margin-bottom: 0.5rem;
        color: #8e8ea0;
    }
    
    .info-value {
        color: #ffffff;
        font-weight: 500;
    }
    
    /* Mobile responsive */
    @media (max-width: 768px) {
        .main-header {
            padding: 1rem;
        }
        
        .header-content {
            flex-direction: column;
            gap: 1rem;
        }
        
        .chat-container {
            padding: 1rem;
        }
        
        .input-section {
            padding: 1rem;
        }
        
        .example-prompts {
            grid-template-columns: 1fr;
        }
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

def display_header():
    """Display header"""
    st.markdown("""
    <div class="main-header">
        <div class="header-content">
            <div class="header-title">🤖 DocuGPT</div>
            <div class="header-actions">
                <button class="header-btn" onclick="showUpload()">📄 Upload</button>
                <button class="header-btn" onclick="clearChat()">🗑️ Clear</button>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def display_welcome_screen():
    """Display welcome screen"""
    st.markdown("""
    <div class="welcome-container">
        <div class="welcome-title">Welcome to DocuGPT</div>
        <div class="welcome-subtitle">Upload a PDF document and start having intelligent conversations</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Example prompts
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📄 What is this document about?", key="ex1", use_container_width=True):
            st.session_state.example_query = "What is this document about?"
            st.rerun()
            
        if st.button("✨ What are the main features?", key="ex2", use_container_width=True):
            st.session_state.example_query = "What are the main features?"
            st.rerun()
    
    with col2:
        if st.button("🚀 How do I get started?", key="ex3", use_container_width=True):
            st.session_state.example_query = "How do I get started?"
            st.rerun()
            
        if st.button("📚 Show me examples", key="ex4", use_container_width=True):
            st.session_state.example_query = "Show me examples"
            st.rerun()

def display_upload_section():
    """Display upload section"""
    st.markdown("""
    <div class="upload-modal">
        <h3>📄 Upload PDF Document</h3>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=['pdf'],
        help=f"Maximum file size: {Config.MAX_FILE_SIZE}MB"
    )
    
    if uploaded_file is not None:
        file_size = len(uploaded_file.getvalue()) / (1024 * 1024)
        
        if file_size > Config.MAX_FILE_SIZE:
            st.error(f"File size ({file_size:.1f}MB) exceeds maximum allowed size ({Config.MAX_FILE_SIZE}MB)")
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
                        st.session_state.show_upload = False
                        st.success("✅ Document processed successfully!")
                        st.rerun()
                    
                except Exception as e:
                    st.error(f"Error processing document: {str(e)}")

def display_chat_messages():
    """Display chat messages"""
    if st.session_state.messages:
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f"""
                <div class="message">
                    <div class="message-avatar user-avatar">U</div>
                    <div class="message-content">
                        {message["content"]}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="message">
                    <div class="message-avatar assistant-avatar">🤖</div>
                    <div class="message-content">
                        {message["content"]}
                    </div>
                </div>
                """, unsafe_allow_html=True)

def display_document_info():
    """Display document information"""
    if st.session_state.current_document:
        doc = st.session_state.current_document
        st.markdown(f"""
        <div class="document-info">
            <h3>📋 Document Information</h3>
            <div class="info-item">
                <span>Title:</span>
                <span class="info-value">{doc['metadata']['title']}</span>
            </div>
            <div class="info-item">
                <span>Pages:</span>
                <span class="info-value">{doc['metadata']['total_pages']}</span>
            </div>
            <div class="info-item">
                <span>Sections:</span>
                <span class="info-value">{len(doc['sections'])}</span>
            </div>
            <div class="info-item">
                <span>Chunks:</span>
                <span class="info-value">{len(st.session_state.rag_engine.chunks)}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

def display_chat_input():
    """Display chat input"""
    st.markdown("""
    <div class="input-section">
        <div class="input-container">
            <div class="input-wrapper">
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([6, 1])
    
    with col1:
        user_input = st.text_input(
            "Message",
            placeholder="Message DocuGPT...",
            label_visibility="collapsed",
            key="chat_input"
        )
    
    with col2:
        send_button = st.button("Send", type="primary", use_container_width=True)
    
    st.markdown("""
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Handle example queries
    if 'example_query' in st.session_state:
        user_input = st.session_state.example_query
        send_button = True
        del st.session_state.example_query
    
    # Handle message sending
    if send_button and user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        if st.session_state.document_processed:
            with st.spinner("DocuGPT is thinking..."):
                try:
                    response = st.session_state.chat_agent.generate_response(user_input)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        else:
            st.session_state.messages.append({
                "role": "assistant", 
                "content": "Please upload a PDF document first so I can help you with your questions."
            })
        
        st.rerun()

def main():
    """Main application function"""
    initialize_session_state()
    
    # Display header
    display_header()
    
    # Main content area
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    # Show upload section if requested or no document
    if st.session_state.show_upload or not st.session_state.document_processed:
        display_upload_section()
    
    # Show document info if available
    if st.session_state.document_processed:
        display_document_info()
    
    # Show welcome screen or chat messages
    if not st.session_state.document_processed and not st.session_state.show_upload:
        display_welcome_screen()
    else:
        display_chat_messages()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Chat input (always visible)
    display_chat_input()
    
    # Add bottom padding
    st.markdown('<div style="height: 120px;"></div>', unsafe_allow_html=True)
    
    # Handle header button clicks
    if st.button("Show Upload", key="show_upload_btn", help="Upload PDF"):
        st.session_state.show_upload = True
        st.rerun()
    
    if st.button("Clear Chat", key="clear_chat_btn", help="Clear conversation"):
        st.session_state.messages = []
        st.session_state.chat_agent.conversation_history = []
        st.rerun()

if __name__ == "__main__":
    main()
