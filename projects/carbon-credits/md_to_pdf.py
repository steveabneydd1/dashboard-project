#!/usr/bin/env python3
from fpdf import FPDF
import re
import textwrap

def clean_text(text):
    # Replace Unicode characters with ASCII
    text = text.replace('—', '-').replace('–', '-')
    text = text.replace(''', "'").replace(''', "'")
    text = text.replace('"', '"').replace('"', '"')
    text = text.replace('…', '...')
    text = text.replace('✅', '[OK]').replace('❌', '[X]')
    text = text.replace('•', '*')
    # Remove markdown formatting but keep content
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    text = re.sub(r'`(.+?)`', r'\1', text)
    text = re.sub(r'\[(.+?)\]\((.+?)\)', r'\1', text)  # Links - just keep text
    return text

def md_to_pdf(md_path, pdf_path):
    with open(md_path, 'r') as f:
        content = f.read()
    
    pdf = FPDF()
    pdf.set_margins(15, 15, 15)
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()
    
    effective_width = 180  # A4 = 210mm, minus 15mm each side
    
    lines = content.split('\n')
    
    for line in lines:
        line_clean = clean_text(line)
        
        # Skip table separator lines
        if re.match(r'^\|[-:\s|]+\|$', line.strip()):
            continue
        
        # Skip code blocks markers
        if line.strip().startswith('```'):
            continue
        
        # H1
        if line.startswith('# '):
            pdf.set_font('Helvetica', 'B', 16)
            pdf.multi_cell(effective_width, 8, line_clean[2:])
            pdf.ln(2)
            continue
        
        # H2
        if line.startswith('## '):
            pdf.ln(3)
            pdf.set_font('Helvetica', 'B', 13)
            pdf.multi_cell(effective_width, 7, line_clean[3:])
            pdf.ln(1)
            continue
        
        # H3
        if line.startswith('### '):
            pdf.ln(2)
            pdf.set_font('Helvetica', 'B', 11)
            pdf.multi_cell(effective_width, 6, line_clean[4:])
            continue
        
        # HR
        if line.strip() == '---':
            pdf.ln(3)
            pdf.set_draw_color(180, 180, 180)
            pdf.line(15, pdf.get_y(), 195, pdf.get_y())
            pdf.ln(5)
            continue
        
        # Table row - convert to key: value format
        if '|' in line and line.strip().startswith('|'):
            cells = [c.strip() for c in line.split('|') if c.strip()]
            if len(cells) >= 2:
                key = clean_text(cells[0])
                val = clean_text(cells[1])
                pdf.set_font('Helvetica', 'B', 9)
                pdf.cell(35, 5, key[:20] + ':')
                pdf.set_font('Helvetica', '', 9)
                # Wrap long values
                if len(val) > 80:
                    val = val[:77] + '...'
                pdf.multi_cell(effective_width - 35, 5, val)
            continue
        
        # Bullet
        if line.strip().startswith('- ') or line.strip().startswith('* '):
            pdf.set_font('Helvetica', '', 10)
            bullet_text = line_clean.strip()[2:]
            pdf.cell(8, 5, '')
            pdf.multi_cell(effective_width - 8, 5, '* ' + bullet_text)
            continue
        
        # Regular text
        if line.strip():
            pdf.set_font('Helvetica', '', 10)
            pdf.multi_cell(effective_width, 5, line_clean)
        else:
            pdf.ln(2)
    
    pdf.output(pdf_path)
    print(f"Created: {pdf_path}")

if __name__ == '__main__':
    base = '/Users/steveabney/.openclaw/workspace/projects/carbon-credits'
    md_to_pdf(f'{base}/CONTACT_LIST_FOR_CARBON_X.md', f'{base}/Walker_Ranch_Contact_List.pdf')
    md_to_pdf(f'{base}/EMAIL_TEMPLATE.md', f'{base}/Walker_Ranch_Email_Template.pdf')
    print("Done!")
