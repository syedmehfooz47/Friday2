# -*- coding: utf-8 -*-
"""
PDF Generator - Creates professional PDF documents using Groq AI
Generates well-formatted, multi-page PDF documents
"""

import os
import time
from pathlib import Path
from dotenv import load_dotenv
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from .logger import Logger
from .llm_handler import llm_handler

load_dotenv()


class PDFGenerator:
    """Generate professional PDF documents"""
    
    def __init__(self):
        self.data_folder = Path(__file__).parent.parent / "Data" / "GeneratedDocuments"
        self.data_folder.mkdir(parents=True, exist_ok=True)
    
    def generate_pdf(self, topic: str, pages: int = 10) -> tuple[str, str]:
        """
        Generate a professional PDF document
        
        Args:
            topic: Topic for the document
            pages: Number of pages to generate (minimum 10)
            
        Returns:
            Tuple of (response message, file path)
        """
        username = os.getenv("Username", "Boss")
        
        if pages < 1:
            return f"Invalid page count, Boss. Please specify at least 1 page.", None
        
        Logger.log(f"Generating {pages}-page PDF on topic: '{topic}'", "PDF")
        
        try:
            # Generate content using Groq
            content_prompt = f"""You are a professional document writer.
Create a comprehensive, well-structured document about "{topic}".

The document should be approximately {pages * 400} words ({pages} pages worth of content).

Requirements:
- Start with an engaging introduction
- Use clear section headings
- Include detailed explanations and examples
- Write in a professional, informative tone
- End with a strong conclusion
- Format with proper paragraphs

DO NOT include any markdown formatting, asterisks, or special characters. Write in plain text with clear paragraph breaks."""
            
            messages = [{"role": "user", "content": content_prompt}]
            content = llm_handler.get_response(messages, max_tokens=8000, temperature=0.7)
            
            if content.startswith("Error"):
                return f"Failed to generate content: {content}", None
            
            # Create PDF
            safe_topic = "".join(c for c in topic if c.isalnum() or c in (' ', '_')).rstrip()[:50]
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            file_path = self.data_folder / f"{safe_topic.replace(' ', '_')}_{timestamp}.pdf"
            
            doc = SimpleDocTemplate(
                str(file_path),
                pagesize=letter,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18
            )
            
            # Styles
            styles = getSampleStyleSheet()
            
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor='#2C3E50',
                spaceAfter=30,
                alignment=TA_CENTER,
                fontName='Helvetica-Bold'
            )
            
            body_style = ParagraphStyle(
                'CustomBody',
                parent=styles['BodyText'],
                fontSize=12,
                leading=18,
                alignment=TA_JUSTIFY,
                spaceAfter=12,
                fontName='Helvetica'
            )
            
            # Build document
            story = []
            
            # Title
            title = Paragraph(topic.upper(), title_style)
            story.append(title)
            story.append(Spacer(1, 0.3 * inch))
            
            # Content
            paragraphs = content.split('\n\n')
            for para in paragraphs:
                if para.strip():
                    # Check if it's a heading
                    if len(para) < 100 and not para.endswith('.'):
                        heading_style = ParagraphStyle(
                            'Heading',
                            parent=styles['Heading2'],
                            fontSize=16,
                            textColor='#34495E',
                            spaceAfter=12,
                            spaceBefore=12,
                            fontName='Helvetica-Bold'
                        )
                        p = Paragraph(para.strip(), heading_style)
                    else:
                        p = Paragraph(para.strip(), body_style)
                    
                    story.append(p)
                    story.append(Spacer(1, 0.1 * inch))
            
            doc.build(story)
            
            Logger.log(f"PDF generated successfully: {file_path}", "PDF")
            return f"I've generated a {pages}-page PDF document on '{topic}' for you, Boss.", str(file_path)
        
        except Exception as e:
            Logger.log(f"Error generating PDF: {e}", "ERROR")
            return f"Failed to generate PDF: {e}", None


# Global instance
pdf_generator = PDFGenerator()