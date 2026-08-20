import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

DOCUMENT_NAME = "Stage 1.4.2.5.2 — Docling for Scanned PDFs"

# ----------------------------------------------------------------------
# 1. Register Local Unicode TrueType Fonts
# ----------------------------------------------------------------------
def init_fonts():
    win_fonts = {
        "DocSans": r"C:\Windows\Fonts\arial.ttf",
        "DocSans-Bold": r"C:\Windows\Fonts\arialbd.ttf",
        "DocMono": r"C:\Windows\Fonts\consola.ttf",
        "DocMono-Bold": r"C:\Windows\Fonts\consolab.ttf",
    }
    
    if all(os.path.exists(p) for p in win_fonts.values()):
        for name, path in win_fonts.items():
            pdfmetrics.registerFont(TTFont(name, path))
        return "DocSans", "DocSans-Bold", "DocMono", "DocMono-Bold"
    
    return "Helvetica", "Helvetica-Bold", "Courier", "Courier-Bold"

SANS, SANS_BOLD, MONO, MONO_BOLD = init_fonts()

# ----------------------------------------------------------------------
# 2. Numbered Canvas with Unified Running Header and Page Footer
# ----------------------------------------------------------------------
class PresentationCanvas(canvas.Canvas):
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
            self.draw_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_decorations(self, page_count):
        self.saveState()
        self.setFont(SANS, 8)
        self.setFillColor(colors.HexColor("#4B5563"))
        
        # Header on every page
        self.drawString(36, 760, DOCUMENT_NAME)
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.75)
        self.line(36, 752, 576, 752)
        
        # Footer on every page
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(576, 25, page_str)
        self.restoreState()

# ----------------------------------------------------------------------
# 3. PDF Generator
# ----------------------------------------------------------------------
def generate_presentation_pdf(output_filename=f"{DOCUMENT_NAME}.pdf"):
    doc = SimpleDocTemplate(
        output_filename,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=46,
        bottomMargin=42
    )

    doc_title_style = ParagraphStyle(
        'MainTitle',
        fontName=SANS_BOLD,
        fontSize=15,
        leading=19,
        textColor=colors.HexColor("#0F766E"),
        spaceAfter=3
    )
    doc_sub_style = ParagraphStyle(
        'SubTitle',
        fontName=SANS,
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#0F766E"),
        spaceAfter=8
    )
    step_heading_style = ParagraphStyle(
        'StepHeading',
        fontName=SANS_BOLD,
        fontSize=10,
        leading=13,
        textColor=colors.HexColor("#1E293B"),
        spaceBefore=7,
        spaceAfter=3
    )
    body_style = ParagraphStyle(
        'BodyDark',
        fontName=SANS,
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#1F2937"),
        spaceAfter=3
    )
    badge_style = ParagraphStyle(
        'Badge',
        fontName=SANS_BOLD,
        fontSize=7,
        leading=9,
        textColor=colors.HexColor("#0F766E")
    )
    code_text_style = ParagraphStyle(
        'CodeText',
        fontName=MONO,
        fontSize=7.5,
        leading=10.5,
        textColor=colors.HexColor("#0F172A")
    )
    table_cell_style = ParagraphStyle(
        'TblCell',
        fontName=SANS,
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#1F2937")
    )
    table_hdr_style = ParagraphStyle(
        'TblHdr',
        fontName=SANS_BOLD,
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#0F766E")
    )

    def render_card(badge_label, content_text):
        b_p = Paragraph(f"<b>{badge_label.upper()}</b>", badge_style)
        
        formatted = (
            content_text.strip()
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('\n', '<br/>')
            .replace(' ', '&nbsp;')
        )
        c_p = Paragraph(formatted, code_text_style)
        
        t = Table([[b_p], [Spacer(1, 2)], [c_p]], colWidths=[540])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F0FDFA")),
            ('BOX', (0, 0), (-1, -1), 0.75, colors.HexColor("#99F6E4")),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 7),
            ('RIGHTPADDING', (0, 0), (-1, -1), 7),
        ]))
        return t

    story = []

    # Introductory Header Block
    intro_txt = (
        "Yes. This is the point where we move from learning OCR mechanics to using a modern document-understanding library.<br/>"
        "For Stage 1.4.2.5.2 — Docling for Scanned PDFs, we'll use your existing scanned PDF directly. "
        "We will not manually convert it to scanned_page.png first. Docling's DocumentConverter can take a PDF directly, "
        "and its PDF pipeline supports OCR for scanned/image-based content. (Docling Project)"
    )
    story.append(Paragraph(intro_txt, body_style))
    story.append(Spacer(1, 4))

    # Stage Banner
    story.append(Paragraph(DOCUMENT_NAME, doc_title_style))
    story.append(Paragraph("Modern Document-Understanding Pipelines for Scanned Documents in RAG", doc_sub_style))

    # Goal
    story.append(Paragraph("Goal", step_heading_style))
    story.append(Paragraph("Our experiment will be:", body_style))
    goal_diag = (
        "Scanned PDF\n"
        "    │\n"
        "    ▼\n"
        "  Docling\n"
        "    │\n"
        "    ├── PDF processing\n"
        "    ├── OCR\n"
        "    ├── Layout understanding\n"
        "    └── Document representation\n"
        "    │\n"
        "    ▼\n"
        "DoclingDocument\n"
        "    │\n"
        "    ├── Markdown\n"
        "    ├── JSON\n"
        "    └── Text"
    )
    story.append(render_card("PIPELINE GOAL", goal_diag))
    story.append(Paragraph("This is much closer to how we want to approach document ingestion in a production RAG system.", body_style))
    story.append(Spacer(1, 3))

    # Step 1
    story.append(Paragraph("Step 1 — Install Docling", step_heading_style))
    story.append(Paragraph("From the root of your existing rag-learning project, run:", body_style))
    story.append(render_card("BASH", "uv add docling"))
    story.append(Paragraph("This is the installation command recommended by the current Docling documentation, and Docling supports Windows. (Docling Project)", body_style))
    story.append(Paragraph("After installation, verify:", body_style))
    story.append(render_card("BASH", 'uv run python -c "import docling; print(\'Docling installed successfully\')"'))
    story.append(Paragraph("You should get:", body_style))
    story.append(render_card("OUTPUT", "Docling installed successfully"))
    story.append(Paragraph("<b>Important</b><br/>At this stage, don't install pytesseract just for this exercise unless you already installed it from the previous lesson.<br/>Docling itself supports multiple OCR engines, including Tesseract, RapidOCR and EasyOCR. (Docling Project)<br/>For our first Docling experiment, we'll start with Docling's standard PDF pipeline rather than manually wiring an OCR engine.", body_style))
    story.append(Spacer(1, 3))

    # Step 2
    story.append(Paragraph("Step 2 — Verify the Notebook Kernel", step_heading_style))
    story.append(Paragraph("Open your existing notebook in VS Code.<br/>Make sure the selected kernel is the same Python environment managed by your uv project.<br/>Run:", body_style))
    story.append(render_card("PYTHON", "import sys\n\nprint(sys.executable)"))
    story.append(Paragraph("This is important because we want:", body_style))
    env_diag = (
        "VS Code Notebook\n"
        "       ↓\n"
        "your UV environment\n"
        "       ↓\n"
        "Docling"
    )
    story.append(render_card("ENVIRONMENT RESOLUTION", env_diag))
    story.append(Paragraph("and not some unrelated global Python installation.", body_style))
    story.append(Spacer(1, 3))

    # Step 3
    story.append(Paragraph("Step 3 — Import DocumentConverter", step_heading_style))
    story.append(Paragraph("Now create a new notebook cell:", body_style))
    story.append(render_card("PYTHON", "from docling.document_converter import DocumentConverter"))
    story.append(Paragraph("If this imports successfully, our basic Docling environment is ready.", body_style))
    story.append(Spacer(1, 3))

    # Step 4
    story.append(Paragraph("Step 4 — Define the Scanned PDF", step_heading_style))
    story.append(Paragraph("We are going to use the scanned PDF you already have.<br/>Don't create an image manually.<br/>For example:", body_style))
    code_s4 = (
        "from pathlib import Path\n\n"
        'pdf_path = Path("path/to/your/scanned.pdf")\n\n'
        "print(pdf_path.exists())\n"
        "print(pdf_path)"
    )
    story.append(render_card("PYTHON", code_s4))
    story.append(Paragraph("We want:\n\nTrue<br/>If you don't remember the exact location, we can identify it from your existing notebook/project files rather than guessing the path.", body_style))
    story.append(Spacer(1, 3))

    # Step 5
    story.append(Paragraph("Step 5 — Create the Docling Converter", step_heading_style))
    story.append(Paragraph("Now:", body_style))
    story.append(render_card("PYTHON", "converter = DocumentConverter()"))
    story.append(Paragraph("This is the central object we'll use.<br/>Conceptually:", body_style))
    conv_diag = (
        "DocumentConverter\n"
        "       │\n"
        "       ├── PDF\n"
        "       ├── DOCX\n"
        "       ├── PPTX\n"
        "       ├── XLSX\n"
        "       ├── Images\n"
        "       └── other supported formats"
    )
    story.append(render_card("DOCUMENT CONVERTER SCOPE", conv_diag))
    story.append(Paragraph("Docling's DocumentConverter is its primary entry point for converting documents into its unified document representation. (Docling Project)", body_style))
    story.append(Spacer(1, 3))

    # Step 6
    story.append(Paragraph("Step 6 — Convert the Scanned PDF", step_heading_style))
    story.append(Paragraph("Now the important line:", body_style))
    story.append(render_card("PYTHON", "result = converter.convert(pdf_path)"))
    story.append(Paragraph("That's it.<br/>Notice what we didn't write:<br/>❌ PDF → PNG manually<br/>❌ Pillow<br/>❌ pytesseract.image_to_string()<br/>❌ manually combine pages<br/><br/>Instead:", body_style))
    pipe_diag = (
        "Scanned PDF\n"
        "     ↓\n"
        "DocumentConverter\n"
        "     ↓\n"
        "Docling processing pipeline"
    )
    story.append(render_card("STREAMLINED PIPELINE", pipe_diag))
    story.append(Spacer(1, 3))

    # Step 7
    story.append(Paragraph("Step 7 — Understand What result Is", step_heading_style))
    story.append(Paragraph("Let's inspect:", body_style))
    story.append(render_card("PYTHON", "print(type(result))"))
    story.append(Paragraph("You'll get a Docling conversion result object.<br/>Now:", body_style))
    story.append(render_card("PYTHON", "print(result.status)"))
    story.append(Paragraph("And:", body_style))
    story.append(render_card("PYTHON", "print(result.document)"))
    story.append(Paragraph("The important object is:\n\nresult.document<br/>This is a DoclingDocument.<br/>Conceptually:", body_style))
    res_diag = (
        "result\n"
        " │\n"
        " ├── status\n"
        " ├── input information\n"
        " └── document\n"
        "       │\n"
        "       └── DoclingDocument"
    )
    story.append(render_card("RESULT COMPOSITION", res_diag))
    story.append(Spacer(1, 3))

    # Step 8
    story.append(Paragraph("Step 8 — Export the Result as Markdown", step_heading_style))
    story.append(Paragraph("Now let's see what Docling understood.", body_style))
    story.append(render_card("PYTHON", "markdown_text = result.document.export_to_markdown()"))
    story.append(Paragraph("Display it:", body_style))
    story.append(render_card("PYTHON", "print(markdown_text)"))
    story.append(Paragraph("This is where things become interesting.<br/>Instead of getting only raw OCR text, we're asking Docling to represent the processed document in Markdown.<br/>Docling's standard usage explicitly supports converting a document and exporting the resulting DoclingDocument to Markdown. (Docling Project)", body_style))
    story.append(Spacer(1, 3))

    # Step 9
    story.append(Paragraph("Step 9 — Save the Markdown", step_heading_style))
    story.append(Paragraph("Let's preserve the result:", body_style))
    code_s9 = (
        'markdown_path = Path("scanned_document_docling.md")\n\n'
        "markdown_path.write_text(\n"
        "    markdown_text,\n"
        '    encoding="utf-8"\n'
        ")\n\n"
        'print(f"Saved: {markdown_path}")'
    )
    story.append(render_card("PYTHON", code_s9))
    story.append(Paragraph("Now we have:", body_style))
    s9_flow = (
        "scanned.pdf\n"
        "      │\n"
        "      ▼\n"
        "    Docling\n"
        "      │\n"
        "      ▼\n"
        "scanned_document_docling.md"
    )
    story.append(render_card("OUTPUT ARTIFACT", s9_flow))
    story.append(Spacer(1, 3))

    # Step 10
    story.append(Paragraph("Step 10 — Export as JSON", step_heading_style))
    story.append(Paragraph("Now let's look at another important representation.", body_style))
    story.append(render_card("PYTHON", "json_text = result.document.export_to_json()"))
    story.append(Paragraph("Save it:", body_style))
    code_s10 = (
        'json_path = Path("scanned_document_docling.json")\n\n'
        "json_path.write_text(\n"
        "    json_text,\n"
        '    encoding="utf-8"\n'
        ")\n\n"
        'print(f"Saved: {json_path}")'
    )
    story.append(render_card("PYTHON", code_s10))
    story.append(Paragraph("Now:", body_style))
    s10_flow = (
        "Scanned PDF\n"
        "     │\n"
        "     ▼\n"
        "  DoclingDocument\n"
        "     │\n"
        "     ├── Markdown\n"
        "     │\n"
        "     └── JSON"
    )
    story.append(render_card("UNIVERSAL EXPORT ARTIFACTS", s10_flow))
    story.append(Paragraph("Docling's newer document model is specifically designed as a universal representation that can preserve document hierarchy and can be exported to formats including JSON and Markdown. (Docling Project)", body_style))
    story.append(Spacer(1, 3))

    # Step 11
    story.append(Paragraph("Step 11 — Inspect the JSON", step_heading_style))
    story.append(Paragraph("Let's see what we have.", body_style))
    code_s11 = (
        "import json\n\n"
        "doc_json = json.loads(json_text)\n\n"
        "print(type(doc_json))\n"
        "print(doc_json.keys())"
    )
    story.append(render_card("PYTHON", code_s11))
    story.append(Paragraph("Don't worry if the exact keys differ from what you expect.<br/>The important conceptual difference is:", body_style))
    comp_json = (
        "Basic OCR\n"
        "Image\n"
        "  ↓\n"
        "Text\n\n"
        "Docling\n"
        "Document\n"
        "   ↓\n"
        "Structured document representation"
    )
    story.append(render_card("CONCEPTUAL DIFFERENCE", comp_json))
    story.append(Paragraph("That distinction is extremely important for your RAG journey.", body_style))
    story.append(Spacer(1, 3))

    # Step 12
    story.append(Paragraph("Step 12 — Compare Basic OCR vs Docling", step_heading_style))
    story.append(Paragraph("Now let's explicitly compare the two approaches.", body_style))
    app_a = (
        "Approach A — Basic Tesseract\n"
        "Scanned PDF\n"
        "     ↓\n"
        "Page Image\n"
        "     ↓\n"
        "Tesseract\n"
        "     ↓\n"
        "Plain Text\n\n"
        "Output:\n"
        "\"Employee Details Name Department...\""
    )
    story.append(render_card("APPROACH A — TESSERACT", app_a))
    story.append(Spacer(1, 2))
    app_b = (
        "Approach B — Docling\n"
        "Scanned PDF\n"
        "     ↓\n"
        "Docling\n"
        "     ↓\n"
        "OCR + document processing\n"
        "     ↓\n"
        "DoclingDocument\n"
        "     ↓\n"
        "Markdown / JSON / other representations"
    )
    story.append(render_card("APPROACH B — DOCLING", app_b))
    story.append(Paragraph("Potentially:", body_style))
    
    table_sample = [
        [Paragraph("Name", table_hdr_style), Paragraph("Department", table_hdr_style), Paragraph("Experience", table_hdr_style)],
        [Paragraph("Ravi", table_cell_style), Paragraph("Data", table_cell_style), Paragraph("8", table_cell_style)],
        [Paragraph("Suresh", table_cell_style), Paragraph("IT", table_cell_style), Paragraph("10", table_cell_style)],
    ]
    t_tbl = Table(table_sample, colWidths=[150, 190, 200])
    t_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#CCFBF1")),
        ('BOX', (0, 0), (-1, -1), 0.75, colors.HexColor("#99F6E4")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t_tbl)
    story.append(Spacer(1, 2))
    story.append(Paragraph("The second representation is much more useful for downstream RAG processing.<br/>Docling's PDF pipeline also supports table-structure processing, which is one reason it is more appropriate for complex documents than treating everything as plain OCR text. (Docling Project)", body_style))
    story.append(Spacer(1, 3))

    # Step 13
    story.append(Paragraph("Step 13 — Check Whether OCR Actually Happened", step_heading_style))
    story.append(Paragraph("This is an important experiment.<br/>Our input is a scanned PDF.<br/>Therefore, we want to see whether Docling was able to recover text from the page.<br/>Start with:", body_style))
    story.append(render_card("PYTHON", "print(markdown_text[:3000])"))
    story.append(Paragraph("Look at the output.<br/>If you see meaningful text from the scanned document, Docling successfully processed the scanned content.", body_style))
    story.append(Spacer(1, 3))

    # Step 14
    story.append(Paragraph("Step 14 — Understand What Docling Is Doing for Us", step_heading_style))
    story.append(Paragraph("This is the key learning point.<br/>Previously:", body_style))
    prev_diag = (
        "PDF\n"
        " ↓\n"
        "render page\n"
        " ↓\n"
        "PNG\n"
        " ↓\n"
        "Tesseract\n"
        " ↓\n"
        "text"
    )
    story.append(render_card("PREVIOUS WORKFLOW", prev_diag))
    story.append(Spacer(1, 2))
    story.append(Paragraph("Now:", body_style))
    now_diag = (
        "PDF\n"
        " ↓\n"
        "Docling PDF pipeline\n"
        " ↓\n"
        "document processing\n"
        " ├── OCR\n"
        " ├── layout\n"
        " ├── reading order\n"
        " ├── table structure\n"
        " └── document representation\n"
        " ↓\n"
        "DoclingDocument"
    )
    story.append(render_card("DOCLING UNIFIED WORKFLOW", now_diag))
    story.append(Paragraph("That's why I recommended moving toward Docling.", body_style))
    story.append(Spacer(1, 3))

    # Step 15
    story.append(Paragraph("Step 15 — But Don't Assume Docling Solves Everything", step_heading_style))
    story.append(Paragraph("This is important for your production-grade RAG learning.<br/>Docling is not magic.<br/>For example:", body_style))
    story.append(render_card("EXAMPLE A", "Scanned architecture diagram\nis different from:\nScanned paragraph"))
    story.append(Paragraph("And:", body_style))
    story.append(render_card("EXAMPLE B", "Mathematical formula\nis different from:\nTable"))
    story.append(Paragraph("Docling has additional enrichment capabilities and different processing pipelines for more advanced scenarios. Its current CLI, for example, exposes options for formula enrichment, picture description, chart extraction and other processing capabilities. (Docling Project)<br/>We'll learn those after we understand the basic Docling pipeline.", body_style))
    story.append(Spacer(1, 3))

    # Step 16
    story.append(Paragraph("Step 16 — Our First RAG-Oriented Architecture", step_heading_style))
    story.append(Paragraph("At this point, our architecture becomes:", body_style))
    rag_arch = (
        "                    DOCUMENT\n"
        "                       │\n"
        "                       ▼\n"
        "                    Docling\n"
        "                       │\n"
        "             ┌─────────┴─────────┐\n"
        "             │                   │\n"
        "          Text/Table          Images/etc.\n"
        "             │\n"
        "             ▼\n"
        "       DoclingDocument\n"
        "             │\n"
        "             ▼\n"
        "       Markdown / JSON\n"
        "             │\n"
        "             ▼\n"
        "       RAG preprocessing\n"
        "             │\n"
        "             ▼\n"
        "          Chunking\n"
        "             │\n"
        "             ▼\n"
        "         Embeddings\n"
        "             │\n"
        "             ▼\n"
        "        Vector Store"
    )
    story.append(render_card("RAG-ORIENTED INGESTION ARCHITECTURE", rag_arch))
    story.append(Paragraph("This is much closer to the architecture we'll eventually use in your production-grade RAG.", body_style))
    story.append(Spacer(1, 3))

    # Step 17
    story.append(Paragraph("Step 17 — What We Are NOT Doing Yet", step_heading_style))
    story.append(Paragraph("For this stage, don't add:<br/>• custom OCR preprocessing<br/>• OpenCV<br/>• image thresholding<br/>• manual Tesseract configuration<br/>• table extraction tuning<br/>• formula extraction<br/>• chart extraction<br/>• VLM pipelines<br/>• LangChain integration<br/>• chunking<br/><br/>Those belong to later stages.<br/>We're learning one thing now: <b>How can Docling ingest a scanned PDF and turn it into a structured document representation?</b>", body_style))
    story.append(Spacer(1, 3))

    # Step 18
    story.append(Paragraph("Step 18 — Your Notebook Cells for This Stage", step_heading_style))
    story.append(Paragraph("You can keep the implementation very small.", body_style))
    
    code_s18_c1 = "from pathlib import Path\nfrom docling.document_converter import DocumentConverter"
    story.append(render_card("CELL 1 — IMPORT", code_s18_c1))
    story.append(Spacer(1, 2))
    
    code_s18_c2 = 'pdf_path = Path("path/to/your/scanned.pdf")\n\nprint("Exists:", pdf_path.exists())\nprint("Path:", pdf_path)'
    story.append(render_card("CELL 2 — PDF", code_s18_c2))
    story.append(Spacer(1, 2))
    
    code_s18_c3 = "converter = DocumentConverter()"
    story.append(render_card("CELL 3 — CONVERTER", code_s18_c3))
    story.append(Spacer(1, 2))
    
    code_s18_c4 = "result = converter.convert(pdf_path)\n\nprint(\"Status:\", result.status)"
    story.append(render_card("CELL 4 — CONVERT", code_s18_c4))
    story.append(Spacer(1, 2))
    
    code_s18_c5 = "doc = result.document\n\nprint(type(doc))"
    story.append(render_card("CELL 5 — GET DOCLING DOCUMENT", code_s18_c5))
    story.append(Spacer(1, 2))
    
    code_s18_c6 = "markdown_text = doc.export_to_markdown()\n\nprint(markdown_text)"
    story.append(render_card("CELL 6 — MARKDOWN", code_s18_c6))
    story.append(Spacer(1, 2))
    
    code_s18_c7 = 'Path("scanned_document_docling.md").write_text(\n    markdown_text,\n    encoding="utf-8"\n)\n\nprint("Markdown saved.")'
    story.append(render_card("CELL 7 — SAVE MARKDOWN", code_s18_c7))
    story.append(Spacer(1, 2))
    
    code_s18_c8 = 'json_text = doc.export_to_json()\n\nPath("scanned_document_docling.json").write_text(\n    json_text,\n    encoding="utf-8"\n)\n\nprint("JSON saved.")'
    story.append(render_card("CELL 8 — JSON", code_s18_c8))
    story.append(Spacer(1, 3))

    # Step 19
    story.append(Paragraph("Step 19 — One Important Thing About OCR Configuration", step_heading_style))
    story.append(Paragraph("There's a subtle point here.<br/>Docling's current PDF pipeline supports OCR, but its OCR configuration is customizable. The documentation exposes PdfPipelineOptions, including do_ocr and OCR engine options. (Docling Project)<br/>So eventually we can explicitly configure:", body_style))
    ocr_cfg_diag = (
        "Docling\n"
        "   │\n"
        "   ▼\n"
        "PDF Pipeline\n"
        "   │\n"
        "   ├── OCR enabled\n"
        "   │\n"
        "   ├── OCR engine = RapidOCR\n"
        "   │\n"
        "   ├── OCR engine = Tesseract\n"
        "   │\n"
        "   └── OCR engine = EasyOCR"
    )
    story.append(render_card("OCR ENGINE CONFIGURATION OPTIONS", ocr_cfg_diag))
    story.append(Paragraph("For this first experiment, however, I want you to see what the standard Docling pipeline gives us before we start changing its internals.", body_style))
    story.append(Spacer(1, 3))

    # Step 20
    story.append(Paragraph("Step 20 — What You've Achieved", step_heading_style))
    story.append(Paragraph("This is the important transition in your RAG journey:", body_style))
    story.append(render_card("BEFORE", "You were learning:\nHow does OCR work?"))
    story.append(Spacer(1, 2))
    story.append(render_card("NOW", "You're learning:\nHow do modern document-processing frameworks\nhandle OCR and complex documents for RAG?"))
    story.append(Paragraph("And that's much closer to your actual goal.<br/>Your current journey is now:", body_style))
    roadmap_diag = (
        "Stage 1.4.2\n"
        "OCR & Complex PDF Ingestion\n"
        "        │\n"
        "        └── Stage 1.4.2.5\n"
        "            OCR Approach\n"
        "                 │\n"
        "                 ├── 1.4.2.5.1\n"
        "                 │   Basic OCR\n"
        "                 │\n"
        "                 └── 1.4.2.5.2\n"
        "                     Docling for Scanned PDFs ← CURRENT"
    )
    story.append(render_card("LEARNING ROADMAP", roadmap_diag))
    story.append(Spacer(1, 3))

    # Concluding Instructions
    story.append(Paragraph("Next Actions", step_heading_style))
    story.append(Paragraph("Run Steps 1–8 first. In particular, after <code>result = converter.convert(pdf_path)</code>, inspect the Markdown output from your actual scanned PDF. That output will determine what we investigate next rather than blindly moving ahead.", body_style))

    doc.build(story, canvasmaker=PresentationCanvas)
    print(f"Generated presentation-grade PDF: {output_filename}")

if __name__ == "__main__":
    generate_presentation_pdf()