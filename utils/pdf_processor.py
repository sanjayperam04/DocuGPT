import PyPDF2
import cv2
import numpy as np
from PIL import Image
import streamlit as st
from typing import List, Dict, Optional, Tuple
import re
from langchain.text_splitter import RecursiveCharacterTextSplitter
from config import Config

class AdvancedPDFProcessor:
    def __init__(self):
        self.config = Config()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.config.MAX_CHUNK_SIZE,
            chunk_overlap=self.config.CHUNK_OVERLAP,
            length_function=len,
            separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
        )
    
    def extract_text_with_structure(self, pdf_file) -> Dict[str, any]:
        """Extract text with document structure preservation - Fixed regex patterns"""
        try:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            document_data = {
                "full_text": "",
                "pages": [],
                "sections": [],
                "metadata": {
                    "total_pages": len(pdf_reader.pages),
                    "title": pdf_reader.metadata.get('/Title', 'Unknown') if pdf_reader.metadata else 'Unknown'
                }
            }
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for page_num, page in enumerate(pdf_reader.pages):
                status_text.text(f"Processing page {page_num + 1}/{len(pdf_reader.pages)}")
                
                page_text = page.extract_text()
                
                # Clean and structure the text
                cleaned_text = self.clean_text(page_text)
                
                document_data["pages"].append({
                    "page_number": page_num + 1,
                    "text": cleaned_text,
                    "word_count": len(cleaned_text.split())
                })
                
                document_data["full_text"] += f"\n--- Page {page_num + 1} ---\n{cleaned_text}"
                
                progress_bar.progress((page_num + 1) / len(pdf_reader.pages))
            
            # Extract document sections with fixed regex
            document_data["sections"] = self.extract_sections(document_data["full_text"])
            
            status_text.text("PDF processing complete!")
            return document_data
            
        except Exception as e:
            st.error(f"Error processing PDF: {str(e)}")
            return None
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize extracted text - Fixed regex patterns"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Fix common OCR errors
        text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
        
        # Remove page numbers and headers/footers
        text = re.sub(r'^\d+\s*$', '', text, flags=re.MULTILINE)
        
        # Normalize quotes - Fixed escaping
        text = re.sub(r'["""]', '"', text)
        
        return text.strip()
    
    def extract_sections(self, text: str) -> List[Dict]:
        """Extract document sections based on headers - Fixed regex patterns"""
        sections = []
        
        # Fixed header patterns - corrected regex syntax
        header_patterns = [
            r'^#{1,6}\s+(.+)$',  # Markdown headers
            r'^\d+\.?\s+[A-Z][^.]*?$',  # Numbered sections - fixed
            r'^[A-Z][A-Z\s]+$',  # All caps headers - fixed
            r'^\w+.*?(?=\n\n|\n[A-Z])',  # Paragraph headers - fixed
        ]
        
        lines = text.split('\n')
        current_section = None
        current_content = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            is_header = False
            for pattern in header_patterns:
                try:
                    if re.match(pattern, line, re.MULTILINE):
                        if current_section:
                            sections.append({
                                "title": current_section,
                                "content": '\n'.join(current_content),
                                "word_count": len(' '.join(current_content).split())
                            })
                        
                        current_section = line
                        current_content = []
                        is_header = True
                        break
                except re.error:
                    # Skip problematic regex patterns
                    continue
            
            if not is_header:
                current_content.append(line)
        
        # Add the last section
        if current_section:
            sections.append({
                "title": current_section,
                "content": '\n'.join(current_content),
                "word_count": len(' '.join(current_content).split())
            })
        
        return sections
    
    def create_intelligent_chunks(self, document_data: Dict) -> List[Dict]:
        """Create intelligent chunks preserving context"""
        chunks = []
        
        # Process sections first
        for section in document_data["sections"]:
            section_chunks = self.text_splitter.split_text(section["content"])
            
            for i, chunk in enumerate(section_chunks):
                chunks.append({
                    "text": chunk,
                    "section": section["title"],
                    "chunk_id": f"{section['title']}_{i}",
                    "word_count": len(chunk.split()),
                    "type": "section"
                })
        
        # If no sections found, chunk the full text
        if not chunks:
            text_chunks = self.text_splitter.split_text(document_data["full_text"])
            
            for i, chunk in enumerate(text_chunks):
                chunks.append({
                    "text": chunk,
                    "section": "General",
                    "chunk_id": f"general_{i}",
                    "word_count": len(chunk.split()),
                    "type": "general"
                })
        
        return chunks
