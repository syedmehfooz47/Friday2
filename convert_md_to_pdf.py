import markdown2
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.lib import colors
import re
from datetime import datetime

# Read the markdown file
with open('PROJECT_REVIEW.md', 'r', encoding='utf-8') as f:
    content = f.read()

# Create PDF
pdf_filename = f'PROJECT_REVIEW_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
doc = SimpleDocTemplate(pdf_filename, pagesize=A4, 
                       rightMargin=0.75*inch, leftMargin=0.75*inch,
                       topMargin=1*inch, bottomMargin=0.75*inch)

# Styles
styles = getSampleStyleSheet()
title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], 
                            fontSize=20, textColor=colors.HexColor('#1a1a1a'), 
                            spaceAfter=12, alignment=TA_CENTER, fontName='Helvetica-Bold')
heading1_style = ParagraphStyle('CustomHeading1', parent=styles['Heading1'], 
                               fontSize=16, textColor=colors.HexColor('#2c3e50'), 
                               spaceAfter=10, spaceBefore=12, fontName='Helvetica-Bold')
heading2_style = ParagraphStyle('CustomHeading2', parent=styles['Heading2'], 
                               fontSize=14, textColor=colors.HexColor('#34495e'), 
                               spaceAfter=8, spaceBefore=10, fontName='Helvetica-Bold')
heading3_style = ParagraphStyle('CustomHeading3', parent=styles['Heading3'], 
                               fontSize=12, textColor=colors.HexColor('#2c3e50'), 
                               spaceAfter=6, spaceBefore=8, fontName='Helvetica-Bold')
body_style = ParagraphStyle('CustomBody', parent=styles['BodyText'], 
                           fontSize=10, leading=14, alignment=TA_JUSTIFY)
code_style = ParagraphStyle('Code', parent=styles['Code'], 
                           fontSize=8, fontName='Courier', 
                           backColor=colors.HexColor('#f5f5f5'), leftIndent=20)

story = []

# Parse markdown content
lines = content.split('\n')
i = 0
in_code_block = False
code_block = []

while i < len(lines):
    line = lines[i]
    
    # Skip mermaid diagrams
    if '```mermaid' in line:
        while i < len(lines) - 1 and '```' not in lines[i+1]:
            i += 1
        i += 2
        continue
    
    # Code blocks
    if line.startswith('```'):
        if in_code_block:
            # End code block
            if code_block:
                code_text = '\n'.join(code_block)
                code_text = code_text.replace('<', '&lt;').replace('>', '&gt;')
                story.append(Paragraph(f'<font face="Courier" size="8">{code_text}</font>', code_style))
                story.append(Spacer(1, 0.1*inch))
            code_block = []
            in_code_block = False
        else:
            in_code_block = True
        i += 1
        continue
    
    if in_code_block:
        code_block.append(line)
        i += 1
        continue
    
    # Title (# ADVANCED...)
    if line.startswith('# ') and 'ADVANCED' in line:
        story.append(Paragraph(line[2:], title_style))
        story.append(Spacer(1, 0.2*inch))
    # H2 (## )
    elif line.startswith('## '):
        if story:
            story.append(PageBreak())
        story.append(Paragraph(line[3:], heading1_style))
        story.append(Spacer(1, 0.15*inch))
    # H3 (### )
    elif line.startswith('### '):
        story.append(Paragraph(line[4:], heading2_style))
        story.append(Spacer(1, 0.1*inch))
    # H4 (#### )
    elif line.startswith('#### '):
        story.append(Paragraph(line[5:], heading3_style))
        story.append(Spacer(1, 0.08*inch))
    # Bold metadata
    elif line.startswith('**') and ':**' in line:
        story.append(Paragraph(line.replace('**', '<b>').replace('**', '</b>'), body_style))
        story.append(Spacer(1, 0.05*inch))
    # Horizontal rule
    elif line.strip() == '---':
        story.append(Spacer(1, 0.1*inch))
    # Bullet points
    elif line.strip().startswith('- ') or line.strip().startswith('* '):
        text = line.strip()[2:]
        text = text.replace('**', '<b>').replace('**', '</b>')
        text = text.replace('✅', '[OK]').replace('❌', '[X]').replace('⚠️', '[!]')
        text = text.replace('<', '&lt;').replace('>', '&gt;')
        story.append(Paragraph(f'• {text}', body_style))
        story.append(Spacer(1, 0.05*inch))
    # Regular text
    elif line.strip():
        text = line.replace('**', '<b>').replace('**', '</b>')
        text = text.replace('✅', '[OK]').replace('❌', '[X]').replace('⚠️', '[!]')
        text = text.replace('<', '&lt;').replace('>', '&gt;')
        story.append(Paragraph(text, body_style))
        story.append(Spacer(1, 0.08*inch))
    
    i += 1

# Build PDF
doc.build(story)
print(f'PDF generated successfully: {pdf_filename}')
