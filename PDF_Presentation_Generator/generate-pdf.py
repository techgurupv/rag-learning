import html
import re
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    HRFlowable,
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


class NumberedCanvas(canvas.Canvas):
    """Dynamic header and footer with total page calculation."""

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

        # Running Header
        self.drawString(
            54,
            750,
            "Stage 1.4.2.5.4 — Docling Table / Image / Formula Understanding",
        )

        # Running Footer (Page X of Y)
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(612 - 54, 36, page_text)
        self.restoreState()


RAW_TEXT = """Stage 1.4.2.5.4 — Docling Table / Image / Formula Understanding
The objective is to answer:

When Docling receives a complex PDF, how does it recognize and represent tables, images/figures, and formulas?
Our flow will be:

                     PDF
                      │
          ┌───────────┼───────────┐
          ↓           ↓           ↓
        Table       Image       Formula
          │           │           │
          ↓           ↓           ↓
       Docling     Docling      Docling
          │           │           │
          └───────────┼───────────┘
                      ↓
               DoclingDocument
                      ↓
        Structured representation
I've also created a dedicated test PDF for this stage.
Download the Stage 1.4.2.5.4 sample PDF
It contains:

a structured table
an architecture diagram as an embedded image
a mathematical formula
captions and explanatory text
Step 1 — Verify your Docling version
You already told me you're using Docling 2.120.3, but let's verify directly in the notebook.

import docling

print("Docling version:", docling.__version__)
Expected:

Docling version: 2.120.3
Step 2 — Define the sample PDF
Use the PDF we just generated.

from pathlib import Path

pdf_path = Path(
    "stage_1_4_2_5_4/docling_table_image_formula_sample.pdf"
)

print(pdf_path)
print(pdf_path.exists())
You should get:

stage_1_4_2_5_4/docling_table_image_formula_sample.pdf
True
If you place the PDF somewhere else in your RAG project's data/raw/pdf/ directory, simply change the path.
Step 3 — Import Docling
from docling.document_converter import DocumentConverter
Create the converter:

converter = DocumentConverter()
Step 4 — Convert the PDF
result = converter.convert(pdf_path)

doc = result.document
Now we have:

PDF
 ↓
DocumentConverter
 ↓
ConversionResult
 ↓
DoclingDocument
Remember this distinction:

result
is the conversion result.

result.document
is the actual:

DoclingDocument
Step 5 — First inspect the Markdown
We deliberately do this, but we will not rely on it as our only inspection method.

markdown_text = doc.export_to_markdown()

print(markdown_text)
You should see the ordinary text and table represented in Markdown.
For example, the table should look approximately like:

| Stage | Component | Purpose |
|---|---|---|
| 1 | Event Producer | Publishes business events |
| 2 | Azure Event Hubs | Ingests and partitions event streams |
...
The picture may appear as a placeholder depending on the export settings.
Docling's export_to_markdown() supports image modes such as placeholder, embedded, and referenced images. (Docling Project)
Step 6 — Inspect the tables directly ⭐
This is where our learning becomes more interesting.
Run:

print("Number of tables:", len(doc.tables))
Then:

for i, table in enumerate(doc.tables):
    print(f"\\n===== TABLE {i + 1} =====")
    print(table.export_to_markdown(doc))
We are no longer asking:

"What did Markdown export give me?"
We're asking:

"What table objects did Docling actually create?"
Docling exposes table items and supports exporting an individual table to Markdown, HTML, and other structured representations. (Docling Project)
Step 7 — Export the table as a DataFrame
This is extremely useful for RAG later.

for i, table in enumerate(doc.tables):
    print(f"\\n===== TABLE {i + 1} =====")

    df = table.export_to_dataframe(doc)

    display(df)
Conceptually:

PDF Table
   ↓
Docling TableItem
   ↓
DataFrame
You should get something similar to:
StageComponentPurpose1Event ProducerPublishes business events2Azure Event HubsIngests and partitions event streams3Stream ConsumerReads and transforms events4Azure Data ExplorerStores data for analytics
This is much more powerful than simply extracting text.
Step 8 — Understand the table structure
Now inspect the first table:

table = doc.tables[0]

print(type(table))
Then:

print(table)
And inspect its available methods:

[m for m in dir(table) if not m.startswith("_")]
Pay particular attention to methods related to:

export
cells
captions
image
provenance
The important concept is:

TableItem
│
├── rows
├── columns
├── cells
├── caption
├── provenance
└── structure
This is why table-aware ingestion is different from ordinary text extraction.
Step 9 — Now investigate images / pictures
Run:

print("Number of pictures:", len(doc.pictures))
Then:

for i, picture in enumerate(doc.pictures):
    print(f"\\n===== PICTURE {i + 1} =====")
    print(type(picture))
    print(picture)
This tells us whether Docling detected our architecture diagram as a PictureItem.
Docling provides PictureItem support and can retrieve the corresponding image from the DoclingDocument. (Docling Project)
Step 10 — Extract the detected image
If we have at least one picture:

if len(doc.pictures) > 0:

    picture = doc.pictures[0]

    picture_image = picture.get_image(doc)

    print(type(picture_image))
If the image is available, save it:

if picture_image is not None:

    picture_image.save(
        "docling_extracted_picture.png"
    )

    print("Picture saved.")
Now you've demonstrated:

PDF
 ↓
Embedded architecture diagram
 ↓
Docling
 ↓
PictureItem
 ↓
PIL Image
 ↓
PNG
This is very different from OCR.
Step 11 — Important distinction: Image Detection vs Image Understanding
This is one of the most important concepts in this stage.
Suppose Docling tells us:

PictureItem
That means:

Docling identified a picture/figure region.
It does not necessarily mean:

"Docling understands that this is an Azure Event Hubs → Stream Consumer → Data Explorer architecture."
Those are two different levels:

Level 1
Image detection
        ↓
"There is a picture here."
versus:

Level 2
Image understanding
        ↓
"This is an event-processing architecture."
For the second task, vision-language capabilities can be involved. Docling supports picture classification and picture-description options in its pipeline configuration. (Docling Project)
That distinction will become extremely important when we reach your multimodal RAG stage.
Step 12 — Investigate the formula
Our sample PDF contains:

P(A|B) = P(B|A)P(A) / P(B)
The formula is deliberately included as an image for this first experiment.
Let's inspect the document's text items.

for item, level in doc.iterate_items():

    print(
        type(item).__name__,
        getattr(item, "label", None),
        getattr(item, "text", "")
    )
Look for anything whose label indicates:

FORMULA
The exact result is something we want to observe, not assume.
Step 13 — Understand formula enrichment
This is where Docling becomes more interesting.
Docling's PDF pipeline has a do_formula_enrichment option for mathematical formula recognition and conversion to LaTeX. (Docling Project)
Conceptually:

PDF
 ↓
Formula region
 ↓
Formula recognition
 ↓
LaTeX
For example, ideally:

P(A|B) = P(B|A)P(A) / P(B)
could become something similar to:

P(A\mid B)=\frac{P(B\mid A)P(A)}{P(B)}
However, we should not turn this option on blindly in your Docling 2.120.3 environment.
Your installed version is important, and formula enrichment can require additional model dependencies/resources. The current Docling documentation confirms that formula enrichment is a specialized processing option and that enabling multiple enrichment features increases processing time. (Docling Project)
So our first experiment is intentionally:

Detect and inspect first → enable specialized enrichment only after we understand the baseline.
Step 14 — Inspect all document elements together
Now let's create one useful diagnostic cell:

for item, level in doc.iterate_items():

    label = getattr(item, "label", None)

    text = getattr(item, "text", "")

    print(
        f"Type={type(item).__name__:<20} "
        f"Label={str(label):<20} "
        f"Text={text[:100]!r}"
    )
This is one of the most important cells in this stage.
We are beginning to see:

DoclingDocument
│
├── TextItem
├── SectionHeaderItem
├── TableItem
├── PictureItem
├── ...
└── Formula-related element, if detected
Now we're actually learning the Docling document model, rather than treating Docling as a black-box PDF-to-Markdown converter.
Step 15 — Export the complete structured document
Since you previously encountered:

AttributeError:
DoclingDocument has no attribute export_to_json
we must remember the correct API for your Docling v2 workflow:

document_dict = doc.export_to_dict()
Docling v2 moved document export operations onto DoclingDocument; the official v2 documentation explicitly shows export_to_dict(), export_to_markdown(), and export_to_document_tokens(). (GitHub)
You can inspect:

document_dict.keys()
and save it:

import json

output_json = Path(
    "docling_table_image_formula.json"
)

output_json.write_text(
    json.dumps(
        document_dict,
        indent=2,
        ensure_ascii=False,
    ),
    encoding="utf-8",
)

print(output_json)
This JSON becomes very useful for debugging.
Step 16 — Our first Table / Image / Formula summary
After running the notebook, create this summary:

print("========== DOCLING CONTENT SUMMARY ==========")

print("Tables   :", len(doc.tables))
print("Pictures :", len(doc.pictures))

formula_items = []

for item, level in doc.iterate_items():

    label = str(getattr(item, "label", ""))

    if "formula" in label.lower():
        formula_items.append(item)

print("Formulas :", len(formula_items))
Ideally we'll get something like:

========== DOCLING CONTENT SUMMARY ==========

Tables   : 1
Pictures : 2
Formulas : ...
Don't worry if the formula count isn't what we expect yet. That itself is part of the experiment: our formula is intentionally an image, so the baseline pipeline may treat it as a picture rather than as a semantic formula.
Step 17 — What we've learned from this experiment
The most important mental model is:

                    PDF
                     │
                     ▼
                  Docling
                     │
          ┌──────────┼──────────┐
          ↓          ↓          ↓
       Table      Picture     Formula
          │          │          │
          ↓          ↓          ↓
      TableItem  PictureItem  Formula/
                              Text item
          │          │          │
          └──────────┼──────────┘
                     ↓
              DoclingDocument
And each content type needs a different downstream strategy.
ContentWhat we want from DoclingRAG implicationTextText + hierarchyNormal text chunkTableRows/columns/cellsStructure-aware chunkImagePicture + locationVision processingFormulaFormula/LaTeX representationFormula-aware textCaptionAssociation with elementPreserve with elementOne important correction from our previous stage
This stage also helps explain the Analytics Layer problem you found.
We should never assume:

Looks like a table
        ↓
Must be TableItem
or:

Looks like two columns
        ↓
Must be two independent text regions
The PDF's internal structure matters.
That's exactly why we're now explicitly inspecting:

doc.tables
doc.pictures
doc.iterate_items()
doc.export_to_dict()
rather than only:

doc.export_to_markdown()
Where we are after this implementation
Our Docling track now becomes:

Stage 1.4.2.5
OCR Approach
│
├── 1.4.2.5.1 — Basic OCR
│   ✅
│
├── 1.4.2.5.2 — Docling for Scanned PDFs
│   ✅
│
├── 1.4.2.5.3 — Docling Layout & Reading Order
│   ✅
│
├── 1.4.2.5.4 — Table / Image / Formula Understanding
│   🔵 CURRENT
│
└── 1.4.2.5.5 — Docling → LangChain → RAG
    ⏳
Do not move to 1.4.2.5.5 yet.
First, run the notebook cells above against the new PDF. The important outputs for our next step will be:

1. len(doc.tables)
2. len(doc.pictures)
3. table.export_to_markdown(doc)
4. table.export_to_dataframe(doc)
5. picture.get_image(doc)
6. output of doc.iterate_items()
7. formula-related items, if any
8. doc.export_to_markdown()
That will let us investigate exactly how your Docling 2.120.3 installation represents each content type, rather than relying on assumptions from newer Docling documentation."""


def sanitize_diagram_chars(text: str) -> str:
    """Converts unsupported Unicode symbols into standard ASCII."""
    mapping = {
        "│": "|",
        "─": "-",
        "┌": "+",
        "┐": "+",
        "└": "+",
        "┘": "+",
        "├": "+",
        "┤": "+",
        "┼": "+",
        "┴": "+",
        "┬": "+",
        "▼": "v",
        "▲": "^",
        "↑": "^",
        "↓": "v",
        "→": "->",
        "←": "<-",
        "✅": "[DONE]",
        "🔵": "[CURRENT]",
        "⏳": "[PENDING]",
        "⭐": "[*]",
    }
    for char, repl in mapping.items():
        text = text.replace(char, repl)
    return text


def is_step_line(line: str) -> bool:
    return bool(
        re.match(
            r"^(Step\s+\d+|Where we are after this implementation)",
            line.strip(),
        )
    )


def is_code_or_diagram(block: str) -> bool:
    diag_chars = set("|+-^v<>")
    has_diag = any(c in diag_chars for c in block) and ("\n" in block)
    keywords = [
        "import ",
        "print(",
        "converter = ",
        "result = ",
        "markdown_text = ",
        "for i, ",
        "table = ",
        "picture_image = ",
        "if len(",
        "getattr(",
        "document_dict = ",
        "json.dumps(",
        "output_json = ",
        "formula_items = ",
        "Docling version:",
        "True",
        "===== TABLE",
        "===== PICTURE",
        "========== DOCLING CONTENT SUMMARY ==========",
        "Stage 1.4.2.5\n",
    ]
    has_kw = any(k in block for k in keywords)
    return has_diag or has_kw


def get_callout_category(block: str) -> str:
    if (
        "import " in block
        or "print(" in block
        or "converter" in block
        or "json" in block
    ):
        return "PYTHON"
    if (
        "Docling version:" in block
        or block.strip() == "True"
        or "Tables   :" in block
    ):
        return "OUTPUT"
    if "PDF" in block and "Docling" in block:
        return "PIPELINE FLOW"
    if (
        "TableItem" in block
        or "Stage 1.4.2.5" in block
        or "RESULT COMPOSITION" in block
    ):
        return "DOCUMENT STRUCTURE"
    return "STRUCTURE / CODE"


def create_step_header(
    title: str, step_style: ParagraphStyle, width: float = 504
) -> Table:
    """Renders Step headings in a refined Sky Blue pill container."""
    clean_title = sanitize_diagram_chars(title)
    p = Paragraph(f"<b>{html.escape(clean_title)}</b>", step_style)
    t = Table([[p]], colWidths=[width])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F0F9FF")),
                ("BOX", (0, 0), (-1, -1), 1.0, colors.HexColor("#0284C7")),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    return t


def create_attachment_box(
    block: str,
    category_title: str,
    body_style: ParagraphStyle,
    label_style: ParagraphStyle,
    width: float = 504,
) -> Table:
    """Builds clean, modern blue-themed callout boxes."""
    clean_text = sanitize_diagram_chars(block)
    escaped_code = (
        html.escape(clean_text).replace("\n", "<br/>").replace(" ", "&nbsp;")
    )

    header_para = Paragraph(f"<b>{category_title}</b>", label_style)
    content_para = Paragraph(escaped_code, body_style)

    table_data = [[header_para], [content_para]]

    callout_table = Table(table_data, colWidths=[width])
    callout_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
                ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#CBD5E1")),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, 0), 6),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 2),
                ("TOPPADDING", (0, 1), (-1, 1), 2),
                ("BOTTOMPADDING", (0, 1), (-1, 1), 8),
            ]
        )
    )
    return callout_table


def segment_text(raw_text: str):
    """Accurately separates Step headings from surrounding body text."""
    normalized = re.sub(
        r"(?m)^(Step\s+\d+.*?)$", r"\n\n\1\n\n", raw_text.strip()
    )
    normalized = re.sub(
        r"(?m)^(Where we are after this implementation.*?)$",
        r"\n\n\1\n\n",
        normalized,
    )
    return [b.strip() for b in normalized.split("\n\n") if b.strip()]


def build_pdf(
    output_filename: str = "Stage_1.4.2.5.4_Docling_Presentation.pdf",
):
    doc = SimpleDocTemplate(
        output_filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54,
    )

    styles = getSampleStyleSheet()

    body_style = ParagraphStyle(
        "ModernBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=14.5,
        textColor=colors.HexColor("#1E293B"),
        spaceAfter=6,
    )

    h1_style = ParagraphStyle(
        "ModernH1",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#0F172A"),
        spaceBefore=8,
        spaceAfter=4,
    )

    step_text_style = ParagraphStyle(
        "StepTextStyle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#0369A1"),
    )

    box_label_style = ParagraphStyle(
        "BoxLabel",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor("#0284C7"),
    )

    box_code_style = ParagraphStyle(
        "BoxCode",
        parent=styles["Normal"],
        fontName="Courier",
        fontSize=8,
        leading=11.5,
        textColor=colors.HexColor("#0F172A"),
    )

    story = []
    blocks = segment_text(RAW_TEXT)

    for block in blocks:
        # Title handling
        if block.startswith("Stage 1.4.2.5.4 —"):
            story.append(Paragraph(html.escape(block), h1_style))
            story.append(
                HRFlowable(
                    width="100%",
                    thickness=1.2,
                    color=colors.HexColor("#0284C7"),
                    spaceBefore=2,
                    spaceAfter=8,
                )
            )
            continue

        # Step Subheadings — Highlighted light-blue banner
        if is_step_line(block):
            story.append(Spacer(1, 6))
            story.append(
                KeepTogether([create_step_header(block, step_text_style)])
            )
            story.append(Spacer(1, 6))
            continue

        # Code / ASCII Diagram containers
        if is_code_or_diagram(block):
            category = get_callout_category(block)
            box = create_attachment_box(
                block, category, box_code_style, box_label_style
            )
            story.append(Spacer(1, 3))
            story.append(KeepTogether([box]))
            story.append(Spacer(1, 5))
            continue

        # Standard body text
        clean_body = sanitize_diagram_chars(block)
        escaped_text = html.escape(clean_body).replace("\n", "<br/>")
        story.append(Paragraph(escaped_text, body_style))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Generated successfully: {output_filename}")


if __name__ == "__main__":
    build_pdf()