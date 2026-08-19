import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

DOCUMENT_NAME = "Stage 1.4.2.5.3 — Docling Layout & Reading Order"

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
# 2. Numbered Canvas with Unified Header
# ----------------------------------------------------------------------
class GuideCanvas(canvas.Canvas):
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
        
        # Bottom Footer
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(576, 25, page_str)
        self.restoreState()

# ----------------------------------------------------------------------
# 3. PDF Generator
# ----------------------------------------------------------------------
def generate_exact_pdf():
    output_filename = f"{DOCUMENT_NAME}.pdf"
    
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

    # Initialize story list
    story = []

    # Title Banner
    story.append(Paragraph(DOCUMENT_NAME, doc_title_style))
    story.append(Paragraph("Document Understanding and Reading Order Integrity for RAG", doc_sub_style))

    # Objective
    story.append(Paragraph("Objective", step_heading_style))
    story.append(Paragraph("We already learned:", body_style))
    story.append(Paragraph("Stage 1.4.2.5.1 — Basic OCR", body_style))
    story.append(render_card("BASIC OCR PIPELINE", "Image\n  ↓\nOCR\n  ↓\nText"))
    story.append(Spacer(1, 3))
    
    story.append(Paragraph("Then:", body_style))
    story.append(Paragraph("Stage 1.4.2.5.2 — Docling for Scanned PDFs", body_style))
    story.append(render_card("DOCLING PIPELINE", "Scanned PDF\n     ↓\n  Docling\n     ↓\nDoclingDocument\n     ↓\nMarkdown / structured representation"))
    story.append(Spacer(1, 3))

    story.append(Paragraph("Now we're asking a deeper question:", body_style))
    story.append(Paragraph("Can Docling understand the layout of a document and determine the correct logical reading order?", body_style))
    story.append(Spacer(1, 3))

    # Step 1
    story.append(Paragraph("Step 1 — Understand the Problem", step_heading_style))
    story.append(Paragraph("Consider a document like this:", body_style))
    box_diag = (
        "┌──────────────────────┬──────────────────────┐\n"
        "│ Heading A            │ Heading B            │\n"
        "│                      │                      │\n"
        "│ Paragraph A1         │ Paragraph B1         │\n"
        "│ Paragraph A2         │ Paragraph B2         │\n"
        "│                      │                      │\n"
        "└──────────────────────┴──────────────────────┘"
    )
    story.append(render_card("VISUAL LAYOUT", box_diag))
    story.append(Spacer(1, 3))
    
    story.append(Paragraph("A naive text extractor might produce:", body_style))
    naive_txt = "Heading A\nHeading B\nParagraph A1\nParagraph B1\nParagraph A2\nParagraph B2"
    story.append(render_card("NAIVE EXTRACTION", naive_txt))
    story.append(Spacer(1, 3))
    
    story.append(Paragraph("But the logical reading order might be:", body_style))
    logical_txt = "Heading A\nParagraph A1\nParagraph A2\n\nHeading B\nParagraph B1\nParagraph B2"
    story.append(render_card("LOGICAL READING ORDER", logical_txt))
    story.append(Paragraph("That's the problem layout and reading-order analysis tries to solve.", body_style))
    story.append(Spacer(1, 3))

    # Step 2
    story.append(Paragraph("Step 2 — Understand Why This Matters to RAG", step_heading_style))
    story.append(Paragraph("This is extremely important. Suppose a PDF contains:", body_style))
    col_diag = "Column 1                  Column 2\n\nAzure Event Hubs          Azure Data Explorer\n\nEvent ingestion           Analytics\n\nHigh-volume events        Query processing"
    story.append(render_card("MULTI-COLUMN INPUT", col_diag))
    story.append(Spacer(1, 3))
    
    story.append(Paragraph("If the extraction order is wrong, we might create a chunk such as:", body_style))
    corrupt_chunk = "Azure Event Hubs\nAzure Data Explorer\nEvent ingestion\nAnalytics\nHigh-volume events\nQuery processing"
    story.append(render_card("CORRUPTED EXTRACTION", corrupt_chunk))
    story.append(Paragraph("The text exists, but its relationships have been damaged. That can negatively affect:", body_style))
    story.append(render_card("RAG DEGRADATION FLOW", "Chunking\n   ↓\nEmbedding\n   ↓\nRetrieval\n   ↓\nLLM context"))
    story.append(Paragraph("Therefore:\n\nGood RAG begins with good document understanding.", body_style))
    story.append(Spacer(1, 3))

    # Step 3
    story.append(Paragraph("Step 3 — Locate the Sample PDF", step_heading_style))
    story.append(Paragraph("Download the sample PDF above and place it somewhere accessible from your notebook. For example:", body_style))
    tree_path = "rag-learning/\n│\n├── notebooks/\n│\n├── data/\n│   └── docling_layout_reading_order_sample.pdf\n│\n└── ..."
    story.append(render_card("DIRECTORY STRUCTURE", tree_path))
    story.append(Spacer(1, 3))
    
    story.append(Paragraph("Then:", body_style))
    code_s3 = 'from pathlib import Path\n\npdf_path = Path(\n    "../../data/docling_layout_reading_order_sample.pdf"\n)\n\nprint(pdf_path.exists())\nprint(pdf_path)'
    story.append(render_card("PYTHON", code_s3))
    story.append(Paragraph("Adjust the path according to where you saved it. We want:\n\nTrue", body_style))
    story.append(Spacer(1, 3))

    # Step 4
    story.append(Paragraph("Step 4 — Check Your Docling Version", step_heading_style))
    story.append(Paragraph("We're using your installed:\n\nDocling 2.120.3\n\nLet's confirm from the notebook:", body_style))
    code_s4 = 'import importlib.metadata\n\nprint(importlib.metadata.version("docling"))'
    story.append(render_card("PYTHON", code_s4))
    story.append(Paragraph("Expected:\n\n2.120.3", body_style))
    story.append(Spacer(1, 3))

    # Step 5
    story.append(Paragraph("Step 5 — Create the Document Converter", step_heading_style))
    story.append(Paragraph("Use the same approach from Stage 1.4.2.5.2:", body_style))
    code_s5 = "from docling.document_converter import DocumentConverter\n\nconverter = DocumentConverter()"
    story.append(render_card("PYTHON", code_s5))
    story.append(Spacer(1, 3))

    # Step 6
    story.append(Paragraph("Step 6 — Convert the Sample PDF", step_heading_style))
    story.append(Paragraph("Run:", body_style))
    code_s6 = "result = converter.convert(pdf_path)\n\nprint(result.status)"
    story.append(render_card("PYTHON", code_s6))
    story.append(Paragraph("We want a successful conversion.", body_style))
    story.append(Spacer(1, 3))

    # Step 7
    story.append(Paragraph("Step 7 — Get the DoclingDocument", step_heading_style))
    code_s7 = "doc = result.document\nprint(type(doc))"
    story.append(render_card("PYTHON", code_s7))
    story.append(Paragraph("You should get a DoclingDocument.", body_style))
    story.append(Spacer(1, 3))

    # Step 8
    story.append(Paragraph("Step 8 — Export to Markdown", step_heading_style))
    story.append(Paragraph("This is our first way to observe the result:", body_style))
    code_s8 = "markdown_text = doc.export_to_markdown()\n\nprint(markdown_text)"
    story.append(render_card("PYTHON", code_s8))
    story.append(Paragraph("What are we looking for? Look carefully at: Heading order, Paragraph order, Two-column content, Table position, Caption position, Page transitions.", body_style))
    story.append(Paragraph("Don't just ask:\n\"Did Docling extract the words?\"\nAsk:\n\"Did Docling preserve the logical structure?\"\nThat's the purpose of this stage.", body_style))
    story.append(Spacer(1, 3))

    # Step 9
    story.append(Paragraph("Step 9 — Inspect the Page Structure", step_heading_style))
    story.append(Paragraph("Now we want to go deeper than Markdown. The DoclingDocument contains structured information about document elements. Let's first inspect what is available:", body_style))
    code_s9 = 'print(type(doc))\n[m for m in dir(doc) if not m.startswith("_")]'
    story.append(render_card("PYTHON", code_s9))
    story.append(Paragraph("This is useful because we're working specifically with Docling 2.120.3, rather than blindly copying APIs from another version.", body_style))
    story.append(Spacer(1, 3))

    # Step 10
    story.append(Paragraph("Step 10 — Inspect Document Items", step_heading_style))
    story.append(Paragraph("For this stage, one particularly useful concept is the document's items. Try:", body_style))
    code_s10 = "print(doc.body)\nprint(doc.__dict__.keys())"
    story.append(render_card("PYTHON", code_s10))
    story.append(Paragraph("We're looking for how Docling 2.120.3 represents the document internally. Depending on the exact object structure exposed by your installed version, we'll inspect the relevant collections rather than assuming a particular API.", body_style))
    story.append(Spacer(1, 3))

    # Step 11
    story.append(Paragraph("Step 11 — Why We Are Inspecting the Structure", step_heading_style))
    story.append(Paragraph("Imagine Docling internally recognizes something like:", body_style))
    tree_p1 = "Page 1\n│\n├── Heading\n├── Paragraph\n├── Paragraph\n├── Heading\n├── Paragraph\n├── Table\n└── Caption"
    story.append(render_card("DOCUMENT STRUCTURE", tree_p1))
    story.append(Paragraph("That's much more useful than:\none giant string\nbecause later we can make intelligent decisions about chunking. For example:", body_style))
    story.append(render_card("SEMANTIC CHUNKING", "Heading\n   +\nParagraphs\n   ↓\none semantic chunk\nrather than blindly doing:\nevery 500 characters"))
    story.append(Spacer(1, 3))

    # Step 12
    story.append(Paragraph("Step 12 — Inspect the Markdown More Carefully", step_heading_style))
    story.append(Paragraph("Let's print the first page's extracted Markdown separately if possible, but first simply inspect:", body_style))
    code_s12 = "print(markdown_text[:5000])"
    story.append(render_card("PYTHON", code_s12))
    story.append(Paragraph("Look for something like:", body_style))
    md_sample = "# Azure Event Processing Architecture\n\n## 1. Overview\n...\n## 2. Processing Stages\n...\n| Stage | Component | Purpose |\n|---|---|---|\n..."
    story.append(render_card("MARKDOWN PREVIEW", md_sample))
    story.append(Paragraph("The exact result will depend on how Docling interprets the generated PDF.", body_style))
    story.append(Spacer(1, 3))

    # Step 13
    story.append(Paragraph("Step 13 — Focus on Reading Order", step_heading_style))
    story.append(Paragraph("Our sample contains this logical sequence:", body_style))
    seq_txt = "1. Overview\n\n2. Ingestion Layer\n\n3. Analytics Layer\n\n4. Processing Stages\n\n5. Important Design Considerations"
    story.append(render_card("LOGICAL SEQUENCE", seq_txt))
    story.append(Paragraph("We intentionally designed the document so that the visual layout isn't simply a single linear stream. The question we're testing is:\n\nVisual position\n      ≠\nLogical reading order\n\nA document-understanding system needs to infer the latter.", body_style))
    story.append(Spacer(1, 3))

    # Step 14
    story.append(Paragraph("Step 14 — Compare with a Naive Text Extraction Approach", step_heading_style))
    story.append(Paragraph("This comparison is useful.", body_style))
    comp_naive = "Naive PDF extraction\nPDF\n ↓\nText extraction\n ↓\nString\nPotential problem:\nWrong ordering\nLost relationships\nLost layout\nLost table structure"
    comp_docling = "Docling\nPDF\n ↓\nDocument understanding\n ↓\nLayout\n ↓\nReading order\n ↓\nStructured document\nPotentially:\nHeading\n   ↓\nParagraph\n   ↓\nParagraph\n   ↓\nTable\n   ↓\nCaption"
    story.append(render_card("NAIVE PDF EXTRACTION", comp_naive))
    story.append(Spacer(1, 2))
    story.append(render_card("DOCLING EXTRACTION", comp_docling))
    story.append(Paragraph("That's why we're learning Docling.", body_style))
    story.append(Spacer(1, 3))

    # Step 15
    story.append(Paragraph("Step 15 — Understand Reading Order in RAG", step_heading_style))
    story.append(Paragraph("Suppose our document says: Azure Event Hubs and underneath it: Event ingestion platform. Then in another column: Azure Data Explorer with: Analytics platform. If our parser mixes them up, the resulting embedding might represent a distorted relationship. Instead, we want:", body_style))
    correct_rel = "Azure Event Hubs\n    ↓\nEvent ingestion platform\nand:\nAzure Data Explorer\n    ↓\nAnalytics platform"
    story.append(render_card("RELATIONSHIPS", correct_rel))
    story.append(Paragraph("This produces much better semantic units for subsequent chunking.", body_style))
    story.append(Spacer(1, 3))

    # Step 16
    story.append(Paragraph("Step 16 — Understand the Relationship with Chunking", step_heading_style))
    story.append(Paragraph("This is one of the most important lessons from this stage. We previously learned that chunking strategy matters. But now notice:", body_style))
    chunk_flow = "Document Understanding\n        ↓\nLayout\n        ↓\nReading Order\n        ↓\nSemantic Structure\n        ↓\nChunking"
    story.append(render_card("INGESTION FLOW", chunk_flow))
    story.append(Paragraph("Therefore: You shouldn't think of chunking as an isolated operation. The quality of your chunks depends partly on how well you understand the source document. This is why modern RAG ingestion pipelines increasingly use document-understanding frameworks.", body_style))
    story.append(Spacer(1, 3))

    # Step 17
    story.append(Paragraph("Step 17 — Inspect the Table", step_heading_style))
    story.append(Paragraph("Our sample PDF contains a table:\n\nStage | Component | Purpose", body_style))
    tbl_raw = [
        [Paragraph("Stage", table_hdr_style), Paragraph("Component", table_hdr_style), Paragraph("Purpose", table_hdr_style)],
        [Paragraph("1", table_cell_style), Paragraph("Event Producer", table_cell_style), Paragraph("Publishes raw event streaming payload", table_cell_style)],
        [Paragraph("2", table_cell_style), Paragraph("Azure Event Hubs", table_cell_style), Paragraph("Ingests high-throughput data streams", table_cell_style)],
        [Paragraph("3", table_cell_style), Paragraph("Azure Data Explorer", table_cell_style), Paragraph("Low-latency real-time analytics query engine", table_cell_style)],
    ]
    tbl_flowable = Table(tbl_raw, colWidths=[45, 155, 340])
    tbl_flowable.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#CCFBF1")),
        ('BOX', (0, 0), (-1, -1), 0.75, colors.HexColor("#99F6E4")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(tbl_flowable)
    story.append(Spacer(1, 3))
    
    story.append(Paragraph("After conversion:", body_style))
    code_s17 = "markdown_text = doc.export_to_markdown()\n\nprint(markdown_text)"
    story.append(render_card("PYTHON", code_s17))
    story.append(Paragraph("Look for a Markdown table. If Docling preserves it as:\n| Stage | Component | Purpose |\n|---|---|---|\n| 1 | Event Producer | ... |\n| 2 | Azure Event Hubs | ... |\nthat's an important observation.", body_style))
    story.append(Paragraph("Compare that with basic OCR, which could produce:", body_style))
    ocr_raw_table = "Stage Component Purpose\n1 Event Producer Publishes...\n2 Azure Event Hubs Ingests..."
    story.append(render_card("UNSTRUCTURED OCR OUTPUT", ocr_raw_table))
    story.append(Paragraph("The second output contains the words but may have lost the explicit table relationships.", body_style))
    story.append(Spacer(1, 3))

    # Step 18 (Exact Centered Axis Layout)
    story.append(Paragraph("Step 18 — The Architecture We Are Building Toward", step_heading_style))
    story.append(Paragraph("Our ingestion architecture is gradually becoming:", body_style))
    arch_full = (
        "                    Enterprise PDF\n"
        "                          │\n"
        "                          ▼\n"
        "                       Docling\n"
        "                          │\n"
        "           ┌──────────────┼──────────────┐\n"
        "           │              │              │\n"
        "           ▼              ▼              ▼\n"
        "          OCR           Layout         Tables\n"
        "           │              │              │\n"
        "           └──────────────┼──────────────┘\n"
        "                          ▼\n"
        "                  DoclingDocument\n"
        "                          │\n"
        "                          ▼\n"
        "                    Reading Order\n"
        "                          │\n"
        "                          ▼\n"
        "                  Structured Content\n"
        "                          │\n"
        "                          ▼\n"
        "                       Chunking\n"
        "                          │\n"
        "                          ▼\n"
        "                      Embedding\n"
        "                          │\n"
        "                          ▼\n"
        "                     Vector Store"
    )
    story.append(render_card("INGESTION ARCHITECTURE", arch_full))
    story.append(Paragraph("This is the conceptual reason we're doing this stage.", body_style))
    story.append(Spacer(1, 3))

    # Step 19
    story.append(Paragraph("Step 19 — What We Are NOT Doing Yet", step_heading_style))
    story.append(Paragraph("Don't worry about: OCR engine tuning, Tesseract configuration, image preprocessing, formula enrichment, picture description, multimodal embeddings, table-specific chunking, LangChain integration. Those are separate concerns.", body_style))
    story.append(Paragraph("Our question right now is simply:\nCan Docling correctly understand the spatial organization and logical reading order of our document?", body_style))
    story.append(Spacer(1, 3))

    # Step 20
    story.append(Paragraph("Step 20 — Your Hands-On Experiment", step_heading_style))
    story.append(Paragraph("Run these cells in order.", body_style))
    
    code_s20_c1 = "from pathlib import Path\nfrom docling.document_converter import DocumentConverter"
    story.append(render_card("CELL 1", code_s20_c1))
    story.append(Spacer(1, 2))
    
    code_s20_c2 = 'pdf_path = Path(\n    "path/to/docling_layout_reading_order_sample.pdf"\n)\n\nprint("Exists:", pdf_path.exists())'
    story.append(render_card("CELL 2", code_s20_c2))
    story.append(Spacer(1, 2))
    
    code_s20_c3 = "converter = DocumentConverter()"
    story.append(render_card("CELL 3", code_s20_c3))
    story.append(Spacer(1, 2))
    
    code_s20_c4 = "result = converter.convert(pdf_path)\n\nprint(\"Status:\", result.status)"
    story.append(render_card("CELL 4", code_s20_c4))
    story.append(Spacer(1, 2))
    
    code_s20_c5 = "doc = result.document\n\nprint(type(doc))"
    story.append(render_card("CELL 5", code_s20_c5))
    story.append(Spacer(1, 2))
    
    code_s20_c6 = "markdown_text = doc.export_to_markdown()\n\nprint(markdown_text)"
    story.append(render_card("CELL 6", code_s20_c6))
    story.append(Spacer(1, 2))
    
    code_s20_c7 = "print(doc.__dict__.keys())"
    story.append(render_card("CELL 7", code_s20_c7))
    story.append(Spacer(1, 2))
    
    code_s20_c8 = 'print([m for m in dir(doc) if not m.startswith("_")])'
    story.append(render_card("CELL 8", code_s20_c8))
    story.append(Spacer(1, 3))

    # Observation Block
    story.append(Paragraph("The key thing I want you to observe", step_heading_style))
    story.append(Paragraph("Don't worry yet about writing a lot of code. After running the conversion, look at the Markdown output and compare it against the visual PDF. We're testing three things:", body_style))
    obs_flow = "1. Did Docling recognize the headings?\n        ↓\n2. Did it preserve the logical reading order?\n        ↓\n3. Did it preserve the table structure?"
    story.append(render_card("VERIFICATION CRITERIA", obs_flow))
    story.append(Paragraph("Once we see your actual output from Docling 2.120.3, we'll inspect the DoclingDocument structure in the next step and learn how Docling represents layout and reading order internally. That is much more valuable than simply calling an export method and moving on.", body_style))

    doc.build(story, canvasmaker=GuideCanvas)
    print(f"Generated PDF with exact text: {output_filename}")

if __name__ == "__main__":
    generate_exact_pdf()