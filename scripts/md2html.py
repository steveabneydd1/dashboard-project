#!/usr/bin/env python3
"""Convert Markdown to styled HTML."""
import sys
import markdown

def md_to_html(md_path, html_path):
    with open(md_path, 'r') as f:
        md_content = f.read()
    
    html_content = markdown.markdown(md_content, extensions=['tables', 'fenced_code'])
    
    full_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            font-size: 11pt;
            line-height: 1.6;
            max-width: 800px;
            margin: 40px auto;
            padding: 0 20px;
            color: #333;
        }}
        h1 {{ font-size: 20pt; margin-top: 0; color: #111; }}
        h2 {{ font-size: 15pt; margin-top: 1.5em; border-bottom: 1px solid #ddd; padding-bottom: 0.3em; color: #222; }}
        h3 {{ font-size: 12pt; margin-top: 1em; color: #333; }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 1em 0;
            font-size: 10pt;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 8px 10px;
            text-align: left;
        }}
        th {{ background: #f7f7f7; font-weight: 600; }}
        tr:nth-child(even) {{ background: #fafafa; }}
        code {{
            background: #f4f4f4;
            padding: 2px 5px;
            border-radius: 3px;
            font-size: 10pt;
        }}
        pre {{
            background: #f4f4f4;
            padding: 1em;
            overflow-x: auto;
            border-radius: 4px;
        }}
        hr {{ border: none; border-top: 1px solid #ddd; margin: 2em 0; }}
        a {{ color: #0066cc; }}
        ul, ol {{ padding-left: 1.5em; }}
        li {{ margin: 0.3em 0; }}
        strong {{ color: #111; }}
        @media print {{
            body {{ margin: 0; padding: 20px; max-width: none; }}
        }}
    </style>
</head>
<body>
{html_content}
</body>
</html>"""
    
    with open(html_path, 'w') as f:
        f.write(full_html)
    print(f"Created: {html_path}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: md2html.py <input.md> <output.html>")
        sys.exit(1)
    md_to_html(sys.argv[1], sys.argv[2])
