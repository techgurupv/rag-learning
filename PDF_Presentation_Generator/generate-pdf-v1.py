import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Preformatted
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Pygments for code highlighting
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter


def register_unicode_mono_font():
    """Finds and registers a system monospace font containing Unicode box-drawing characters."""
    if sys.platform.startswith("win"):
        candidates = [
            "C:\\Windows\\Fonts\\consola.ttf",
            "C:\\Windows\\Fonts\\lucon.ttf",
            "C:\\Windows\\Fonts\\cour.ttf",
        ]
    elif sys.platform == "darwin":
        candidates = [
            "/System/Library/Fonts/Menlo.ttc",
            "/System/Library/Fonts/Monaco.ttf",
            "/Library/Fonts/Courier New.ttf",
        ]
    else:
        candidates = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
            "/usr/share/fonts/TTF/DejaVuSansMono.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
        ]

    for path in candidates:
        if os.path.exists(path):
            try:
                pdfmetrics.registerFont(TTFont("UnicodeMono", path))
                return "UnicodeMono"
            except Exception:
                continue
    return "Courier"


def highlight_python(code_text):
    """Applies clean syntax color tags to Python snippets."""
    lexer = PythonLexer()
    
    color_map = {
        'k': '#0F766E',      # keywords (teal)
        'kd': '#0F766E',
        'kn': '#0F766E',
        'nf': '#1D4ED8',     # function name (blue)
        'nc': '#1D4ED8',
        's': '#B45309',      # string (amber)
        's1': '#B45309',
        's2': '#B45309',
        'sd': '#475569',     # docstrings (slate)
        'c1': '#64748B',     # comments (muted slate)
        'nb': '#7C3AED',     # builtins (purple)
        'mi': '#047857',     # integers
    }

    raw_tokens = lexer.get_tokens(code_text)
    formatted = []
    
    for ttype, val in raw_tokens:
        clean_val = val.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        tok_key = str(ttype).split('.')[-1].lower()
        tok_parent = str(ttype).split('.')[-2].lower() if len(str(ttype).split('.')) > 1 else ''
        
        target_color = color_map.get(tok_key, color_map.get(tok_parent, None))
        
        if target_color:
            formatted.append(f'<font color="{target_color}">{clean_val}</font>')
        else:
            formatted.append(clean_val)
            
    return "".join(formatted)


class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        
        # Header
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.5)
        self.line(40, 755, 572, 755)
        self.drawString(40, 760, "Stage 1.4.2.2 — Detecting Scanned / Non-Text PDF Pages")
        
        # Footer
        self.line(40, 42, 572, 42)
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(572, 30, page_str)
        self.restoreState()


def build_pdf(filename="Stage_1_4_2_2_Detecting_Scanned_PDF_Pages.pdf"):
    mono_font = register_unicode_mono_font()

    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=55,
        bottomMargin=55
    )

    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=19,
        textColor=colors.HexColor('#0F172A'),
        spaceAfter=10
    )

    h2_style = ParagraphStyle(
        'DocH2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor('#1E293B'),
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#334155'),
        spaceBefore=2,
        spaceAfter=4
    )

    code_paragraph_style = ParagraphStyle(
        'HighlightedCode',
        fontName=mono_font,
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor('#1E293B')
    )

    # Tight leading matching font size ensures ASCII boxes do not stretch vertically
    diagram_style = ParagraphStyle(
        'DiagramPreformatted',
        fontName=mono_font,
        fontSize=7.2,
        leading=8.6,
        textColor=colors.HexColor('#0F766E')
    )

    story = []

    def make_heading(text):
        p = Paragraph(text, h2_style)
        t = Table([[p]], colWidths=[532])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
            ('LINELEFT', (0, 0), (0, -1), 3, colors.HexColor('#2563EB')),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ]))
        return t

    def make_code_box(content, is_python=True, tag="PYTHON"):
        if is_python:
            html_content = highlight_python(content)
            element = Paragraph(f"<pre>{html_content}</pre>", code_paragraph_style)
            bg = colors.HexColor('#F8FAFC')
            border_color = colors.HexColor('#CBD5E1')
            tag_color = colors.HexColor('#2563EB')
        else:
            # Preformatted preserves exact whitespace, column indices, and line height
            element = Preformatted(content, diagram_style)
            bg = colors.HexColor('#F0FDFA')
            border_color = colors.HexColor('#99F6E4')
            tag_color = colors.HexColor('#0D9488')

        header_p = Paragraph(f"<b><font size=6 color='{tag_color}'>{tag}</font></b>", body_style)
        
        t = Table([[header_p], [element]], colWidths=[532])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), bg),
            ('BOX', (0, 0), (-1, -1), 0.5, border_color),
            ('LINEBELOW', (0, 0), (-1, 0), 0.5, border_color),
            ('TOPPADDING', (0, 0), (-1, 0), 2),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 2),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 1), (-1, 1), 4),
            ('BOTTOMPADDING', (0, 1), (-1, 1), 5),
        ]))
        return t

    content_blocks = [
        ("title", "Stage 1.4.2.2 — Detecting Scanned / Non-Text PDF Pages"),
        ("body", "Exactly. We should not install OCR yet. First we'll understand and implement <b>Stage 1.4.2.2 — Detecting Scanned / Non-Text PDF Pages</b>.<br/>The goal is to build a small inspection experiment in your existing notebook:"),
        ("diagram", "notebooks/\n└── text-loaders/\n    └── 01_data_ingestion.ipynb", "DIRECTORY"),
        
        ("h2", "1. What are we trying to detect?"),
        ("body", "For every PDF page, we want to answer:"),
        ("diagram", "Does this page contain useful extractable text?\n             │\n        ┌────┴────┐\n        │         │\n       YES        NO\n        │         │\n        ▼         ▼\n Normal PDF      OCR candidate", "DECISION FLOW"),
        ("body", "But we'll go one step further.<br/>A page can contain some text and still be problematic. So we'll collect useful diagnostics rather than simply returning True/False."),

        ("h2", "1.4.2.2 — PDF Page Inspection"),
        
        ("h2", "Step 1 — Create the inspection function"),
        ("body", "Add a new Markdown cell:"),
        ("code", "# 1.4.2.2 Detecting Scanned / Non-Text PDF Pages\n\nThe objective is to inspect every PDF page before deciding whether normal\ntext extraction is sufficient or OCR may be required.", "MARKDOWN"),
        ("body", "Then add this code cell:"),
        ("code", """def inspect_pdf_documents(name, documents):
    \"\"\"
    Inspect LangChain Documents produced from a PDF.

    Reports:
    - page number
    - extracted character count
    - whether text exists
    - source metadata
    \"\"\"

    print("=" * 80)
    print(f"PDF INSPECTION: {name}")
    print("=" * 80)

    print(f"Number of pages/documents: {len(documents)}")

    for index, document in enumerate(documents, start=1):

        content = document.page_content.strip()

        print(f"\\nPage {index}")
        print("-" * 80)

        print("Characters :", len(content))
        print("Has text   :", bool(content))
        print("Metadata   :", document.metadata)""", "PYTHON"),

        ("h2", "Step 2 — Inspect the text-based PDF"),
        ("body", "Run:"),
        ("code", "inspect_pdf_documents(\n    \"Text-based PDF\",\n    text_documents\n)", "PYTHON"),
        ("body", "You should see something conceptually similar to:"),
        ("diagram", "================================================================================\nPDF INSPECTION: Text-based PDF\n================================================================================\n\nNumber of pages/documents: 5\n\nPage 1\n--------------------------------------------------------------------------------\nCharacters : *******\nHas text   : True\n\nPage 2\n--------------------------------------------------------------------------------\nCharacters : *******\nHas text   : True", "TERMINAL OUTPUT"),
        ("body", "and so on.<br/>The exact character counts aren't important. The important observation is <b>Has text : True</b> for the pages containing extractable text."),

        ("h2", "Step 3 — Inspect the scanned PDF"),
        ("body", "Now run:"),
        ("code", "inspect_pdf_documents(\n    \"Scanned PDF\",\n    scanned_documents\n)", "PYTHON"),
        ("body", "You should see something similar to:"),
        ("diagram", "================================================================================\nPDF INSPECTION: Scanned PDF\n================================================================================\n\nNumber of pages/documents: 1\n\nPage 1\n--------------------------------------------------------------------------------\nCharacters : 0\nHas text   : False", "TERMINAL OUTPUT"),
        ("body", "This is exactly what we want to demonstrate. We have now programmatically detected:"),
        ("diagram", "Text PDF\n\nPage 1 → text available\nPage 2 → text available\n...\nversus:\n\nScanned PDF\n\nPage 1 → no extractable text", "COMPARISON"),

        ("h2", "Step 4 — Make the detection reusable"),
        ("body", "The previous function is useful for learning, but let's improve it.<br/>Create:"),
        ("code", """def analyze_pdf_pages(documents):
    \"\"\"
    Analyze PDF pages and return page-level diagnostics.
    \"\"\"

    results = []

    for page_number, document in enumerate(documents, start=1):

        content = document.page_content.strip()

        results.append({
            "page": page_number,
            "characters": len(content),
            "has_text": bool(content),
            "metadata": document.metadata
        })

    return results""", "PYTHON"),
        ("body", "Now execute:"),
        ("code", "text_analysis = analyze_pdf_pages(text_documents)\n\nscanned_analysis = analyze_pdf_pages(scanned_documents)", "PYTHON"),
        ("body", "Inspect <code>text_analysis</code> and <code>scanned_analysis</code>. You'll get Python dictionaries representing each page."),

        ("h2", "Step 5 — Make the result easier to understand"),
        ("body", "Because you're using a notebook, let's use a DataFrame:"),
        ("code", "import pandas as pd\n\ntext_df = pd.DataFrame(text_analysis)\ntext_df", "PYTHON"),
        ("table_text", [
            ["page", "characters", "has_text"],
            ["1", "850", "True"],
            ["2", "720", "True"],
            ["3", "940", "True"],
            ["4", "650", "True"],
            ["5", "810", "True"]
        ]),
        ("body", "Now:"),
        ("code", "scanned_df = pd.DataFrame(scanned_analysis)\nscanned_df", "PYTHON"),
        ("table_text", [
            ["page", "characters", "has_text"],
            ["1", "0", "False"]
        ]),
        ("body", "This makes the difference very obvious."),

        ("h2", "Step 6 — Don't stop at has_text"),
        ("body", "This is an important production-level concept. Consider this PDF page:"),
        ("diagram", "Page 3\n\nCharacters: 37\nHas text: True", "INSPECTION"),
        ("body", "Does that automatically mean the page is fine? No. It could be:"),
        ("diagram", "                    Page 3\n                      │\n             Has some text\n                      │\n          ┌───────────┴───────────┐\n          ▼                       ▼\n   Useful extraction        Poor extraction\n          │                       │\n          ▼                       ▼\n       Continue              Investigate", "DIAGNOSTIC TREE"),
        ("body", "For example, the page could contain: a large table, an image containing text, a scanned signature, a diagram, a two-column layout, or text extracted in the wrong order.<br/><br/><b>Therefore: Text presence is a detection signal, not an extraction-quality guarantee.</b>"),

        ("h2", "Step 7 — Introduce a text threshold"),
        ("body", "Let's create a simple learning-oriented classifier:"),
        ("code", """def classify_page(content, minimum_characters=50):
    \"\"\"
    Simple learning-oriented classification.

    Returns:
        TEXT_AVAILABLE
        POSSIBLE_SCANNED
    \"\"\"

    character_count = len(content.strip())

    if character_count >= minimum_characters:
        return "TEXT_AVAILABLE"

    return "POSSIBLE_SCANNED\"""", "PYTHON"),
        ("body", "Now test it:"),
        ("code", "for document in text_documents:\n    result = classify_page(document.page_content)\n    print(result)\n\nfor document in scanned_documents:\n    result = classify_page(document.page_content)\n    print(result)", "PYTHON"),
        ("body", "Your scanned page should be classified as: <b>POSSIBLE_SCANNED</b>"),

        ("h2", "Step 8 — Why do we call it POSSIBLE_SCANNED?"),
        ("body", "This naming is intentional. We should not say 'No text → definitely scanned PDF' because there are other possibilities:"),
        ("diagram", "No extracted text\n       │\n       ├── Scanned page\n       │\n       ├── Image-only page\n       │\n       ├── Extraction failure\n       │\n       ├── Unsupported encoding\n       │\n       └── Corrupted/unusual PDF", "FAILURE MODES"),
        ("body", "Therefore our ingestion pipeline should say <b>POSSIBLE_SCANNED</b> rather than <b>DEFINITELY_SCANNED</b>. This is a much better engineering mindset."),

        ("h2", "Step 9 — Build our first PDF inspection report"),
        ("body", "Let's combine everything:"),
        ("code", """def generate_pdf_inspection_report(documents, minimum_characters=50):

    report = []

    for page_number, document in enumerate(documents, start=1):

        content = document.page_content.strip()
        character_count = len(content)

        if character_count >= minimum_characters:
            status = "TEXT_AVAILABLE"
        else:
            status = "POSSIBLE_SCANNED"

        report.append({
            "page": page_number,
            "characters": character_count,
            "status": status,
            "source": document.metadata.get("source"),
        })

    return report""", "PYTHON"),
        ("body", "Run:"),
        ("code", "report = generate_pdf_inspection_report(scanned_documents)\npd.DataFrame(report)", "PYTHON"),
        ("table_text", [
            ["page", "characters", "status", "source"],
            ["1", "0", "POSSIBLE_SCANNED", "..."]
        ]),
        ("body", "Now test the normal PDF:"),
        ("code", "report = generate_pdf_inspection_report(text_documents)\npd.DataFrame(report)", "PYTHON"),
        ("body", "You should see <b>TEXT_AVAILABLE</b> for the normal pages."),

        ("h2", "Step 10 — Our first ingestion decision engine"),
        ("body", "We can now represent our current learning architecture as:"),
        ("diagram", """                     PDF
                      │
                      ▼
              ┌───────────────┐
              │ Inspect Pages │
              └───────┬───────┘
                      │
             ┌────────┴────────┐
             │                 │
             ▼                 ▼
      TEXT_AVAILABLE     POSSIBLE_SCANNED
             │                 │
             ▼                 ▼
    Normal extraction      Investigate
             │                 │
             │                 ▼
             │                OCR
             │
             └──────────┬──────┘
                        ▼
               LangChain Documents""", "PIPELINE FLOW"),
        ("body", "Important: We aren't actually running OCR yet. We're only building the decision point that tells us: <i>'This page probably needs additional processing.'</i>"),

        ("h2", "Step 11 — One important improvement"),
        ("body", "Our current detector only examines <code>document.page_content</code>. For complex PDFs, that's not enough. For our next experiment we'll inspect the PDF itself:"),
        ("diagram", """Page
 │
 ├── Text blocks
 ├── Images
 ├── Image count
 ├── Text character count
 ├── Text density
 └── Potentially suspicious pages""", "PAGE PROPERTIES"),
        ("body", "That gives us a much stronger picture:"),
        ("diagram", """                    PDF PAGE
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
        Text         Images       Layout
          │            │            │
          └────────────┼────────────┘
                       ▼
                Page Analysis
                       │
                       ▼
              Ingestion Decision""", "ARCHITECTURE"),
        ("body", "That will be our next experiment before OCR.<br/><br/><b>Your learning progression is now:</b>"),
        ("diagram", """1.4.2 OCR & Complex PDF Ingestion
        │
        ├── 1.4.2.1 Text PDF vs Scanned PDF       ✓
        │
        ├── 1.4.2.2 Detect Non-Text Pages         ← We are here
        │
        ├── 1.4.2.3 Deep PDF Page Analysis
        │
        ├── 1.4.2.4 OCR Fundamentals
        │
        ├── 1.4.2.5 OCR Implementation
        │
        └── 1.4.2.6 OCR → LangChain Documents""", "ROADMAP"),
        ("body", "Don't install an OCR engine yet. First complete the page-analysis experiment; it will make the reason for OCR much clearer and will give you a more production-oriented mental model of document ingestion.")
    ]

    for item in content_blocks:
        b_type = item[0]
        if b_type == "title":
            story.append(Paragraph(item[1], title_style))
            story.append(Spacer(1, 3))
        elif b_type == "h2":
            story.append(Spacer(1, 4))
            story.append(make_heading(item[1]))
            story.append(Spacer(1, 3))
        elif b_type == "body":
            story.append(Paragraph(item[1], body_style))
            story.append(Spacer(1, 2))
        elif b_type == "code":
            tag = item[2] if len(item) > 2 else "PYTHON"
            story.append(make_code_box(item[1], is_python=True, tag=tag))
            story.append(Spacer(1, 3))
        elif b_type == "diagram":
            tag = item[2] if len(item) > 2 else "STRUCTURE"
            story.append(make_code_box(item[1], is_python=False, tag=tag))
            story.append(Spacer(1, 3))
        elif b_type == "table_text":
            data = item[1]
            t = Table(data, colWidths=[55, 80, 120, 160][:len(data[0])])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F1F5F9')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#0F172A')),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                ('TOPPADDING', (0, 0), (-1, -1), 3),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ]))
            story.append(t)
            story.append(Spacer(1, 3))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated grid-aligned PDF: '{filename}'")

if __name__ == "__main__":
    build_pdf()