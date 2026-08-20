"""Generates a presentation-grade PDF roadmap using ReportLab with exact text preservation,

TrueType Unicode font support for box-drawing trees, and gold Unicode star
ratings.
"""

from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# --- Register Windows TrueType Fonts (Full Unicode Support) ---
try:
  # Monospace for ASCII and Tree diagrams
  pdfmetrics.registerFont(
      TTFont("ConsolasRegular", "C:/Windows/Fonts/consola.ttf")
  )
  pdfmetrics.registerFont(
      TTFont("ConsolasBold", "C:/Windows/Fonts/consolab.ttf")
  )
  MONO_FONT = "ConsolasRegular"
except Exception:
  MONO_FONT = "Courier"

try:
  # Sans-serif for Body and Headings (Supports Unicode ★ Stars)
  pdfmetrics.registerFont(TTFont("SegoeUI", "C:/Windows/Fonts/segoeui.ttf"))
  pdfmetrics.registerFont(TTFont("SegoeUI-Bold", "C:/Windows/Fonts/seguib.ttf"))
  SANS_REG = "SegoeUI"
  SANS_BOLD = "SegoeUI-Bold"
except Exception:
  try:
    pdfmetrics.registerFont(TTFont("ArialUnicode", "C:/Windows/Fonts/arial.ttf"))
    pdfmetrics.registerFont(
        TTFont("ArialUnicode-Bold", "C:/Windows/Fonts/arialbd.ttf")
    )
    SANS_REG = "ArialUnicode"
    SANS_BOLD = "ArialUnicode-Bold"
  except Exception:
    SANS_REG = "Helvetica"
    SANS_BOLD = "Helvetica-Bold"

# Reusable gold star rating component
GOLD_STARS = '<font color="#eab308" face="' + SANS_REG + '">★ ★ ★ ★ ★</font>'


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
    self.setFont(SANS_BOLD, 8)
    self.setFillColor(colors.HexColor("#64748b"))

    # Header
    self.drawString(
        54, 842 - 36, "STAGE 1.4.2 — INGESTION & DOCUMENT UNDERSTANDING"
    )
    self.setStrokeColor(colors.HexColor("#e2e8f0"))
    self.setLineWidth(0.75)
    self.line(54, 842 - 42, 595 - 54, 842 - 42)

    # Footer
    self.setFont(SANS_REG, 8)
    self.drawString(54, 36, "Docling Architecture & RAG Roadmap")
    page_str = f"Page {self._pageNumber} of {page_count}"
    self.drawRightString(595 - 54, 36, page_str)
    self.restoreState()


def create_ascii_table(text: str, available_width: float = 487) -> Table:
  safe_text = (
      text.replace("&", "&amp;")
      .replace("<", "&lt;")
      .replace(">", "&gt;")
      .replace(" ", "&nbsp;")
      .replace("\n", "<br/>")
  )
  style = ParagraphStyle(
      name="AsciiMonospace",
      fontName=MONO_FONT,
      fontSize=8.2,
      leading=11.5,
      textColor=colors.HexColor("#0f172a"),
  )
  p = Paragraph(safe_text, style)
  t = Table([[p]], colWidths=[available_width])
  t.setStyle(
      TableStyle([
          ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
          ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
          ("LINELEFT", (0, 0), (0, -1), 3.0, colors.HexColor("#0284c7")),
          ("TOPPADDING", (0, 0), (-1, -1), 6),
          ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
          ("LEFTPADDING", (0, 0), (-1, -1), 10),
          ("RIGHTPADDING", (0, 0), (-1, -1), 8),
      ])
  )
  return t


def build_pdf(filename: str = "docling_learning_track.pdf"):
  doc = SimpleDocTemplate(
      filename,
      pagesize=A4,
      leftMargin=54,
      rightMargin=54,
      topMargin=54,
      bottomMargin=54,
  )

  title_style = ParagraphStyle(
      name="DocTitle",
      fontName=SANS_BOLD,
      fontSize=18,
      leading=22,
      textColor=colors.HexColor("#0f172a"),
      spaceAfter=12,
  )

  h2_style = ParagraphStyle(
      name="H2Heading",
      fontName=SANS_BOLD,
      fontSize=12,
      leading=16,
      textColor=colors.HexColor("#0369a1"),
      spaceBefore=14,
      spaceAfter=6,
      keepWithNext=True,
  )

  h3_style = ParagraphStyle(
      name="H3Heading",
      fontName=SANS_BOLD,
      fontSize=10.5,
      leading=14,
      textColor=colors.HexColor("#0f172a"),
      spaceBefore=10,
      spaceAfter=4,
      keepWithNext=True,
  )

  body_style = ParagraphStyle(
      name="BodyTextCustom",
      fontName=SANS_REG,
      fontSize=9.5,
      leading=13.5,
      textColor=colors.HexColor("#334155"),
      spaceAfter=6,
  )

  story = []

  # Title
  story.append(
      Paragraph(
          "Docling Learning Track &amp; Architecture Roadmap", title_style
      )
  )

  # Lead Paragraph
  story.append(
      Paragraph(
          "Yes. In fact, now that you've stepped into Docling, I would slightly"
          " change our learning path.<br/>Your original OCR path is useful for"
          " understanding fundamentals, but for a production-grade RAG, you"
          " don't want to spend the entire ingestion journey building OCR"
          " pipelines manually. Docling gives us a much broader"
          " document-understanding capability.",
          body_style,
      )
  )
  story.append(Paragraph("Think of it this way:", body_style))

  story.append(
      create_ascii_table("""OCR
└── "Can I read the text?"

Docling
└── "Can I understand the document?\"""")
  )
  story.append(Spacer(1, 6))

  story.append(
      Paragraph(
          "And that is much more interesting for your RAG journey.", body_style
      )
  )

  story.append(
      Paragraph(
          "What else should we learn from the Docling perspective?", h2_style
      )
  )
  story.append(
      Paragraph(
          "I would create a dedicated Docling Learning Track inside Stage"
          " 1.4.2.<br/>We have already completed:",
          body_style,
      )
  )

  story.append(
      create_ascii_table("""Stage 1.4.2.5.2
Docling for Scanned PDFs                         [OK]

Stage 1.4.2.5.3
Docling Layout & Reading Order                  [OK]""")
  )
  story.append(Spacer(1, 6))

  story.append(
      Paragraph("From here, I recommend learning these areas.", body_style)
  )

  # 1. Docling Document Model
  block_1 = [
      Paragraph(f"1. Docling Document Model {GOLD_STARS}", h3_style),
      Paragraph(
          "This should be our next Docling topic.<br/>We need to understand"
          " what this object actually represents:",
          body_style,
      ),
      create_ascii_table("doc = result.document"),
      Spacer(1, 4),
      Paragraph(
          "Instead of treating it as just another extracted-text object, we'll"
          " learn:",
          body_style,
      ),
      create_ascii_table("""DoclingDocument
│
├── Text
├── Headings
├── Paragraphs
├── Tables
├── Pictures
├── Captions
├── Lists
├── Pages
├── Groups
├── References
└── Structure"""),
      Spacer(1, 4),
      Paragraph(
          "Most importantly: <b>How does Docling represent the relationship"
          " between these elements?</b><br/>This is fundamental for advanced"
          " RAG.",
          body_style,
      ),
  ]
  story.append(KeepTogether(block_1))

  # 2. Docling Export Formats
  block_2 = [
      Paragraph("2. Docling Export Formats", h3_style),
      Paragraph(
          "We've already touched this. We should properly learn:", body_style
      ),
      create_ascii_table("""DoclingDocument
      │
      ├── Markdown
      ├── Dictionary
      ├── JSON representation
      ├── HTML
      └── other supported representations"""),
      Spacer(1, 4),
      Paragraph(
          "And understand:<br/><b>When should we use Markdown?</b><br/>For"
          " example:",
          body_style,
      ),
      create_ascii_table("""PDF
 ↓
Docling
 ↓
Markdown
 ↓
Chunking
 ↓
Embedding"""),
      Spacer(1, 4),
      Paragraph(
          "<b>When should we use structured representation?</b><br/>For"
          " example:",
          body_style,
      ),
      create_ascii_table("""PDF
 ↓
Docling
 ↓
Structured document
 ↓
Element-aware processing
 ↓
Chunking"""),
      Spacer(1, 4),
      Paragraph(
          "This distinction becomes very important in production RAG.",
          body_style,
      ),
  ]
  story.append(KeepTogether(block_2))

  # 3. Tables Deep Dive
  block_3 = [
      Paragraph(f"3. Tables — Deep Dive {GOLD_STARS}", h3_style),
      Paragraph(
          "This is a must learn for your RAG project.<br/>We shouldn't stop at:"
          ' <i>"Docling can extract tables."</i><br/>We should learn:',
          body_style,
      ),
      create_ascii_table("""PDF Table
   ↓
Docling
   ↓
Table structure
   ↓
Rows / Columns / Cells
   ↓
Structured representation"""),
      Spacer(1, 4),
      Paragraph(
          "And then ask: <b>How should tables be represented for"
          " RAG?</b><br/>For example:",
          body_style,
      ),
      create_ascii_table("""| Product | Region | Revenue |
|---------|--------|---------|
| A       | India  | 10M     |
| B       | USA    | 20M     |"""),
      Spacer(1, 4),
      Paragraph(
          "Should we embed the raw Markdown table?<br/>Or convert it"
          " into:",
          body_style,
      ),
      create_ascii_table("""Product A
Region: India
Revenue: 10M"""),
      Spacer(1, 4),
      Paragraph(
          "Or create a table-specific retrieval strategy? That becomes an"
          " advanced RAG topic.",
          body_style,
      ),
  ]
  story.append(KeepTogether(block_3))

  # 4. Pictures and Images
  block_4 = [
      Paragraph("4. Pictures and Images", h3_style),
      Paragraph(
          "Docling can identify pictures in documents. We should learn:",
          body_style,
      ),
      create_ascii_table("""PDF
 ↓
Docling
 ↓
Picture detected
 ↓
Picture metadata / location
 ↓
Image processing"""),
      Spacer(1, 4),
      Paragraph(
          "Then we can ask: <b>What do we do when a PDF contains an"
          " architecture diagram?</b><br/>This connects directly to your"
          " multimodal RAG goal.<br/>For example:",
          body_style,
      ),
      create_ascii_table("""Architecture Diagram
        ↓
Docling detects picture
        ↓
Image extraction
        ↓
Vision model
        ↓
Description
        ↓
Metadata / searchable representation"""),
  ]
  story.append(KeepTogether(block_4))

  # 5. Architecture Diagrams
  block_5 = [
      Paragraph(f"5. Architecture Diagrams and Figures {GOLD_STARS}", h3_style),
      Paragraph("This deserves its own experiment.<br/>For example:", body_style),
      create_ascii_table("""User
 ↓
API
 ↓
Event Hub
 ↓
Processing
 ↓
Data Explorer"""),
      Spacer(1, 4),
      Paragraph(
          "Docling may identify the diagram as a picture, but: <b>Identifying"
          " an image and understanding an image are two different"
          " problems.</b><br/>We should learn that distinction.",
          body_style,
      ),
      create_ascii_table("""Document understanding
        ↓
"There's a picture here."

Vision understanding
        ↓
"This picture represents an Azure Event Hub
architecture.\""""),
      Spacer(1, 4),
      Paragraph(
          "That distinction is crucial for multimodal RAG.", body_style
      ),
  ]
  story.append(KeepTogether(block_5))

  # 6. Mathematical Formulas
  block_6 = [
      Paragraph("6. Mathematical Formulas", h3_style),
      Paragraph(
          "This is another important Docling capability to"
          " investigate.<br/>For example:",
          body_style,
      ),
      create_ascii_table("E = mc²\n\nor:\n\nP(A|B) = P(B|A)P(A) / P(B)"),
      Spacer(1, 4),
      Paragraph("We should learn:", body_style),
      create_ascii_table("""PDF
 ↓
Formula
 ↓
Document parser
 ↓
Formula representation
 ↓
Markdown / LaTeX"""),
      Spacer(1, 4),
      Paragraph(
          "This is particularly useful for scientific papers, engineering"
          " documents, technical manuals, and research documents.",
          body_style,
      ),
  ]
  story.append(KeepTogether(block_6))

  # 7. Lists & Nested Structures
  block_7 = [
      Paragraph("7. Lists and Nested Structures", h3_style),
      Paragraph("Consider:", body_style),
      create_ascii_table("""1. Authentication
   1.1 OAuth
   1.2 JWT

2. Authorization
   2.1 RBAC
   2.2 ABAC"""),
      Spacer(1, 4),
      Paragraph(
          "A basic text extractor might flatten this. Docling's document"
          " structure gives us an opportunity to preserve:",
          body_style,
      ),
      create_ascii_table("""Parent
 ├── Child
 └── Child"""),
      Spacer(1, 4),
      Paragraph(
          "This matters when creating hierarchical chunks.", body_style
      ),
  ]
  story.append(KeepTogether(block_7))

  # 8. Document Hierarchy
  block_8 = [
      Paragraph(f"8. Document Hierarchy {GOLD_STARS}", h3_style),
      Paragraph(
          "This is one of the most important topics for your RAG"
          " learning.<br/>Consider:",
          body_style,
      ),
      create_ascii_table("""Chapter
│
├── Section
│   ├── Paragraph
│   ├── Paragraph
│   └── Table
│
└── Section
    ├── Paragraph
    └── Figure"""),
      Spacer(1, 4),
      Paragraph(
          "Instead of treating the PDF as <i>one giant text stream</i>, we can"
          " preserve:",
          body_style,
      ),
      create_ascii_table("""Document
   ↓
Section
   ↓
Subsection
   ↓
Content"""),
      Spacer(1, 4),
      Paragraph(
          "This leads directly to <b>Hierarchical RAG</b> and"
          " <b>Parent-child retrieval</b>.",
          body_style,
      ),
  ]
  story.append(KeepTogether(block_8))

  # 9. Page-Level Information
  block_9 = [
      Paragraph("9. Page-Level Information", h3_style),
      Paragraph(
          "We should learn how Docling associates content with"
          " pages.<br/>For example:",
          body_style,
      ),
      create_ascii_table("""Document
│
├── Page 1
│   ├── Heading
│   └── Paragraph
│
├── Page 2
│   ├── Table
│   └── Paragraph
│
└── Page 3
    └── Figure"""),
      Spacer(1, 4),
      Paragraph("Then we can attach metadata:", body_style),
      create_ascii_table("""{
    "page": 3,
    "document": "architecture.pdf",
    "element_type": "picture"
}"""),
      Spacer(1, 4),
      Paragraph(
          "This becomes extremely valuable for citations, source references,"
          " debugging, retrieval, and UI document previews.",
          body_style,
      ),
  ]
  story.append(KeepTogether(block_9))

  # 10. Bounding Boxes and Coordinates
  block_10 = [
      Paragraph("10. Bounding Boxes and Coordinates", h3_style),
      Paragraph(
          "This is a more advanced but very useful topic. A document element"
          " can have a physical location:",
          body_style,
      ),
      create_ascii_table("""┌────────────────────────────┐
│                            │
│       Heading              │
│                            │
│   ┌───────────────┐        │
│   │    TABLE      │        │
│   └───────────────┘        │
│                            │
└────────────────────────────┘"""),
      Spacer(1, 4),
      Paragraph(
          "We can potentially associate an element with: <code>x</code>,"
          " <code>y</code>, <code>width</code>, <code>height</code>,"
          " <code>page</code>.<br/>Why do we care? Because production"
          ' applications may need: <i>"Show me the exact location of the'
          ' answer in the original PDF."</i>',
          body_style,
      ),
  ]
  story.append(KeepTogether(block_10))

  # 11. Metadata Extraction
  block_11 = [
      Paragraph("11. Metadata Extraction", h3_style),
      Paragraph("We should learn how to preserve metadata such as:", body_style),
      create_ascii_table("""Document
│
├── filename
├── page
├── section
├── element type
├── heading hierarchy
├── coordinates
└── source"""),
      Spacer(1, 4),
      Paragraph(
          "Then our eventual RAG chunk could look conceptually like:",
          body_style,
      ),
      create_ascii_table("""{
    "text": "...",
    "metadata": {
        "source": "architecture.pdf",
        "page": 4,
        "section": "Event Processing",
        "element_type": "paragraph"
    }
}"""),
      Spacer(1, 4),
      Paragraph(
          "This connects Docling directly to LangChain Documents.",
          body_style,
      ),
  ]
  story.append(KeepTogether(block_11))

  # 12. Docling -> LangChain
  block_12 = [
      Paragraph("12. Docling → LangChain", h3_style),
      Paragraph(
          "This should definitely be part of our journey. Eventually:",
          body_style,
      ),
      create_ascii_table("""PDF
 ↓
Docling
 ↓
DoclingDocument
 ↓
Structured elements
 ↓
LangChain Document
 ↓
Chunking
 ↓
Embedding
 ↓
Vector DB"""),
      Spacer(1, 4),
      Paragraph(
          "This is where our Docling learning becomes directly useful to your"
          " RAG application.",
          body_style,
      ),
  ]
  story.append(KeepTogether(block_12))

  # 13. Docling + Chunking
  block_13 = [
      Paragraph(f"13. Docling + Chunking {GOLD_STARS}", h3_style),
      Paragraph(
          "This is where things become really interesting. Instead of:",
          body_style,
      ),
      create_ascii_table("""PDF
 ↓
Extract all text
 ↓
RecursiveCharacterTextSplitter"""),
      Spacer(1, 4),
      Paragraph("we can explore:", body_style),
      create_ascii_table("""PDF
 ↓
Docling
 ↓
Document structure
 ↓
Semantic elements
 ↓
Structure-aware chunking"""),
      Spacer(1, 4),
      Paragraph(
          "For example: <b>Heading + Paragraph + Paragraph + Table</b> can"
          " potentially form a much better semantic unit than <i>every 500"
          " characters</i>.",
          body_style,
      ),
  ]
  story.append(KeepTogether(block_13))

  # 14. Docling + Hybrid Documents
  block_14 = [
      Paragraph("14. Docling + Hybrid Documents", h3_style),
      Paragraph(
          "We should eventually test a single PDF containing:", body_style
      ),
      create_ascii_table("""Text
+
Table
+
Image
+
Architecture Diagram
+
Formula
+
Scanned Page"""),
      Spacer(1, 4),
      Paragraph(
          "This is actually very close to the sample PDF you asked me to"
          " create earlier. Then we can see how Docling handles each"
          " component. That would make an excellent practical exercise.",
          body_style,
      ),
  ]
  story.append(KeepTogether(block_14))

  # 15. Comparison Table
  table_data = [
      ["Capability", "PyPDFLoader", "PyMuPDF", "Docling"],
      ["Text", "[OK]", "[OK]", "[OK]"],
      ["Pages", "[OK]", "[OK]", "[OK]"],
      [
          "Reading order",
          "Limited",
          "Limited",
          '<font color="#eab308">★</font>',
      ],
      [
          "Tables",
          "Limited",
          "Limited",
          '<font color="#eab308">★ ★ ★</font>',
      ],
      [
          "Layout",
          "Limited",
          "Limited",
          '<font color="#eab308">★ ★ ★</font>',
      ],
      [
          "Images",
          "Limited",
          "[OK]",
          '<font color="#eab308">★ ★ ★</font>',
      ],
      [
          "Structure",
          "Limited",
          "Limited",
          '<font color="#eab308">★ ★ ★</font>',
      ],
      [
          "Complex PDFs",
          "Limited",
          "Good",
          '<font color="#eab308">★ ★ ★ ★ ★</font>',
      ],
      ["RAG-oriented document understanding", "Basic", "Basic", "Strong"],
  ]

  # Wrap table cells in Paragraphs so font and HTML color tags render properly
  table_cell_style = ParagraphStyle(
      name="TableCell",
      fontName=SANS_REG,
      fontSize=8.5,
      leading=11,
      textColor=colors.HexColor("#1e293b"),
  )
  table_head_style = ParagraphStyle(
      name="TableHead",
      fontName=SANS_BOLD,
      fontSize=8.5,
      leading=11,
      textColor=colors.white,
  )

  formatted_table_data = []
  for row_idx, row in enumerate(table_data):
    formatted_row = []
    for cell in row:
      if row_idx == 0:
        formatted_row.append(Paragraph(cell, table_head_style))
      else:
        formatted_row.append(Paragraph(cell, table_cell_style))
    formatted_table_data.append(formatted_row)

  comp_table = Table(formatted_table_data, colWidths=[187, 100, 100, 100])
  comp_table.setStyle(
      TableStyle([
          ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
          ("ALIGN", (0, 0), (-1, -1), "LEFT"),
          ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
          (
              "ROWBACKGROUNDS",
              (0, 1),
              (-1, -1),
              [colors.white, colors.HexColor("#f8fafc")],
          ),
          ("TOPPADDING", (0, 0), (-1, -1), 5),
          ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
      ])
  )

  block_15 = [
      Paragraph("15. Docling vs Traditional PDF Loaders", h3_style),
      Paragraph("We should also perform a proper comparison:", body_style),
      comp_table,
      Spacer(1, 4),
      Paragraph(
          "The exact capabilities depend on the document and configuration, so"
          " we'll validate them hands-on rather than treating the table as"
          " absolute.",
          body_style,
      ),
  ]
  story.append(KeepTogether(block_15))

  # 16. Configuration
  block_16 = [
      Paragraph("16. Docling Configuration", h3_style),
      Paragraph(
          "Eventually we'll learn that <code>converter ="
          " DocumentConverter()</code> is only the beginning. We'll investigate"
          " things such as:",
          body_style,
      ),
      create_ascii_table("""DocumentConverter
       │
       ├── PDF pipeline options
       ├── OCR options
       ├── table options
       ├── image options
       └── processing configuration"""),
      Spacer(1, 4),
      Paragraph(
          "This is where we start moving toward production configuration.",
          body_style,
      ),
  ]
  story.append(KeepTogether(block_16))

  # 17. Performance & Production
  block_17 = [
      Paragraph(
          "17. Docling Performance &amp; Production Considerations", h3_style
      ),
      Paragraph("Later, we should investigate:", body_style),
      create_ascii_table("""Large PDFs
Thousands of PDFs
Parallel processing
Caching
OCR cost
Processing time
Memory usage
Failure handling
Logging"""),
      Spacer(1, 4),
      Paragraph(
          "Because: <b>A library working perfectly on a 5-page PDF is not"
          " automatically a production ingestion pipeline.</b>",
          body_style,
      ),
  ]
  story.append(KeepTogether(block_17))

  # Learning Journey Restructure
  block_restructure = [
      Paragraph("How I would restructure your learning journey", h2_style),
      Paragraph(
          "I would not abandon OCR, but I would avoid spending too much time"
          " manually implementing OCR pipelines now.<br/>I'd make the next"
          " part:",
          body_style,
      ),
      create_ascii_table("""Stage 1.4.2 — OCR & Complex PDF Ingestion
│
├── 1.4.2.1 — Text vs Scanned PDF                     [OK]
├── 1.4.2.2 — Detecting Scanned Pages                [OK]
├── 1.4.2.3 — Deep PDF Page Analysis                 [OK]
├── 1.4.2.4 — OCR Fundamentals                       [OK]
│
├── 1.4.2.5 — OCR Approach
│   ├── 1.4.2.5.1 — Basic OCR                        [OK]
│   ├── 1.4.2.5.2 — Docling for Scanned PDFs         [OK]
│   └── 1.4.2.5.3 — Layout & Reading Order           [OK]
│
└── Docling Deep Dive
    │
    ├── Docling Document Model
    ├── Export & Serialization
    ├── Tables
    ├── Pictures & Figures
    ├── Mathematical Formulas
    ├── Lists & Hierarchy
    ├── Page & Element Metadata
    ├── Bounding Boxes
    ├── Document Structure
    ├── Structure-aware Chunking
    ├── Docling → LangChain Documents
    ├── Multimodal / Vision Integration
    ├── Complex Mixed PDFs
    ├── Docling vs PDF Loaders
    └── Production Configuration & Performance"""),
  ]
  story.append(KeepTogether(block_restructure))

  # Recommendation
  block_rec = [
      Paragraph("My recommendation for our very next lesson", h2_style),
      Paragraph(
          "Don't jump to OCR preprocessing yet.<br/>I'd make our next"
          " lesson:",
          body_style,
      ),
      create_ascii_table("Stage 1.4.2.5.4 — Docling Document Model"),
      Spacer(1, 4),
      Paragraph(
          "Because we've already successfully created:",
          body_style,
      ),
      create_ascii_table("doc = result.document"),
      Spacer(1, 4),
      Paragraph(
          "but we haven't really understood what <code>DoclingDocument</code>"
          " contains and how its elements are represented.<br/>Once you"
          " understand that, everything else—tables, figures, hierarchy,"
          " metadata, bounding boxes, structure-aware chunking, and Docling →"
          " LangChain—will make much more sense.<br/>That would be a much"
          " stronger progression for your RAG learning journey.",
          body_style,
      ),
  ]
  story.append(KeepTogether(block_rec))

  doc.build(story, canvasmaker=NumberedCanvas)
  print(f"Successfully generated: {Path(filename).resolve()}")


if __name__ == "__main__":
  build_pdf("docling_learning_track.pdf")