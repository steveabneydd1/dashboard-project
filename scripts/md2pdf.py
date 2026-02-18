#!/usr/bin/env python3
"""Convert Markdown to PDF using weasyprint."""
import sys
import markdown
from weasyprint import HTML, CSS

def md_to_pdf(md_path, pdf_path):
    with open(md_path, 'r') as f:
        md_content = f.read()
    
    html_content = markdown.markdown(md_content, extensions=['tables', 'fenced_code'])
    
    # Wrap in styled HTML
    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                font-size: 11pt;
                line-height: 1.5;
                max-width: 7.5in;
                margin: 0.5in auto;
                padding: 0 0.5in;
            }}
            h1 {{ font-size: 18pt; margin-top: 0; }}
            h2 {{ font-size: 14pt; margin-top: 1em; border-bottom: 1px solid #ccc; padding-bottom: 0.3em; }}
            h3 {{ font-size: 12pt; margin-top: 0.8em; }}
            table {{
                border-collapse: collapse;
                width: 100%;
                margin: 1em 0;
                font-size: 10pt;
            }}
            th, td {{
                border: 1px solid #ddd;
                padding: 6px 8px;
                text-align: left;
            }}
            th {{ background: #f5f5f5; }}
            code {{
                background: #f4f4f4;
                padding: 2px 4px;
                border-radius: 3px;
                font-size: 10pt;
            }}
            pre {{
                background: #f4f4f4;
                padding: 1em;
                overflow-x: auto;
            }}
            hr {{ border: none; border-top: 1px solid #ccc; margin: 1.5em 0; }}
        </style>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """
    
    HTML(string=full_html).write_pdf(pdf_path)
    print(f"Created: {pdf_path}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: md2pdf.py <input.md> <output.pdf>")
        sys.exit(1)
    md_to_pdf(sys.argv[1], sys.argv[2])
