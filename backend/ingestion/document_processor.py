"""
Document processor for unstructured data (PDF, DOCX, TXT).
"""

from typing import List, Dict, Any
import logging
from pathlib import Path
import PyPDF2
import pdfplumber
from docx import Document as DocxDocument

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Process unstructured documents into chunks."""
    
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        """
        Initialize document processor.
        
        Args:
            chunk_size: Target chunk size in tokens (approximate)
            chunk_overlap: Overlap between chunks in tokens
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def process_pdf(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Process PDF file.
        
        Args:
            file_path: Path to PDF file
        
        Returns:
            List of chunks with metadata
        """
        chunks = []
        
        try:
            # Try pdfplumber first (better for tables)
            with pdfplumber.open(file_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    text = page.extract_text()
                    
                    if text:
                        page_chunks = self._chunk_text(text)
                        
                        for chunk_text in page_chunks:
                            chunks.append({
                                "content": chunk_text,
                                "metadata": {
                                    "document": Path(file_path).name,
                                    "page": page_num,
                                    "type": "pdf"
                                }
                            })
            
            logger.info(f"Processed PDF: {len(chunks)} chunks from {file_path}")
            
        except Exception as e:
            logger.error(f"Error processing PDF with pdfplumber: {e}")
            
            # Fallback to PyPDF2
            try:
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    
                    for page_num, page in enumerate(pdf_reader.pages, 1):
                        text = page.extract_text()
                        
                        if text:
                            page_chunks = self._chunk_text(text)
                            
                            for chunk_text in page_chunks:
                                chunks.append({
                                    "content": chunk_text,
                                    "metadata": {
                                        "document": Path(file_path).name,
                                        "page": page_num,
                                        "type": "pdf"
                                    }
                                })
                
                logger.info(f"Processed PDF with PyPDF2: {len(chunks)} chunks")
                
            except Exception as e2:
                logger.error(f"Error processing PDF with PyPDF2: {e2}")
        
        return chunks
    
    def process_docx(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Process DOCX file.
        
        Args:
            file_path: Path to DOCX file
        
        Returns:
            List of chunks with metadata
        """
        chunks = []
        
        try:
            doc = DocxDocument(file_path)
            
            full_text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
            
            text_chunks = self._chunk_text(full_text)
            
            for chunk_text in text_chunks:
                chunks.append({
                    "content": chunk_text,
                    "metadata": {
                        "document": Path(file_path).name,
                        "type": "docx"
                    }
                })
            
            logger.info(f"Processed DOCX: {len(chunks)} chunks from {file_path}")
            
        except Exception as e:
            logger.error(f"Error processing DOCX: {e}")
        
        return chunks
    
    def process_txt(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Process TXT file.
        
        Args:
            file_path: Path to TXT file
        
        Returns:
            List of chunks with metadata
        """
        chunks = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
            
            text_chunks = self._chunk_text(text)
            
            for chunk_text in text_chunks:
                chunks.append({
                    "content": chunk_text,
                    "metadata": {
                        "document": Path(file_path).name,
                        "type": "txt"
                    }
                })
            
            logger.info(f"Processed TXT: {len(chunks)} chunks from {file_path}")
            
        except Exception as e:
            logger.error(f"Error processing TXT: {e}")
        
        return chunks
    
    def _chunk_text(self, text: str) -> List[str]:
        """
        Chunk text into smaller pieces with overlap.
        
        Args:
            text: Input text
        
        Returns:
            List of text chunks
        """
        # Simple word-based chunking (approximate tokens)
        words = text.split()
        chunks = []
        
        i = 0
        while i < len(words):
            chunk_words = words[i:i + self.chunk_size]
            chunk_text = " ".join(chunk_words)
            chunks.append(chunk_text)
            
            # Move forward with overlap
            i += self.chunk_size - self.chunk_overlap
        
        return chunks
    
    def process_document(self, file_path: str, document_type: str) -> List[Dict[str, Any]]:
        """
        Process document based on type.
        
        Args:
            file_path: Path to document
            document_type: Type (pdf, docx, txt)
        
        Returns:
            List of chunks with metadata
        """
        if document_type == "pdf":
            return self.process_pdf(file_path)
        elif document_type == "docx":
            return self.process_docx(file_path)
        elif document_type == "txt":
            return self.process_txt(file_path)
        else:
            logger.error(f"Unsupported document type: {document_type}")
            return []
