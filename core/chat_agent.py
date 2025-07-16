import streamlit as st
from groq import Groq
from typing import List, Dict, Optional, Generator
from config import Config
from datetime import datetime

class AdvancedChatAgent:
    def __init__(self, rag_engine):
        self.config = Config()
        self.client = Groq(api_key=self.config.GROQ_API_KEY)
        self.rag_engine = rag_engine
        self.conversation_history = []
        self.current_document = None
        
    def set_document(self, document_data: Dict):
        """Set current document context"""
        self.current_document = document_data
        self.conversation_history = []  # Reset conversation for new document
    
    def analyze_query_intent(self, query: str) -> str:
        """Analyze user query to determine intent"""
        query_lower = query.lower()
        
        intent_keywords = {
            "getting_started": ["start", "begin", "setup", "install", "first", "how to start"],
            "troubleshooting": ["error", "problem", "issue", "fix", "troubleshoot", "not working"],
            "how_to": ["how", "step", "guide", "tutorial", "walkthrough", "process"],
            "features": ["feature", "function", "capability", "what can", "what does"],
            "configuration": ["config", "setting", "customize", "options", "preferences"],
            "api": ["api", "endpoint", "request", "response", "authentication"],
            "examples": ["example", "sample", "demo", "show me", "illustrate"]
        }
        
        for intent, keywords in intent_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                return intent
        
        return "general"
    
    def get_contextual_system_prompt(self, intent: str) -> str:
        """Generate context-aware system prompt"""
        doc_info = ""
        if self.current_document:
            doc_info = f"""
Document Context:
- Title: {self.current_document['metadata']['title']}
- Pages: {self.current_document['metadata']['total_pages']}
- Sections: {len(self.current_document['sections'])}
"""
        
        base_prompt = f"""You are an expert documentation assistant. {doc_info}

Your role is to provide helpful, accurate, and actionable guidance based on the uploaded documentation.

Guidelines:
1. Answer questions directly and concisely
2. Provide step-by-step instructions when appropriate
3. Reference specific sections or pages when possible
4. If information isn't in the documentation, clearly state that
5. Ask clarifying questions when needed
6. Use examples from the documentation when available

Current query intent: {intent}"""
        
        intent_specific_prompts = {
            "getting_started": "\nFocus on: Beginner-friendly guidance, prerequisites, first steps, and initial setup.",
            "troubleshooting": "\nFocus on: Problem identification, specific solutions, error resolution, and debugging steps.",
            "how_to": "\nFocus on: Clear step-by-step instructions, sequential processes, and practical guidance.",
            "features": "\nFocus on: Feature explanations, capabilities, benefits, and use cases.",
            "configuration": "\nFocus on: Settings, customization options, configuration parameters, and preferences.",
            "api": "\nFocus on: API endpoints, authentication, request/response formats, and integration examples.",
            "examples": "\nFocus on: Practical examples, code samples, demonstrations, and real-world usage."
        }
        
        return base_prompt + intent_specific_prompts.get(intent, "")
    
    def generate_response(self, user_query: str) -> str:
        """Generate contextual response using RAG"""
        if not self.current_document:
            return "Please upload a PDF document first so I can help you with your questions."
        
        # Analyze query intent
        intent = self.analyze_query_intent(user_query)
        
        # Get relevant chunks
        relevant_chunks = self.rag_engine.search_similar_chunks(user_query, top_k=8)
        
        # Prepare context
        context = self.prepare_context(relevant_chunks, intent)
        
        # Prepare messages
        messages = [
            {"role": "system", "content": self.get_contextual_system_prompt(intent)}
        ]
        
        # Add conversation history (last 6 messages)
        messages.extend(self.conversation_history[-6:])
        
        # Add context
        if context:
            messages.append({"role": "system", "content": context})
        
        # Add current query
        messages.append({"role": "user", "content": user_query})
        
        try:
            response = self.client.chat.completions.create(
                messages=messages,
                model=self.config.DEFAULT_MODEL,
                max_tokens=self.config.MAX_TOKENS,
                temperature=self.config.TEMPERATURE
            )
            
            ai_response = response.choices[0].message.content
            
            # Update conversation history
            self.conversation_history.append({"role": "user", "content": user_query})
            self.conversation_history.append({"role": "assistant", "content": ai_response})
            
            return ai_response
            
        except Exception as e:
            return f"I apologize, but I'm experiencing technical difficulties. Please try again. Error: {str(e)}"
    
    def prepare_context(self, relevant_chunks: List[Dict], intent: str) -> str:
        """Prepare context from relevant chunks"""
        if not relevant_chunks:
            return ""
        
        context = f"Relevant documentation sections for {intent} query:\n\n"
        
        for i, result in enumerate(relevant_chunks, 1):
            chunk = result["chunk"]
            context += f"Section {i} (from {chunk['section']}):\n"
            context += f"{chunk['text']}\n\n"
        
        return context
    
    def generate_streaming_response(self, user_query: str) -> Generator[str, None, None]:
        """Generate streaming response for better UX"""
        if not self.current_document:
            yield "Please upload a PDF document first."
            return
        
        intent = self.analyze_query_intent(user_query)
        relevant_chunks = self.rag_engine.search_similar_chunks(user_query, top_k=8)
        context = self.prepare_context(relevant_chunks, intent)
        
        messages = [
            {"role": "system", "content": self.get_contextual_system_prompt(intent)}
        ]
        
        messages.extend(self.conversation_history[-6:])
        
        if context:
            messages.append({"role": "system", "content": context})
        
        messages.append({"role": "user", "content": user_query})
        
        try:
            response = self.client.chat.completions.create(
                messages=messages,
                model=self.config.DEFAULT_MODEL,
                max_tokens=self.config.MAX_TOKENS,
                temperature=self.config.TEMPERATURE,
                stream=True
            )
            
            full_response = ""
            for chunk in response:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    yield content
            
            # Update conversation history
            self.conversation_history.append({"role": "user", "content": user_query})
            self.conversation_history.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            yield f"Error: {str(e)}"
