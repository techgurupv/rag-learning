import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Preformatted, Table, TableStyle
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ---------------------------------------------------------
# Unicode Font Registration (Ensures exact symbols render)
# ---------------------------------------------------------
def setup_unicode_fonts():
    font_candidates = [
        # Linux / Colab / Debian paths
        ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"),
        ("/usr/share/fonts/truetype/freefont/FreeSans.ttf", "/usr/share/fonts/truetype/freefont/FreeMono.ttf"),
        # macOS paths
        ("/System/Library/Fonts/Supplemental/Arial Unicode.ttf", "/System/Library/Fonts/Courier.dfont"),
        ("/Library/Fonts/Arial Unicode.ttf", "/System/Library/Fonts/Menlo.ttc"),
        # Windows paths
        ("C:\\Windows\\Fonts\\arialuni.ttf", "C:\\Windows\\Fonts\\consola.ttf"),
        ("C:\\Windows\\Fonts\\seguisym.ttf", "C:\\Windows\\Fonts\\lucon.ttf"),
    ]
    
    regular_registered = False
    mono_registered = False
    
    for reg_path, mono_path in font_candidates:
        if os.path.exists(reg_path) and not regular_registered:
            try:
                pdfmetrics.registerFont(TTFont('UnicodeSans', reg_path))
                regular_registered = True
            except Exception:
                pass
        if os.path.exists(mono_path) and not mono_registered:
            try:
                pdfmetrics.registerFont(TTFont('UnicodeMono', mono_path))
                mono_registered = True
            except Exception:
                pass

    sans_font = 'UnicodeSans' if regular_registered else 'Helvetica'
    mono_font = 'UnicodeMono' if mono_registered else 'Courier'
    return sans_font, mono_font

SANS_FONT, MONO_FONT = setup_unicode_fonts()


class NumberedCanvas(canvas.Canvas):
    """Canvas that computes total pages dynamically with clean headers and footers."""
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
        self.setFont(SANS_FONT, 8)
        self.setFillColor(colors.HexColor("#64748B"))

        # Highlighted PDF Running Header
        self.drawString(54, 11 * 72 - 36, "■ EXPERIMENT ANALYSIS: DOCLING STAGE 1.4.2.5.4")
        self.drawRightString(8.5 * 72 - 54, 11 * 72 - 36, "TECHNICAL VERIFICATION REPORT")
        self.setStrokeColor(colors.HexColor("#38BDF8"))  # Light blue accent header rule
        self.setLineWidth(1)
        self.line(54, 11 * 72 - 42, 8.5 * 72 - 54, 11 * 72 - 42)

        # Running Footer
        self.drawString(54, 36, "Confidential — Architecture Understanding & Verification")
        self.drawRightString(8.5 * 72 - 54, 36, f"Page {self._pageNumber} of {page_count}")
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.75)
        self.line(54, 46, 8.5 * 72 - 54, 46)
        self.restoreState()


def create_highlighted_box(
    text, 
    bg_color="#E0F2FE", 
    text_color="#0369A1", 
    border_color="#7DD3FC", 
    font_size=10.5
):
    style = ParagraphStyle(
        name=f"BoxText_{bg_color}_{text_color}_{font_size}",
        fontName=SANS_FONT,
        fontSize=font_size,
        textColor=colors.HexColor(text_color),
        leading=font_size + 4,
    )
    p = Paragraph(text, style)
    t = Table([[p]], colWidths=[504])
    
    t_style = [
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor(bg_color)),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]
    if border_color:
        t_style.append(('BOX', (0, 0), (-1, -1), 1, colors.HexColor(border_color)))
        
    t.setStyle(TableStyle(t_style))
    return t


def generate_experiment_pdf(output_filename="Docling_Stage_1_4_2_5_4_Analysis.pdf"):
    doc = SimpleDocTemplate(
        output_filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    body_style = ParagraphStyle(
        'ExactBody',
        parent=styles['Normal'],
        fontName=SANS_FONT,
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor("#1E293B"),
        spaceAfter=4
    )

    code_style = ParagraphStyle(
        'ExactCode',
        fontName=MONO_FONT,
        fontSize=8,
        leading=11.5,
        textColor=colors.HexColor("#0F172A"),
    )

    # Palette
    LIGHT_BLUE_BG = "#E0F2FE"       # Light Sky Blue
    LIGHT_BLUE_TXT = "#0369A1"      # Deep Cyan / Navy Blue
    LIGHT_BLUE_BORDER = "#7DD3FC"   # Border Accent

    # Exact content structure with full ASCII and symbols intact
    content_blocks = [
        ("TITLE", "■ EXPERIMENT REPORT: STAGE 1.4.2.5.4", "#0F172A", "#FFFFFF", None, 12),
        ("TEXT", "Yes — and this output is very significant for our Stage 1.4.2.5.4 experiment.<br/>You got:"),
        ("CODE", """========== ARCHITECTURE TEXT TEST ==========

Producer             -> FOUND
Event Hubs           -> FOUND
Stream Consumer      -> FOUND
Data Explorer        -> FOUND
But we need to be careful about what this proves."""),
        
        ("STEP", "■ Step 1 — What the code was testing"),
        ("TEXT", "The code was essentially:"),
        ("CODE", """markdown_text = doc.export_to_markdown()

architecture_words = [
    "Producer",
    "Event Hubs",
    "Stream Consumer",
    "Data Explorer",
]

for word in architecture_words:
    found = word.lower() in markdown_text.lower()

    print(
        f"{word:20} -> "
        f"{'FOUND' if found else 'NOT FOUND'}"
    )"""),
        ("TEXT", "The test asks:<br/><br/><i>\"Do these words occur somewhere in the Markdown exported from the DoclingDocument?\"</i><br/><br/>Your answer is:<br/>Yes, all four occur somewhere in the exported Markdown.<br/>But this does not yet prove that Docling extracted them from the architecture image."),
        
        ("STEP", "■ Step 2 — Why?"),
        ("TEXT", "Look at our sample PDF.<br/>It contains normal text such as:<br/><br/><i>An enterprise application publishes events to Azure Event Hubs.</i><br/><br/>It also contains the architecture diagram.<br/>Therefore:<br/><br/><b>\"Event Hubs\"</b><br/>could appear in the Markdown because it was extracted from the normal PDF text, not because Docling read it from the diagram.<br/><br/>This is the crucial distinction."),
        
        ("STEP", "■ Step 3 — Let's prove where the text came from"),
        ("TEXT", "We need to perform a much more precise experiment.<br/>Run this:"),
        ("CODE", """architecture_words = [
    "Producer",
    "Event Hubs",
    "Stream Consumer",
    "Data Explorer",
]

print("========== DOCLING DOCUMENT ITEMS ==========")

for item, level in doc.iterate_items():

    text = getattr(item, "text", "")

    if text:

        for word in architecture_words:

            if word.lower() in text.lower():

                print(
                    f"\\nFOUND: {word}"
                )

                print(
                    "Item type:",
                    type(item).__name__
                )

                print(
                    "Text:",
                    repr(text)
                )"""),
        ("TEXT", "This will tell us which Docling item contains those words."),
        
        ("STEP", "■ Step 4 — What I expect"),
        ("TEXT", "Suppose we get:"),
        ("CODE", """FOUND: Event Hubs
Item type: TextItem
Text: 'An enterprise application publishes events to Azure Event Hubs.'"""),
        ("TEXT", "That tells us:"),
        ("CODE", """Event Hubs
    ↓
Normal PDF text
    ↓
TextItem"""),
        ("TEXT", "It does not prove:"),
        ("CODE", """Architecture image
    ↓
OCR/VLM
    ↓
Event Hubs"""),
        ("TEXT", "Likewise, if Producer occurs in ordinary text elsewhere, that could explain its presence."),
        
        ("STEP", "■ Step 5 — Our test PDF has an important complication"),
        ("TEXT", "This is something I want to make explicit because it affects the validity of our experiment.<br/>Our PDF was designed to contain:"),
        ("CODE", """normal text
table
architecture diagram
formula image"""),
        ("TEXT", "Some words appearing in the architecture diagram also appear in the surrounding normal text.<br/>Therefore, this test:"),
        ("CODE", "word in markdown_text"),
        ("TEXT", "is not sufficient to establish image understanding.<br/><br/>This is a classic experimental-design problem:<br/><br/><b>The test data contains the same vocabulary in multiple places.</b><br/><br/>So we need to remove that ambiguity."),
        
        ("STEP", "■ Step 6 — The strongest test"),
        ("TEXT", "Let's inspect the actual PictureItem.<br/>Run:"),
        ("CODE", """for i, picture in enumerate(doc.pictures, start=1):

    print("\\n" + "=" * 70)
    print(f"PICTURE {i}")
    print("=" * 70)

    print(picture.model_dump())"""),
        ("TEXT", "We're particularly interested in whether the picture contains an annotation/description."),
        
        ("STEP", "■ Step 7 — Search specifically for the picture description"),
        ("TEXT", "Run:"),
        ("CODE", """for i, picture in enumerate(doc.pictures, start=1):

    print(f"\\n========== PICTURE {i} ==========")

    annotations = getattr(
        picture,
        "annotations",
        None
    )

    print("Annotations:")
    print(annotations)"""),
        ("TEXT", "If Level 3 picture understanding has happened, we should see something representing a generated description.<br/>Conceptually:"),
        ("CODE", """PictureItem
│
├── image
│
├── provenance
│
└── annotations
       │
       └── generated description"""),
        
        ("STEP", "■ Step 8 — There's an even better experiment"),
        ("TEXT", "We can make our test unambiguous.<br/>Create an architecture diagram containing unique text such as:"),
        ("CODE", """┌──────────────────────────────────┐
│       Enterprise Flow            │
│                                  │
│  ZetaProducer                    │
│       ↓                          │
│  QEventBridge                    │
│       ↓                          │
│  RStreamProcessor                │
│       ↓                          │
│  KAnalyticsStore                 │
└──────────────────────────────────┘"""),
        ("TEXT", "Those names should exist only inside the image.<br/>Then test:"),
        ("CODE", """unique_words = [
    "ZetaProducer",
    "QEventBridge",
    "RStreamProcessor",
    "KAnalyticsStore",
]"""),
        ("TEXT", "Now:"),
        ("CODE", """markdown_text = doc.export_to_markdown()

for word in unique_words:

    print(
        f"{word:20} -> "
        f"{'FOUND' if word.lower() in markdown_text.lower() else 'NOT FOUND'}"
    )"""),
        ("TEXT", "This eliminates the ambiguity."),
        
        ("STEP", "■ Step 9 — Why this matters"),
        ("TEXT", "Imagine the result is:"),
        ("CODE", """ZetaProducer        -> FOUND
QEventBridge        -> FOUND
RStreamProcessor    -> FOUND
KAnalyticsStore     -> FOUND"""),
        ("TEXT", "Now we have much stronger evidence that some image-processing mechanism has extracted the information.<br/>But if we get:"),
        ("CODE", """ZetaProducer        -> NOT FOUND
QEventBridge        -> NOT FOUND
RStreamProcessor    -> NOT FOUND
KAnalyticsStore     -> NOT FOUND"""),
        ("TEXT", "while:"),
        ("CODE", "len(doc.pictures)"),
        ("TEXT", "is still:"),
        ("CODE", "1"),
        ("TEXT", "then we have demonstrated:"),
        ("CODE", """Picture detection       ✅
Picture extraction      ✅
Text extraction         ❌"""),
        ("TEXT", "And if the picture annotation contains a meaningful description, then:"),
        ("CODE", """Picture detection       ✅
Picture extraction      ✅
Semantic understanding  ✅
Exact OCR               possibly ❌"""),
        ("TEXT", "That's a very valuable result."),
        
        ("STEP", "■ Step 10 — So what does YOUR current result mean?"),
        ("TEXT", "Your current result:"),
        ("CODE", """Producer             -> FOUND
Event Hubs           -> FOUND
Stream Consumer      -> FOUND
Data Explorer        -> FOUND"""),
        ("TEXT", "means only:<br/><br/><b>All four strings exist somewhere in Docling's Markdown output.</b><br/><br/>It does not yet prove:<br/><br/><i>\"Docling read those four strings from the architecture diagram.\"</i><br/><br/>Therefore, don't mark Level 3 as completed yet.<br/>We're actually doing the right thing by questioning the result."),
        
        ("STATUS", "■ Current status", "#ECFDF5", "#065F46", "#A7F3D0", 10.5),
        ("TEXT", "<b>Stage 1.4.2.5.4</b><br/>Docling Table / Image / Formula Understanding<br/><br/><b>Level 1 — Picture Detection</b><br/>✅ Demonstrated<br/><br/><b>Level 2 — Picture Extraction</b><br/>✅ Demonstrated<br/><br/><b>Level 3 — Image Content Understanding & Semantic Extraction</b><br/>🔵 Investigating"),
        
        ("NEXT", "■ Next experiment", "#F1F5F9", "#334155", "#CBD5E1", 10.5),
        ("TEXT", "First run the <code>doc.iterate_items()</code> diagnostic above.<br/>Paste its output here. From that output, we'll determine whether those FOUND values came from normal TextItems or from the picture-understanding enrichment. That will give us a scientifically valid answer rather than assuming that FOUND means OCR/VLM succeeded.")
    ]

    story = []

    for item in content_blocks:
        block_type = item[0]
        
        if block_type == "TITLE":
            _, text, bg, txt, border, size = item
            story.append(Spacer(1, 10))
            story.append(create_highlighted_box(text, bg_color=bg, text_color=txt, border_color=border, font_size=size))
            story.append(Spacer(1, 6))
            
        elif block_type == "STEP":
            _, text = item
            story.append(Spacer(1, 10))
            story.append(create_highlighted_box(
                text, 
                bg_color=LIGHT_BLUE_BG, 
                text_color=LIGHT_BLUE_TXT, 
                border_color=LIGHT_BLUE_BORDER, 
                font_size=10.5
            ))
            story.append(Spacer(1, 6))
            
        elif block_type in ("STATUS", "NEXT"):
            _, text, bg, txt, border, size = item
            story.append(Spacer(1, 10))
            story.append(create_highlighted_box(text, bg_color=bg, text_color=txt, border_color=border, font_size=size))
            story.append(Spacer(1, 6))
            
        elif block_type == "TEXT":
            story.append(Paragraph(item[1], body_style))
            story.append(Spacer(1, 4))
            
        elif block_type == "CODE":
            pre = Preformatted(item[1], code_style)
            t = Table([[pre]], colWidths=[504])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
                ('BOX', (0, 0), (-1, -1), 0.75, colors.HexColor("#CBD5E1")),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ]))
            story.append(Spacer(1, 3))
            story.append(t)
            story.append(Spacer(1, 6))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Generated successfully: {output_filename}")

if __name__ == "__main__":
    generate_experiment_pdf()