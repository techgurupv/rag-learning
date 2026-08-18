import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Preformatted
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Pygments for syntax tokenization
from pygments.lexers import PythonLexer, PowerShellLexer


def register_unicode_mono_font():
    """Finds and registers a system monospace font containing Unicode box-drawing characters."""
    if sys.platform.startswith("win"):
        candidates = [
            "C:\\Windows\\Fonts\\consola.ttf",
            "C:\\Windows\\Fonts\\lucon.ttf",
            "C:\\Windows\\Fonts\\cour.ttf",
            "C:\\Windows\\Fonts\\seguisym.ttf",
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


def highlight_code_strict_lines(code_text, is_powershell=False):
    """
    Renders syntax-highlighted code line-by-line.
    Converts indentation to &nbsp; and preserves exact line breaks with <br/>.
    """
    lexer = PowerShellLexer() if is_powershell else PythonLexer()
    
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

    lines = code_text.strip('\n').split('\n')
    highlighted_lines = []

    for line in lines:
        if not line:
            highlighted_lines.append('&nbsp;')
            continue

        raw_tokens = lexer.get_tokens(line)
        line_parts = []
        for ttype, val in raw_tokens:
            tok_key = str(ttype).split('.')[-1].lower()
            tok_parent = str(ttype).split('.')[-2].lower() if len(str(ttype).split('.')) > 1 else ''
            target_color = color_map.get(tok_key, color_map.get(tok_parent, None))
            
            clean_val = val.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            clean_val = clean_val.replace(' ', '&nbsp;')
            
            if target_color:
                line_parts.append(f'<font color="{target_color}">{clean_val}</font>')
            else:
                line_parts.append(clean_val)
                
        highlighted_lines.append("".join(line_parts))

    return "<br/>".join(highlighted_lines)


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
        self.drawString(40, 760, "Stage 1.4.2.5 — Choosing an OCR Approach & Running OCR")
        
        # Footer
        self.line(40, 42, 572, 42)
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(572, 30, page_str)
        self.restoreState()


def build_pdf(filename="Stage_1_4_2_5_OCR_Implementation.pdf"):
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
        'LineByLineHighlightedCode',
        fontName=mono_font,
        fontSize=7.2,
        leading=10.2,
        textColor=colors.HexColor('#1E293B')
    )

    diagram_style = ParagraphStyle(
        'DiagramPreformatted',
        fontName=mono_font,
        fontSize=7.2,
        leading=8.8,
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
            is_ps = (tag == "POWERSHELL" or tag == "TERMINAL")
            html_content = highlight_code_strict_lines(content, is_powershell=is_ps)
            element = Paragraph(html_content, code_paragraph_style)
            bg = colors.HexColor('#F8FAFC')
            border_color = colors.HexColor('#CBD5E1')
            tag_color = colors.HexColor('#2563EB')
        else:
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
        ("title", "Stage 1.4.2.5 — Choosing an OCR Approach and Running OCR"),
        ("body", "At this point, we already established an important distinction: <b>A scanned PDF page is essentially an image.</b><br/>So normal PDF text extractors (such as PyPDFLoader or PyMuPDFLoader) return little or no meaningful text.<br/>Our goal now is:"),
        ("diagram", """scanned PDF
    ↓
scanned_page.png
    ↓
OCR Engine
    ↓
recognized text
    ↓
LangChain Document
    ↓
later → chunking → embedding → vector DB → retrieval""", "TARGET PIPELINE"),
        ("body", "For this learning stage, we start with <b>Tesseract OCR</b>."),

        ("h2", "1. Why Tesseract for this stage?"),
        ("body", "There are several OCR approaches available across the ecosystem:"),
        ("table_text", [
            ["OCR Approach", "Type", "Best Suited For"],
            ["Tesseract", "Open source", "Learning OCR fundamentals, local processing"],
            ["EasyOCR", "Open source", "Multilingual / general image OCR"],
            ["PaddleOCR", "Open source", "Stronger document / layout OCR"],
            ["Docling", "Open source", "Document understanding + structured extraction"],
            ["Azure Doc Intelligence", "Cloud", "Enterprise document processing"],
            ["Google Document AI", "Cloud", "Enterprise document understanding"],
            ["AWS Textract", "Cloud", "Enterprise document extraction"],
            ["OpenAI / Gemini Vision", "Closed / API", "Vision + reasoning + extraction"]
        ]),
        ("body", "We shouldn't jump to Docling or cloud OCR yet. The purpose of Stage 1.4.2.5 is to understand the fundamental mechanism: <i>How do we turn pixels from a scanned page into text that can enter our RAG pipeline?</i> Tesseract is open-source and provides Windows installers via the UB Mannheim distribution."),

        ("h2", "2. Important: Tesseract has TWO parts"),
        ("body", "When we use <code>import pytesseract</code>, we have not installed the OCR engine itself. There are two distinct components:"),
        ("diagram", """Windows
│
├── Tesseract OCR Engine
│       ↓
│   actual OCR program (.exe binary)
│
└── Python
        ↓
    pytesseract
        ↓
    Python wrapper that communicates with Tesseract""", "TWO-PART ARCHITECTURE"),
        ("body", "<b>Component 1:</b> Tesseract executable engine.<br/><b>Component 2:</b> <code>pytesseract</code> Python wrapper."),

        ("h2", "3. OCR setup on your Windows 10 machine"),
        ("body", "Because you are using Windows 10, VS Code, Notebook, and <code>uv</code>, we'll keep the setup consistent with your existing environment.<br/><br/><b>Step 3.1 — Install Tesseract itself:</b><br/>Download/install the Windows version from UB Mannheim. During installation, make sure English language data (<code>eng</code>) is selected.<br/>Typical installation path: <code>C:\\Program Files\\Tesseract-OCR\\tesseract.exe</code>"),

        ("h2", "4. Verify Tesseract from PowerShell"),
        ("body", "After installation, close and reopen VS Code/PowerShell to refresh PATH environment variables. Run:"),
        ("code", "tesseract --version", "POWERSHELL"),
        ("body", "Expected output:"),
        ("diagram", "tesseract 5.x.x\n leptonica-...\n ...", "OUTPUT"),
        ("body", "Then check available language models:"),
        ("code", "tesseract --list-langs", "POWERSHELL"),
        ("diagram", "List of available languages in \"...\"\neng\nosd", "OUTPUT"),

        ("h2", "5. What if PowerShell says tesseract is not recognized?"),
        ("body", "This means Tesseract is installed but Windows cannot locate it in PATH. Test the absolute path first:"),
        ("code", '& "C:\\Program Files\\Tesseract-OCR\\tesseract.exe" --version', "POWERSHELL"),
        ("body", "If that works, add <code>C:\\Program Files\\Tesseract-OCR</code> to your Windows system/user PATH."),

        ("h2", "6. Now install the Python wrapper using UV"),
        ("body", "Go to your existing RAG project root and add the package:"),
        ("code", """cd <your-rag-learning-project>
uv add pytesseract""", "POWERSHELL"),
        ("body", "<code>uv add</code> updates <code>pyproject.toml</code>, lockfile, and virtual environment automatically."),
        ("diagram", """uv                  → manages Python dependencies (pytesseract)
Windows Installer   → installs Tesseract OCR binary engine""", "DEPENDENCY SEPARATION"),

        ("h2", "7. Verify pytesseract in your notebook"),
        ("body", "Create a new cell in your Stage 1.4.2.5 notebook and run:"),
        ("code", """import pytesseract

print(pytesseract.get_tesseract_version())
print(pytesseract.get_languages())""", "PYTHON"),
        ("body", "Output should reflect your installed engine version and <code>['eng', 'osd', ...]</code>."),

        ("h2", "8. Verify our actual scanned_page.png"),
        ("body", "Load the image produced from the previous experiment:"),
        ("code", """from PIL import Image

image = Image.open("scanned_page.png")

print(image.size)
print(image.mode)""", "PYTHON"),
        ("body", "Typical output: <code>(1700, 2200), RGB</code>."),

        ("h2", "9. Look at the scanned page before OCR"),
        ("body", "Inspect the visual frame:"),
        ("code", "display(image)", "PYTHON"),
        ("body", "Remember: The PDF viewer sees structured text, but the OCR engine sees only raw pixel color arrays."),

        ("h2", "10. Run our first OCR"),
        ("body", "Execute the character recognition:"),
        ("code", """import pytesseract

ocr_text = pytesseract.image_to_string(
    image,
    lang="eng"
)

print(ocr_text)""", "PYTHON"),
        ("diagram", """scanned_page.png → Image → pytesseract → Tesseract OCR → recognized text""", "FIRST OCR RUN"),

        ("h2", "11. Save the OCR result"),
        ("body", "Preserve the output text to disk:"),
        ("code", """ocr_output_path = "scanned_page_ocr.txt"

with open(ocr_output_path, "w", encoding="utf-8") as f:
    f.write(ocr_text)

print(f"OCR output saved to: {ocr_output_path}")""", "PYTHON"),
        ("body", "This creates a clear visual transformation: <code>scanned_page.png</code> (IMAGE) → <code>scanned_page_ocr.txt</code> (TEXT)."),

        ("h2", "12. Now connect OCR to LangChain"),
        ("body", "OCR is an ingestion capability. Here is how it completes the RAG flow:"),
        ("diagram", """                 Scanned PDF
                      │
                      ▼
              PDF page image
                      │
                      ▼
                OCR Engine
                      │
                      ▼
                  OCR text
                      │
                      ▼
           LangChain Document
                      │
                      ▼
                  Chunking
                      │
                      ▼
                 Embedding
                      │
                      ▼
                Vector Store
                      │
                      ▼
                 Retrieval
                      │
                      ▼
                     LLM""", "INGESTION INTEGRATION"),
        ("body", "<b>Without OCR:</b> Scanned PDF → No text → No chunks → Retrieval fails.<br/><b>With OCR:</b> Scanned PDF → OCR Text → Chunks → Embeddings → Vector DB → Accurate Retrieval."),

        ("h2", "13. Create a LangChain Document"),
        ("body", "Convert the recognized text into a standard LangChain Document object:"),
        ("code", """from langchain_core.documents import Document

ocr_document = Document(
    page_content=ocr_text,
    metadata={
        "source": "scanned_page.png",
        "document_type": "scanned_pdf_page",
        "ocr": True,
        "ocr_engine": "tesseract",
        "language": "eng"
    }
)

print(ocr_document)
print(ocr_document.page_content)""", "PYTHON"),

        ("h2", "14. Why metadata becomes especially important here"),
        ("body", "Preserving provenance (<code>ocr: True</code>) allows downstream debugging when tracking citation quality across multi-format corpora:"),
        ("diagram", """LLM answer
   ↓
retrieved chunk
   ↓
OCR-generated chunk (metadata: ocr=True, page=12)
   ↓
employee_handbook.pdf""", "PROVENANCE TRACING"),

        ("h2", "15. One very important observation"),
        ("body", "OCR is prone to minor character hallucinations (e.g. <code>Azure Event Hub</code> → <code>Azure Event Huh</code>, or <code>Data Explorer</code> → <code>Data ExpIorer</code>).<br/>Because OCR errors degrade chunks, embeddings, and retrieval accuracy, production systems use preprocessing and quality evaluation."),

        ("h2", "16. Our first OCR experiment should be deliberately simple"),
        ("body", "Establish the baseline with raw <code>image_to_string()</code> first. Inspect word accuracy, line preservation, and table integrity before introducing advanced pre-processing filters (grayscale, noise removal, binarization, deskewing)."),

        ("h2", "17. Also understand what Tesseract is NOT doing"),
        ("body", "Tesseract detects characters and words, but does not parse semantic relationships (e.g., mapping column keys to row values in complex tabular schemas). Advanced document understanding uses tools like PaddleOCR, Docling, Azure Document Intelligence, Google Document AI, or AWS Textract."),

        ("h2", "18. Your Stage 1.4.2.5 learning target"),
        ("diagram", """Stage 1.4.2.5
│
├── Understand OCR
├── Choose Tesseract
├── Install Tesseract on Windows
├── Install pytesseract using UV
├── Verify Tesseract
├── Load scanned_page.png
├── Run first OCR
├── Inspect OCR output
├── Save OCR text
└── Convert OCR output into LangChain Document""", "TARGET CHECKLIST"),
        ("body", "The upcoming progression:"),
        ("diagram", """Stage 1.4.2.5: Basic OCR
      ↓
Stage 1.4.2.6: OCR preprocessing
      ↓
Stage 1.4.2.7: OCR quality evaluation
      ↓
Stage 1.4.2.8: OCR + PDF page pipeline
      ↓
Stage 1.4.2.9: OCR → LangChain Documents""", "ROADMAP"),

        ("h2", "One thing to do first"),
        ("body", "Before writing notebook code, verify your CLI environment:"),
        ("code", """tesseract --version
tesseract --list-langs
uv add pytesseract""", "POWERSHELL"),
        ("body", "Once these checks succeed, your environment is ready to execute OCR against <code>scanned_page.png</code> cell by cell.")
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
            t = Table(data, colWidths=[130, 95, 307][:len(data[0])])
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
    print(f"Successfully generated PDF: '{filename}'")

if __name__ == "__main__":
    build_pdf()