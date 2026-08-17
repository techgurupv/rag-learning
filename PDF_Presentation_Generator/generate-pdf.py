import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Preformatted, Table, TableStyle
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

def register_unicode_mono_font():
    """
    Finds and registers a system monospace font containing Unicode box-drawing characters.
    """
    font_candidates = []
    
    if sys.platform.startswith("win"):
        font_candidates = [
            "C:\\Windows\\Fonts\\consola.ttf",       # Consolas
            "C:\\Windows\\Fonts\\lucon.ttf",         # Lucida Console
            "C:\\Windows\\Fonts\\cour.ttf",          # Courier New
            "C:\\Windows\\Fonts\\seguisym.ttf",      # Segoe UI Symbol
        ]
    elif sys.platform == "darwin":
        font_candidates = [
            "/System/Library/Fonts/Menlo.ttc",
            "/System/Library/Fonts/Monaco.ttf",
            "/Library/Fonts/Courier New.ttf",
        ]
    else:  # Linux / Unix
        font_candidates = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
            "/usr/share/fonts/TTF/DejaVuSansMono.ttf",
            "/usr/share/fonts/truetype/freefont/FreeMono.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
        ]

    for path in font_candidates:
        if os.path.exists(path):
            try:
                pdfmetrics.registerFont(TTFont("UnicodeMono", path))
                return "UnicodeMono"
            except Exception:
                continue
                
    return "Courier"


class NumberedCanvas(canvas.Canvas):
    """Canvas that performs a two-pass render to dynamically display total page count."""
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
            self.draw_page_number(num_pages)
            super().showPage()
        super().save()

    def draw_page_number(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        
        # Header rule & title
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.5)
        self.line(40, 755, 572, 755)
        self.drawString(40, 760, "Stage 1.4.2.2 — Detecting Scanned / Non-Text PDF Pages")
        
        # Footer rule & page numbering
        self.line(40, 45, 572, 45)
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(572, 32, page_str)
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
        fontSize=16,
        leading=20,
        textColor=colors.HexColor('#0F172A'),
        spaceAfter=10
    )

    h2_style = ParagraphStyle(
        'DocH2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=11.5,
        leading=15,
        textColor=colors.HexColor('#1E293B'),
        spaceBefore=11,
        spaceAfter=4
    )

    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#334155'),
        spaceAfter=4
    )

    code_style = ParagraphStyle(
        'DocCode',
        fontName=mono_font,
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor('#0F172A'),
        backColor=colors.HexColor('#F8FAFC'),
        borderColor=colors.HexColor('#CBD5E1'),
        borderWidth=0.5,
        borderPadding=5,
        spaceBefore=3,
        spaceAfter=5
    )

    story = []

    content_blocks = [
        ("title", "Stage 1.4.2.2 — Detecting Scanned / Non-Text PDF Pages"),
        ("body", "Exactly. We should not install OCR yet. First we'll understand and implement <b>Stage 1.4.2.2 — Detecting Scanned / Non-Text PDF Pages</b>.<br/>The goal is to build a small inspection experiment in your existing notebook:"),
        ("code", "notebooks/\n└── text-loaders/\n    └── 01_data_ingestion.ipynb"),
        
        ("h2", "1. What are we trying to detect?"),
        ("body", "For every PDF page, we want to answer:"),
        ("code", "Does this page contain useful extractable text?\n             │\n        ┌────┴────┐\n        │         │\n       YES        NO\n        │         │\n        ▼         ▼\n Normal PDF      OCR candidate"),
        ("body", "But we'll go one step further.<br/>A page can contain some text and still be problematic. So we'll collect useful diagnostics rather than simply returning True/False."),

        ("h2", "1.4.2.2 — PDF Page Inspection"),
        
        ("h2", "Step 1 — Create the inspection function"),
        ("body", "Add a new Markdown cell:"),
        ("code", "# 1.4.2.2 Detecting Scanned / Non-Text PDF Pages\n\nThe objective is to inspect every PDF page before deciding whether normal\ntext extraction is sufficient or OCR may be required."),
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
        print("Metadata   :", document.metadata)"""),

        ("h2", "Step 2 — Inspect the text-based PDF"),
        ("body", "Run:"),
        ("code", "inspect_pdf_documents(\n    \"Text-based PDF\",\n    text_documents\n)"),
        ("body", "You should see something conceptually similar to:"),
        ("code", "================================================================================\nPDF INSPECTION: Text-based PDF\n================================================================================\n\nNumber of pages/documents: 5\n\nPage 1\n--------------------------------------------------------------------------------\nCharacters : *******\nHas text   : True\n\nPage 2\n--------------------------------------------------------------------------------\nCharacters : *******\nHas text   : True"),
        ("body", "and so on.<br/>The exact character counts aren't important. The important observation is <b>Has text : True</b> for the pages containing extractable text."),

        ("h2", "Step 3 — Inspect the scanned PDF"),
        ("body", "Now run:"),
        ("code", "inspect_pdf_documents(\n    \"Scanned PDF\",\n    scanned_documents\n)"),
        ("body", "You should see something similar to:"),
        ("code", "================================================================================\nPDF INSPECTION: Scanned PDF\n================================================================================\n\nNumber of pages/documents: 1\n\nPage 1\n--------------------------------------------------------------------------------\nCharacters : 0\nHas text   : False"),
        ("body", "This is exactly what we want to demonstrate. We have now programmatically detected:"),
        ("code", "Text PDF\n\nPage 1 → text available\nPage 2 → text available\n...\nversus:\n\nScanned PDF\n\nPage 1 → no extractable text"),

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

    return results"""),
        ("body", "Now execute:"),
        ("code", "text_analysis = analyze_pdf_pages(text_documents)\n\nscanned_analysis = analyze_pdf_pages(scanned_documents)"),
        ("body", "Inspect <code>text_analysis</code> and <code>scanned_analysis</code>. You'll get Python dictionaries representing each page."),

        ("h2", "Step 5 — Make the result easier to understand"),
        ("body", "Because you're using a notebook, let's use a DataFrame:"),
        ("code", "import pandas as pd\n\ntext_df = pd.DataFrame(text_analysis)\ntext_df"),
        ("table_text", [
            ["page", "characters", "has_text"],
            ["1", "850", "True"],
            ["2", "720", "True"],
            ["3", "940", "True"],
            ["4", "650", "True"],
            ["5", "810", "True"]
        ]),
        ("body", "Now:"),
        ("code", "scanned_df = pd.DataFrame(scanned_analysis)\nscanned_df"),
        ("table_text", [
            ["page", "characters", "has_text"],
            ["1", "0", "False"]
        ]),
        ("body", "This makes the difference very obvious."),

        ("h2", "Step 6 — Don't stop at has_text"),
        ("body", "This is an important production-level concept. Consider this PDF page:"),
        ("code", "Page 3\n\nCharacters: 37\nHas text: True"),
        ("body", "Does that automatically mean the page is fine? No. It could be:"),
        ("code", "                    Page 3\n                      │\n             Has some text\n                      │\n          ┌───────────┴───────────┐\n          ▼                       ▼\n   Useful extraction        Poor extraction\n          │                       │\n          ▼                       ▼\n       Continue              Investigate"),
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

    return "POSSIBLE_SCANNED\""""),
        ("body", "Now test it:"),
        ("code", "for document in text_documents:\n    result = classify_page(document.page_content)\n    print(result)\n\nfor document in scanned_documents:\n    result = classify_page(document.page_content)\n    print(result)"),
        ("body", "Your scanned page should be classified as: <b>POSSIBLE_SCANNED</b>"),

        ("h2", "Step 8 — Why do we call it POSSIBLE_SCANNED?"),
        ("body", "This naming is intentional. We should not say 'No text → definitely scanned PDF' because there are other possibilities:"),
        ("code", "No extracted text\n       │\n       ├── Scanned page\n       │\n       ├── Image-only page\n       │\n       ├── Extraction failure\n       │\n       ├── Unsupported encoding\n       │\n       └── Corrupted/unusual PDF"),
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

    return report"""),
        ("body", "Run:"),
        ("code", "report = generate_pdf_inspection_report(scanned_documents)\npd.DataFrame(report)"),
        ("table_text", [
            ["page", "characters", "status", "source"],
            ["1", "0", "POSSIBLE_SCANNED", "..."]
        ]),
        ("body", "Now test the normal PDF:"),
        ("code", "report = generate_pdf_inspection_report(text_documents)\npd.DataFrame(report)"),
        ("body", "You should see <b>TEXT_AVAILABLE</b> for the normal pages."),

        ("h2", "Step 10 — Our first ingestion decision engine"),
        ("body", "We can now represent our current learning architecture as:"),
        ("code", """                     PDF
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
               LangChain Documents"""),
        ("body", "Important: We aren't actually running OCR yet. We're only building the decision point that tells us: <i>'This page probably needs additional processing.'</i>"),

        ("h2", "Step 11 — One important improvement"),
        ("body", "Our current detector only examines <code>document.page_content</code>. For complex PDFs, that's not enough. For our next experiment we'll inspect the PDF itself:"),
        ("code", """Page
 │
 ├── Text blocks
 ├── Images
 ├── Image count
 ├── Text character count
 ├── Text density
 └── Potentially suspicious pages"""),
        ("body", "That gives us a much stronger picture:"),
        ("code", """                    PDF PAGE
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
              Ingestion Decision"""),
        ("body", "That will be our next experiment before OCR.<br/><br/><b>Your learning progression is now:</b>"),
        ("code", """1.4.2 OCR & Complex PDF Ingestion
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
        └── 1.4.2.6 OCR → LangChain Documents"""),
        ("body", "Don't install an OCR engine yet. First complete the page-analysis experiment; it will make the reason for OCR much clearer and will give you a more production-oriented mental model of document ingestion.")
    ]

    for block_type, content in content_blocks:
        if block_type == "title":
            story.append(Paragraph(content, title_style))
        elif block_type == "h2":
            story.append(Paragraph(content, h2_style))
        elif block_type == "body":
            story.append(Paragraph(content, body_style))
        elif block_type == "code":
            story.append(Preformatted(content, code_style))
        elif block_type == "table_text":
            t = Table(content, colWidths=[55, 80, 110, 160][:len(content[0])])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E2E8F0')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#0F172A')),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                ('TOPPADDING', (0, 0), (-1, -1), 3),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ]))
            story.append(t)
            story.append(Spacer(1, 4))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Generated '{filename}' using registered font '{mono_font}'.")

if __name__ == "__main__":
    build_pdf()