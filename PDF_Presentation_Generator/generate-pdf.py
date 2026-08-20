from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

output_pdf = Path("docling_pipeline_findings.pdf")
doc = SimpleDocTemplate(
    str(output_pdf),
    pagesize=A4,
    leftMargin=36,
    rightMargin=36,
    topMargin=36,
    bottomMargin=36,
)

styles = getSampleStyleSheet()
normal = styles["Normal"]

# Custom Typography Styles
title_style = ParagraphStyle(
    "DocTitle",
    parent=normal,
    fontName="Helvetica-Bold",
    fontSize=16,
    leading=20,
    textColor=colors.HexColor("#0f172a"),
)
subtitle_style = ParagraphStyle(
    "DocSubTitle",
    parent=normal,
    fontName="Helvetica",
    fontSize=9,
    leading=13,
    textColor=colors.HexColor("#475569"),
)
badge_style = ParagraphStyle(
    "DocBadge",
    parent=normal,
    fontName="Helvetica-Bold",
    fontSize=7,
    leading=9,
    textColor=colors.HexColor("#0369a1"),
)
card_title_style = ParagraphStyle(
    "CardTitle",
    parent=normal,
    fontName="Helvetica-Bold",
    fontSize=10,
    leading=14,
    textColor=colors.HexColor("#0f172a"),
)
code_style = ParagraphStyle(
    "CodeBlock",
    parent=normal,
    fontName="Courier",
    fontSize=7.5,
    leading=10.5,
    textColor=colors.HexColor("#f1f5f9"),
)
table_cell_style = ParagraphStyle(
    "TableCell",
    parent=normal,
    fontName="Helvetica",
    fontSize=8,
    leading=11,
    textColor=colors.HexColor("#1e293b"),
)
table_header_style = ParagraphStyle(
    "TableHeader",
    parent=normal,
    fontName="Helvetica-Bold",
    fontSize=8,
    leading=11,
    textColor=colors.HexColor("#334155"),
)

story = []

# Header
story.append(Paragraph("ARCHITECTURE & DIAGNOSTIC BRIEF", badge_style))
story.append(Spacer(1, 4))
story.append(Paragraph("Docling Image Extraction Mechanics", title_style))
story.append(Spacer(1, 3))
story.append(Paragraph("Stage 1.4.2.5.4: Resolving NoneType via Pipeline Image Generation Flags", subtitle_style))
story.append(Spacer(1, 8))
story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#0284c7"), spaceAfter=12))

# Section 1: Comparison Table
story.append(Paragraph("1. Root Cause Analysis: Detection vs. Materialization", card_title_style))
story.append(Spacer(1, 6))

data_comp = [
    [Paragraph("Operation", table_header_style), Paragraph("Underlying Mechanism", table_header_style), Paragraph("Default State", table_header_style)],
    [Paragraph("<b>Detection</b><br/><code>len(doc.pictures) &gt; 0</code>", table_cell_style), 
     Paragraph("Layout model predicts bounding boxes (<code>prov</code>) and assigns semantic labels.", table_cell_style), 
     Paragraph("Always Active", table_cell_style)],
    [Paragraph("<b>Materialization</b><br/><code>picture.get_image(doc)</code>", table_cell_style), 
     Paragraph("PDF raster engine clips and serializes the crop into a <code>PIL.Image</code>.", table_cell_style), 
     Paragraph("<b>Disabled</b><br/>(<code>generate_picture_images=False</code>)", table_cell_style)],
]
t_comp = Table(data_comp, colWidths=[130, 260, 130])
t_comp.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("TOPPADDING", (0, 0), (-1, -1), 5),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
]))
story.append(t_comp)
story.append(Spacer(1, 14))

# Section 2: Code Implementation
story.append(Paragraph("2. Production Configuration Code", card_title_style))
story.append(Spacer(1, 6))

code_text = (
    "from docling.datamodel.pipeline_options import PdfPipelineOptions\n"
    "from docling.datamodel.base_models import InputFormat\n"
    "from docling.document_converter import DocumentConverter, PdfFormatOption\n\n"
    "# 1. Enable pipeline crops\n"
    "pipeline_options = PdfPipelineOptions()\n"
    "pipeline_options.generate_picture_images = True\n"
    "pipeline_options.generate_table_images = True\n\n"
    "# 2. Build converter with explicit format options\n"
    "converter = DocumentConverter(\n"
    "    format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)}\n"
    ")\n"
    "doc = converter.convert('architecture_spec.pdf').document"
)

code_table = Table([[Paragraph(code_text.replace("\n", "<br/>").replace(" ", "&nbsp;"), code_style)]], colWidths=[520])
code_table.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#1e293b")),
    ("PADDING", (0, 0), (-1, -1), 8),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
]))
story.append(code_table)
story.append(Spacer(1, 14))

# Section 3: Roadmap Status
story.append(Paragraph("3. Stage 1.4.2.5.4 Execution Roadmap", card_title_style))
story.append(Spacer(1, 6))

data_roadmap = [
    [Paragraph("Step", table_header_style), Paragraph("Milestone", table_header_style), Paragraph("Status", table_header_style)],
    [Paragraph("1–4", table_cell_style), Paragraph("Synthetic PDF generation, Layout detection, Table/Picture bounding", table_cell_style), Paragraph("<font color='#16a34a'><b>COMPLETED</b></font>", table_cell_style)],
    [Paragraph("5–6", table_cell_style), Paragraph("Resolve NoneType crop issue & enable <code>generate_picture_images</code>", table_cell_style), Paragraph("<font color='#0284c7'><b>IN PROGRESS</b></font>", table_cell_style)],
    [Paragraph("7", table_cell_style), Paragraph("Enable <code>do_formula_enrichment</code> to separate raster math from LaTeX trees", table_cell_style), Paragraph("<font color='#64748b'>NEXT STEP</font>", table_cell_style)],
    [Paragraph("8", table_cell_style), Paragraph("Full multimodal chunking comparison (Text vs Table vs LaTeX vs Crop)", table_cell_style), Paragraph("<font color='#64748b'>UPCOMING</font>", table_cell_style)],
]
t_road = Table(data_roadmap, colWidths=[45, 365, 110])
t_road.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("TOPPADDING", (0, 0), (-1, -1), 4),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
]))
story.append(t_road)

doc.build(story)
print(f"Presentation PDF successfully created at: {output_pdf.resolve()}")