import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    HRFlowable,
    KeepTogether,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


def register_system_fonts():
    """Register Windows native fonts with full Unicode and box-drawing glyph support."""
    win_fonts = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts")

    # Primary Monospace font for diagrams
    consolas_path = os.path.join(win_fonts, "consola.ttf")
    segoe_path = os.path.join(win_fonts, "seguisym.ttf")
    arial_path = os.path.join(win_fonts, "arial.ttf")
    arialbd_path = os.path.join(win_fonts, "arialbd.ttf")

    if os.path.exists(consolas_path):
        pdfmetrics.registerFont(TTFont("ConsolasUnicode", consolas_path))
        mono_font = "ConsolasUnicode"
    elif os.path.exists(segoe_path):
        pdfmetrics.registerFont(TTFont("SegoeSymbol", segoe_path))
        mono_font = "SegoeSymbol"
    else:
        mono_font = "Courier"

    if os.path.exists(arial_path) and os.path.exists(arialbd_path):
        pdfmetrics.registerFont(TTFont("ArialUnicode", arial_path))
        pdfmetrics.registerFont(TTFont("ArialUnicode-Bold", arialbd_path))
        body_font = "ArialUnicode"
        bold_font = "ArialUnicode-Bold"
    else:
        body_font = "Helvetica"
        bold_font = "Helvetica-Bold"

    return mono_font, body_font, bold_font


class NumberedCanvas(canvas.Canvas):
    """Generates clean running header and page numbering."""

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

        # Header rule
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.75)
        self.line(40, 755, 572, 755)
        self.drawString(
            40,
            762,
            "DOCLING ARCHITECTURE & LEARNING PATH // STAGE 1.4.2.5.4 ROADMAP",
        )

        # Footer rule
        self.line(40, 45, 572, 45)
        self.drawString(40, 32, "Technical Specification & Progress Tracker")
        self.drawRightString(
            572, 32, f"Page {self._pageNumber} of {page_count}"
        )
        self.restoreState()


def make_diagram_box(ascii_text, mono_font, width=532):
    """Renders dark-themed diagram containers identical to modern terminal/code blocks."""
    code_style = ParagraphStyle(
        name="DiagramStyle",
        fontName=mono_font,
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor("#F8FAFC"),
    )
    pre = Preformatted(ascii_text.strip("\n"), code_style)
    t = Table([[pre]], colWidths=[width])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#0F172A")),
                ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#1E293B")),
                ("LEFTPADDING", (0, 0), (-1, -1), 14),
                ("RIGHTPADDING", (0, 0), (-1, -1), 14),
                ("TOPPADDING", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ]
        )
    )
    return t


def generate_pdf(output_path="Docling_Learning_Path_Presentation.pdf"):
    mono_font, body_font, bold_font = register_system_fonts()

    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=40,
        rightMargin=40,
        topMargin=55,
        bottomMargin=55,
    )

    styles = getSampleStyleSheet()

    styles.add(
        ParagraphStyle(
            "DocTitle",
            fontName=bold_font,
            fontSize=16,
            leading=20,
            textColor=colors.HexColor("#0F172A"),
            spaceAfter=4,
        )
    )
    styles.add(
        ParagraphStyle(
            "SectionHeader",
            fontName=bold_font,
            fontSize=11.5,
            leading=15,
            textColor=colors.HexColor("#0F172A"),
            spaceBefore=8,
            spaceAfter=4,
        )
    )
    styles.add(
        ParagraphStyle(
            "LevelHeader",
            fontName=bold_font,
            fontSize=10.5,
            leading=14,
            textColor=colors.HexColor("#2563EB"),
            spaceBefore=6,
            spaceAfter=3,
        )
    )
    styles.add(
        ParagraphStyle(
            "BodyDark",
            fontName=body_font,
            fontSize=9.5,
            leading=13.5,
            textColor=colors.HexColor("#334155"),
            spaceAfter=4,
        )
    )
    styles.add(
        ParagraphStyle(
            "FormulaItem",
            fontName=body_font,
            fontSize=9.5,
            leading=13.5,
            textColor=colors.HexColor("#334155"),
            leftIndent=12,
            spaceAfter=2,
        )
    )

    story = []

    # Title
    story.append(
        Paragraph(
            "Stage 1.4.2.5.4 — Docling Table / Image / Formula Understanding",
            styles["DocTitle"],
        )
    )
    story.append(
        HRFlowable(
            width="100%",
            thickness=1.5,
            color=colors.HexColor("#2563EB"),
            spaceBefore=3,
            spaceAfter=8,
        )
    )

    # Lead text
    story.append(
        Paragraph(
            "After Level 3 — Image Content Understanding & Semantic Extraction, "
            "I recommend that we finish Stage 1.4.2.5.4 by covering tables and formulas systematically, "
            "rather than moving immediately to 1.4.2.5.5.",
            styles["BodyDark"],
        )
    )
    story.append(Spacer(1, 4))
    story.append(
        Paragraph("Our learning path can now be:", styles["SectionHeader"])
    )

    # Master Diagram
    path_ascii = (
        "Stage 1.4.2.5.4\n"
        "Docling Table / Image / Formula Understanding\n"
        "│\n"
        "├── Level 1\n"
        "│   Picture Detection\n"
        "│   [x] Completed\n"
        "│\n"
        "├── Level 2\n"
        "│   Picture Extraction\n"
        "│   [x] Completed\n"
        "│\n"
        "├── Level 3\n"
        "│   Image Content Understanding & Semantic Extraction\n"
        "│   [*] Current / completing validation\n"
        "│\n"
        "├── Level 4\n"
        "│   Table Understanding & Structured Extraction\n"
        "│   [>] Next\n"
        "│\n"
        "├── Level 5\n"
        "│   Formula Understanding & Extraction\n"
        "│   [>]\n"
        "│\n"
        "└── Level 6\n"
        "    Unified Complex-Content Representation\n"
        "    [>]"
    )
    story.append(make_diagram_box(path_ascii, mono_font))
    story.append(Spacer(1, 8))

    # Details
    story.append(
        Paragraph(
            "What each remaining level teaches", styles["SectionHeader"]
        )
    )

    # Level 4
    story.append(
        Paragraph(
            "Level 4 — Table Understanding & Structured Extraction",
            styles["LevelHeader"],
        )
    )
    story.append(
        Paragraph(
            "We will test whether Docling can preserve:", styles["BodyDark"]
        )
    )

    table_ascii = (
        "PDF Table\n"
        "   ↓\n"
        "Docling TableItem\n"
        "   ↓\n"
        "Rows / columns / cells\n"
        "   ↓\n"
        "Structured representation\n"
        "   ↓\n"
        "Markdown / HTML / DataFrame-style representation"
    )
    story.append(make_diagram_box(table_ascii, mono_font))
    story.append(Spacer(1, 3))
    story.append(
        Paragraph(
            "We'll also deliberately test the issue we encountered earlier: "
            "table vs. visual layout, including a table positioned beside another content region.",
            styles["BodyDark"],
        )
    )
    story.append(Spacer(1, 4))

    # Level 5
    story.append(
        Paragraph(
            "Level 5 — Formula Understanding & Extraction",
            styles["LevelHeader"],
        )
    )
    story.append(
        Paragraph(
            "Our sample PDF already contains a mathematical formula.",
            styles["BodyDark"],
        )
    )
    story.append(Paragraph("We'll investigate:", styles["BodyDark"]))

    formula_ascii = (
        "Formula image / PDF formula\n"
        "          ↓\n"
        "       Docling\n"
        "          ↓\n"
        "Formula detected?\n"
        "          ↓\n"
        "LaTeX / semantic representation?"
    )
    story.append(make_diagram_box(formula_ascii, mono_font))
    story.append(Spacer(1, 3))
    story.append(Paragraph("We'll distinguish:", styles["BodyDark"]))
    story.append(Paragraph("Formula as an image", styles["FormulaItem"]))
    story.append(Paragraph("        ≠", styles["FormulaItem"]))
    story.append(
        Paragraph(
            "Formula recognized as a mathematical expression",
            styles["FormulaItem"],
        )
    )
    story.append(Spacer(1, 4))

    # Level 6
    story.append(
        Paragraph(
            "Level 6 — Unified Complex-Content Representation",
            styles["LevelHeader"],
        )
    )
    story.append(
        Paragraph(
            "This is the important final exercise before moving to LangChain. We'll take our complete PDF:",
            styles["BodyDark"],
        )
    )

    complex_ascii = (
        "                  Complex PDF\n"
        "                      │\n"
        "        ┌─────────────┼──────────────┐\n"
        "        ↓             ↓              ↓\n"
        "       Text          Table          Image\n"
        "                                      │\n"
        "                                      ↓\n"
        "                                    VLM/OCR\n"
        "        │             │              │\n"
        "        └─────────────┼──────────────┘\n"
        "                      ↓\n"
        "              DoclingDocument\n"
        "                      │\n"
        "          ┌───────────┼───────────┐\n"
        "          ↓           ↓           ↓\n"
        "        Text        Table       Picture\n"
        "          │           │           │\n"
        "          └───────────┼───────────┘\n"
        "                      ↓\n"
        "              Unified representation"
    )
    story.append(make_diagram_box(complex_ascii, mono_font))
    story.append(Spacer(1, 3))
    story.append(
        Paragraph(
            "Then we'll ask the most important RAG question:",
            styles["BodyDark"],
        )
    )
    story.append(
        Paragraph(
            "<i>Can we represent all these different content types in a form that a downstream RAG pipeline can actually consume?</i>",
            styles["BodyDark"],
        )
    )
    story.append(Spacer(1, 4))

    # Completion Transition
    story.append(
        Paragraph("Then Stage 1.4.2.5.4 is complete", styles["SectionHeader"])
    )
    story.append(Paragraph("At that point:", styles["BodyDark"]))

    stage_transition_ascii = (
        "Stage 1.4.2.5.4\n"
        "Docling Table / Image / Formula Understanding\n"
        "                     │\n"
        "                     ▼\n"
        "                  COMPLETE\n"
        "                     │\n"
        "                     ▼\n"
        "Stage 1.4.2.5.5\n"
        "Docling → LangChain → RAG"
    )
    story.append(make_diagram_box(stage_transition_ascii, mono_font))
    story.append(Spacer(1, 4))

    story.append(
        Paragraph(
            "And 1.4.2.5.5 will be where everything starts coming together:",
            styles["BodyDark"],
        )
    )

    rag_ascii = (
        "PDF\n"
        " ↓\n"
        "Docling\n"
        " ↓\n"
        "DoclingDocument\n"
        " ↓\n"
        "LangChain Documents\n"
        " ↓\n"
        "Metadata\n"
        " ↓\n"
        "Chunking\n"
        " ↓\n"
        "Embeddings\n"
        " ↓\n"
        "Vector Store\n"
        " ↓\n"
        "Retrieval\n"
        " ↓\n"
        "RAG"
    )
    story.append(make_diagram_box(rag_ascii, mono_font))
    story.append(Spacer(1, 6))

    # Next Steps Block
    next_steps_elements = [
        Paragraph("So, immediately next", styles["SectionHeader"]),
        Paragraph(
            "We should finish Level 3 validation first, because our FOUND result has not yet proven that the words came from the architecture image.",
            styles["BodyDark"],
        ),
        Paragraph("Then:", styles["BodyDark"]),
        Paragraph(
            "<b>Level 4 — Table Understanding & Structured Extraction</b>",
            styles["BodyDark"],
        ),
        Paragraph("That gives us a clean progression:", styles["BodyDark"]),
        Paragraph(
            "<b>Image → Understand → Table → Formula → Unified representation → LangChain → RAG.</b>",
            ParagraphStyle(
                "Highlight",
                parent=styles["BodyDark"],
                textColor=colors.HexColor("#1D4ED8"),
                fontName=bold_font,
            ),
        ),
    ]

    next_steps_table = Table(
        [[next_steps_elements]], colWidths=[532]
    )
    next_steps_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#EFF6FF")),
                ("BOX", (0, 0), (-1, -1), 1.5, colors.HexColor("#3B82F6")),
                ("LEFTPADDING", (0, 0), (-1, -1), 14),
                ("RIGHTPADDING", (0, 0), (-1, -1), 14),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ]
        )
    )

    story.append(KeepTogether(next_steps_table))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Presentation PDF successfully built at: {output_path}")


if __name__ == "__main__":
    generate_pdf()