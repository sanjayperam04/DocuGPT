import streamlit as st
import tempfile
import os
from datetime import datetime
import json

from config import Config
from utils.pdf_processor import AdvancedPDFProcessor
from core.rag_engine import OptimizedRAGEngine
from core.chat_agent import AdvancedChatAgent

# Page configuration
st.set_page_config(
    page_title=Config.PAGE_TITLE,
    page_icon=Config.PAGE_ICON,
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ChatGPT-style CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Hide Streamlit elements */
    .stDeployButton { display: none; }
    .stDecoration { display: none; }
    .stToolbar { display: none !important; }
    .stMainBlockContainer { padding: 0; }
    .stAppViewContainer { padding: 0; }
    
    /* Main app styling */
    .stApp {
        background: #343541;
        font-family: 'Inter', sans-serif;
        color: #ffffff;
    }
    
    /* Header bar */
    .header-bar {
        background: #202123;
        padding: 1rem 2rem;
        border-bottom: 1px solid #4d4d4f;
        display: flex;
        justify-content: space-between;
        align-items: center;
        position: sticky;
        top: 0;
        z-index: 100;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    .header-title {
        font-size: 1.5rem;
        font-weight: 600;
        color: #ffffff;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .header-actions {
        display: flex;
        gap: 1rem;
        align-items: center;
    }
    
    .header-button {
        background: #40414f;
        color: #ffffff;
        border: 1px solid #565869;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        font-size: 0.9rem;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .header-button:hover {
        background: #565869;
    }
    
    /* Chat container */
    .chat-container {
        max-width: 48rem;
        margin: 0 auto;
        padding: 2rem 1rem;
        min-height: calc(100vh - 200px);
    }
    
    /* Message styling */
    .message {
        margin-bottom: 1.5rem;
        padding: 1.5rem;
        border-radius: 8px;
        position: relative;
    }
    
    .message.user {
        background: #40414f;
        margin-left: 10%;
        border: 1px solid #565869;
    }
    
    .message.assistant {
        background: #444654;
        margin-right: 10%;
        border: 1px solid #565869;
    }
    
    .message-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 0.75rem;
        font-weight: 600;
        font-size: 0.9rem;
    }
    
    .message-avatar {
        width: 30px;
        height: 30px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1rem;
        font-weight: 600;
    }
    
    .user-avatar {
        background: #19c37d;
        color: white;
    }
    
    .assistant-avatar {
        background: #ab68ff;
        color: white;
    }
    
    .message-content {
        line-height: 1.6;
        color: #ffffff;
        font-size: 0.95rem;
    }
    
    .message-content p {
        margin: 0 0 1rem 0;
    }
    
    .message-content pre {
        background: #2d2d2d;
        padding: 1rem;
        border-radius: 5px;
        overflow-x: auto;
        border: 1px solid #565869;
    }
    
    .message-content code {
        background: #2d2d2d;
        padding: 0.2rem 0.4rem;
        border-radius: 3px;
        font-family: 'Fira Code', monospace;
    }
    
    /* Input section */
    .input-section {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: #343541;
        padding: 1rem 2rem 2rem;
        border-top: 1px solid #4d4d4f;
        box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
    }
    
    .input-container {
        max-width: 48rem;
        margin: 0 auto;
        position: relative;
    }
    
    .input-wrapper {
        background: #40414f;
        border: 1px solid #565869;
        border-radius: 8px;
        padding: 1rem;
        display: flex;
        align-items: end;
        gap: 0.75rem;
    }
    
    .input-wrapper:focus-within {
        border-color: #19c37d;
        box-shadow: 0 0 0 2px rgba(25, 195, 125, 0.2);
    }
    
    .chat-input {
        flex: 1;
        background: transparent;
        border: none;
        color: #ffffff;
        font-size: 0.95rem;
        line-height: 1.5;
        resize: none;
        outline: none;
        font-family: 'Inter', sans-serif;
        max-height: 200px;
        min-height: 24px;
    }
    
    .chat-input::placeholder {
        color: #8e8ea0;
    }
    
    .send-button {
        background: #19c37d;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        cursor: pointer;
        font-weight: 500;
        transition: all 0.2s;
        font-size: 0.9rem;
    }
    
    .send-button:hover:not(:disabled) {
        background: #16a068;
    }
    
    .send-button:disabled {
        background: #565869;
        cursor: not-allowed;
    }
    
    /* Welcome screen */
    .welcome-screen {
        text-align: center;
        padding: 4rem 2rem;
        max-width: 48rem;
        margin: 0 auto;
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
        line-height: 1.5;
    }
    
    .example-prompts {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1rem;
        margin-bottom: 2rem;
    }
    
    .example-prompt {
        background: #40414f;
        border: 1px solid #565869;
        border-radius: 8px;
        padding: 1.5rem;
        cursor: pointer;
        transition: all 0.2s;
        text-align: left;
    }
    
    .example-prompt:hover {
        background: #565869;
        border-color: #19c37d;
    }
    
    .example-prompt-title {
        font-weight: 600;
        color: #ffffff;
        margin-bottom: 0.5rem;
    }
    
    .example-prompt-text {
        color: #8e8ea0;
        font-size: 0.9rem;
        line-height: 1.4;
    }
    
    /* Document upload modal */
    .upload-modal {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0,0,0,0.8);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1000;
    }
    
    .upload-modal-content {
        background: #40414f;
        border: 1px solid #565869;
        border-radius: 12px;
        padding: 2rem;
        max-width: 500px;
        width: 90%;
        max-height: 80vh;
        overflow-y: auto;
    }
    
    .upload-modal-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1.5rem;
    }
    
    .upload-modal-title {
        font-size: 1.5rem;
        font-weight: 600;
        color: #ffffff;
    }
    
    .close-button {
        background: transparent;
        border: none;
        color: #8e8ea0;
        font-size: 1.5rem;
        cursor: pointer;
        padding: 0.5rem;
        border-radius: 5px;
    }
    
    .close-button:hover {
        background: #565869;
    }
    
    .upload-area {
        border: 2px dashed #565869;
        border-radius: 8px;
        padding: 2rem;
        text-align: center;
        margin-bottom: 1.5rem;
        transition: all 0.2s;
    }
    
    .upload-area:hover {
        border-color: #19c37d;
        background: rgba(25, 195, 125, 0.1);
    }
    
    .upload-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
    }
    
    .upload-text {
        color: #8e8ea0;
        margin-bottom: 1rem;
    }
    
    .document-info {
        background: #565869;
        border-radius: 8px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
    }
    
    .document-info h3 {
        color: #ffffff;
        margin-bottom: 1rem;
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
    
    /* Buttons */
    .btn {
        padding: 0.75rem 1.5rem;
        border: none;
        border-radius: 5px;
        cursor: pointer;
        font-weight: 500;
        transition: all 0.2s;
        font-size: 0.9rem;
    }
    
    .btn-primary {
        background: #19c37d;
        color: white;
    }
    
    .btn-primary:hover {
        background: #16a068;
    }
    
    .btn-secondary {
        background: #40414f;
        color: #ffffff;
        border: 1px solid #565869;
    }
    
    .btn-secondary:hover {
        background: #565869;
    }
    
    /* Mobile responsive */
    @media (max-width: 768px) {
        .header-bar {
            padding: 1rem;
        }
        
        .chat-container {
            padding: 1rem;
        }
        
        .input-section {
            padding: 1rem;
        }
        
        .message {
            margin-left: 0;
            margin-right: 0;
        }
        
        .example-prompts {
            grid-template-columns: 1fr;
        }
    }
    
    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #343541;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #565869;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #8e8ea0;
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
    
    if 'show_upload_modal' not in st.session_state:
        st.session_state.show_upload_modal = False

def display_header():
    """Display ChatGPT-style header"""
    st.markdown("""
    <div class="header-bar">
        <div class="header-title">
            🤖 DocuGPT
        </div>
        <div class="header-actions">
            <button class="header-button" onclick="toggleUploadModal()">
                📄 Upload PDF
            </button>
            <button class="header-button" onclick="clearChat()">
                🗑️ Clear Chat
            </button>
        </div>
    </div>
    """, unsafe_allow_html=True)

def display_upload_modal():
    """Display document upload modal"""
    if st.session_state.show_upload_modal:
        with st.container():
            st.markdown("""
            <div class="upload-modal">
                <div class="upload-modal-content">
                    <div class="upload-modal-header">
                        <div class="upload-modal-title">Upload PDF Document</div>
                        <button class="close-button" onclick="closeUploadModal()">×</button>
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
                    st.error(f"File size ({file_size:.1f}MB) exceeds maximum allowed size ({Config.MAX_FILE_SIZE}MB)")
                    return
                
                st.success(f"✅ File loaded: {file_size:.1f}MB")
                
                if st.button("🚀 Process Document", key="process_doc"):
                    with st.spinner("Processing document..."):
                        try:
                            document_data = st.session_state.pdf_processor.extract_text_with_structure(uploaded_file)
                            
                            if document_data:
                                chunks = st.session_state.pdf_processor.create_intelligent_chunks(document_data)
                                st.session_state.rag_engine.create_embeddings(chunks)
                                st.session_state.chat_agent.set_document(document_data)
                                st.session_state.current_document = document_data
                                st.session_state.document_processed = True
                                st.session_state.show_upload_modal = False
                                st.success("✅ Document processed successfully!")
                                st.rerun()
                            
                        except Exception as e:
                            st.error(f"Error processing document: {str(e)}")
            
            st.markdown("</div></div>", unsafe_allow_html=True)

def display_welcome_screen():
    """Display welcome screen with example prompts"""
    st.markdown("""
    <div class="welcome-screen">
        <div class="welcome-title">Welcome to DocuGPT</div>
        <div class="welcome-subtitle">
            Upload a PDF document and start having intelligent conversations with your content
        </div>
        
        <div class="example-prompts">
            <div class="example-prompt" onclick="sendExample('What is this document about?')">
                <div class="example-prompt-title">📄 Document Summary</div>
                <div class="example-prompt-text">What is this document about?</div>
            </div>
            
            <div class="example-prompt" onclick="sendExample('How do I get started?')">
                <div class="example-prompt-title">🚀 Getting Started</div>
                <div class="example-prompt-text">How do I get started?</div>
            </div>
            
            <div class="example-prompt" onclick="sendExample('What are the main features?')">
                <div class="example-prompt-title">✨ Key Features</div>
                <div class="example-prompt-text">What are the main features?</div>
            </div>
            
            <div class="example-prompt" onclick="sendExample('Show me examples')">
                <div class="example-prompt-title">📚 Examples</div>
                <div class="example-prompt-text">Show me examples</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def display_chat_messages():
    """Display chat messages in ChatGPT style"""
    if st.session_state.messages:
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f"""
                <div class="message user">
                    <div class="message-header">
                        <div class="message-avatar user-avatar">U</div>
                        <div>You</div>
                    </div>
                    <div class="message-content">
                        {message["content"]}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="message assistant">
                    <div class="message-header">
                        <div class="message-avatar assistant-avatar">🤖</div>
                        <div>DocuGPT</div>
                    </div>
                    <div class="message-content">
                        {message["content"]}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Add some padding at the bottom to prevent overlap with input
        st.markdown('<div style="height: 150px;"></div>', unsafe_allow_html=True)

def display_chat_input():
    """Display ChatGPT-style chat input"""
    st.markdown("""
    <div class="input-section">
        <div class="input-container">
            <div class="input-wrapper">
                <textarea 
                    class="chat-input" 
                    placeholder="Message DocuGPT..."
                    rows="1"
                    id="chat-input"
                    onkeydown="handleKeyPress(event)"
                ></textarea>
                <button class="send-button" onclick="sendMessage()" id="send-btn">
                    Send
                </button>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def main():
    """Main application function"""
    initialize_session_state()
    
    # Display header
    display_header()
    
    # Display upload modal if needed
    display_upload_modal()
    
    # Display main content
    if not st.session_state.document_processed:
        display_welcome_screen()
    else:
        display_chat_messages()
    
    # Display chat input
    display_chat_input()
    
    # JavaScript for interactivity
    st.markdown("""
    <script>
        function toggleUploadModal() {
            // This would toggle the upload modal
            // In Streamlit, you'd handle this through session state
        }
        
        function clearChat() {
            // This would clear the chat
            // In Streamlit, you'd handle this through session state
        }
        
        function sendExample(text) {
            document.getElementById('chat-input').value = text;
            sendMessage();
        }
        
        function handleKeyPress(event) {
            if (event.key === 'Enter' && !event.shiftKey) {
                event.preventDefault();
                sendMessage();
            }
        }
        
        function sendMessage() {
            const input = document.getElementById('chat-input');
            const message = input.value.trim();
            
            if (message) {
                // In a real implementation, you'd send this to Streamlit
                console.log('Sending message:', message);
                input.value = '';
            }
        }
        
        // Auto-resize textarea
        document.addEventListener('DOMContentLoaded', function() {
            const textarea = document.getElementById('chat-input');
            if (textarea) {
                textarea.addEventListener('input', function() {
                    this.style.height = 'auto';
                    this.style.height = Math.min(this.scrollHeight, 200) + 'px';
                });
            }
        });
    </script>
    """, unsafe_allow_html=True)
    
    # Handle actual message sending through Streamlit
    if st.session_state.get('user_input_key'):
        user_input = st.session_state.user_input_key
        if user_input.strip():
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            if st.session_state.document_processed:
                with st.spinner("DocuGPT is thinking..."):
                    try:
                        response = st.session_state.chat_agent.generate_response(user_input)
                        st.session_state.messages.append({"role": "assistant", "content": response})
                    except Exception as e:
                        st.error(f"Error generating response: {str(e)}")
            else:
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": "Please upload a PDF document first so I can help you with your questions."
                })
            
            st.rerun()

if __name__ == "__main__":
    main()
