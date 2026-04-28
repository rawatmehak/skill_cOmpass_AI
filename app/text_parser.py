import PyPDF2
import docx
import io
from typing import Optional

class ResumeParser:
    """Extract text from PDF and DOCX resumes"""
    
    @staticmethod
    def extract_from_pdf(file_content: bytes) -> str:
        """Extract text from PDF bytes"""
        try:
            pdf_file = io.BytesIO(file_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            return text.strip()
        except Exception as e:
            raise Exception(f"PDF extraction failed: {str(e)}")
    
    @staticmethod
    def extract_from_docx(file_content: bytes) -> str:
        """Extract text from DOCX bytes"""
        try:
            doc_file = io.BytesIO(file_content)
            doc = docx.Document(doc_file)
            
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            
            return text.strip()
        except Exception as e:
            raise Exception(f"DOCX extraction failed: {str(e)}")
    
    @staticmethod
    def extract_text(file_content: bytes, filename: str) -> str:
        """Route to appropriate parser based on file extension"""
        if filename.lower().endswith('.pdf'):
            return ResumeParser.extract_from_pdf(file_content)
        elif filename.lower().endswith('.docx'):
            return ResumeParser.extract_from_docx(file_content)
        else:
            raise ValueError("Unsupported file format. Only PDF and DOCX allowed.")