import nbformat as nbf

# Initialize a new version 4 Jupyter Notebook
nb = nbf.v4.new_notebook()

# Define the interleaved markdown and code cells
cells = [
    # --- Introduction ---
    nbf.v4.new_markdown_cell(
        r"""# Stage 1.4.2.5.4
## Level 3 — Image Content Understanding & Semantic Extraction

Yes. Now we implement Level 3 — Image Content Understanding & Semantic Extraction as a real experiment.
The key change from Level 1/2 is:

Level 1 → Is there a picture?
Level 2 → Can I extract the picture?
Level 3 → Can a vision model understand what is inside the picture?
Docling supports picture-description enrichment, where a vision-language model generates a textual description for a detected picture. The description is added to the DoclingDocument for accessibility/searchability. (Docling Project)
For our architecture diagram, this is exactly the experiment we want.
Stage 1.4.2.5.4
Level 3 — Image Content Understanding & Semantic Extraction
Our experiment:

Architecture Diagram
        ↓
   PictureItem
        ↓
Picture Description / VLM
        ↓
Semantic description
        ↓
Searchable text
        ↓
Potential RAG content
We will not use a separate OCR script first. We want to see what Docling's picture-understanding capability can do."""
    ),
    # --- Step 1 ---
    nbf.v4.new_markdown_cell(
        r"""Step 1 — Start with our existing PDF
Use the same PDF:

docling_table_image_formula_sample.pdf
And verify:"""
    ),
    nbf.v4.new_code_cell(
        r"""from pathlib import Path

pdf_path = Path(
    "stage_1_4_2_5_4/docling_table_image_formula_sample.pdf"
)

print(pdf_path.exists())"""
    ),
    nbf.v4.new_markdown_cell(
        r"""Expected:

True"""
    ),
    # --- Step 2 ---
    nbf.v4.new_markdown_cell(
        r"""Step 2 — Verify your Docling version
Because you are using Docling 2.120.3, keep this in the notebook:"""
    ),
    nbf.v4.new_code_cell(
        r"""import docling

print(docling.__version__)"""
    ),
    nbf.v4.new_markdown_cell(
        r"""Expected:

2.120.3
This is important because Docling's enrichment APIs have evolved."""
    ),
    # --- Step 3 ---
    nbf.v4.new_markdown_cell(
        r"""Step 3 — Import the picture-description configuration
Run:"""
    ),
    nbf.v4.new_code_cell(
        r"""from docling.datamodel.pipeline_options import (
    PdfPipelineOptions,
    smolvlm_picture_description,
)

from docling.datamodel.base_models import InputFormat

from docling.document_converter import (
    DocumentConverter,
    PdfFormatOption,
)"""
    ),
    nbf.v4.new_markdown_cell(
        r"""Docling provides a preconfigured smolvlm_picture_description option for local picture description. (Docling Project)"""
    ),
    # --- Step 4 ---
    nbf.v4.new_markdown_cell(
        r"""Step 4 — Configure picture understanding
Create the pipeline:"""
    ),
    nbf.v4.new_code_cell(
        r"""pipeline_options = PdfPipelineOptions()

pipeline_options.generate_picture_images = True

pipeline_options.do_picture_description = True

pipeline_options.picture_description_options = (
    smolvlm_picture_description
)"""
    ),
    nbf.v4.new_markdown_cell(
        r"""Notice the important new line:

pipeline_options.do_picture_description = True
This is what moves us from:

Level 2
Picture extraction
to:

Level 3
Picture understanding
Docling's documentation describes do_picture_description as enabling automatic textual descriptions of pictures using vision-language models. (Docling Project)"""
    ),
    # --- Step 5 ---
    nbf.v4.new_markdown_cell(
        r"""Step 5 — Create the converter"""
    ),
    nbf.v4.new_code_cell(
        r"""converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(
            pipeline_options=pipeline_options
        )
    }
)"""
    ),
    # --- Step 6 ---
    nbf.v4.new_markdown_cell(
        r"""Step 6 — Convert the PDF"""
    ),
    nbf.v4.new_code_cell(
        r"""result = converter.convert(pdf_path)

doc = result.document"""
    ),
    nbf.v4.new_markdown_cell(
        r"""This time the pipeline is doing considerably more work:

PDF
 │
 ├── Layout analysis
 │
 ├── Table detection
 │
 ├── Picture detection
 │
 ├── Picture extraction
 │
 └── Picture description
          ↓
        VLM
So don't be surprised if this conversion takes longer than our previous one."""
    ),
    # --- Step 7 ---
    nbf.v4.new_markdown_cell(
        r"""Step 7 — Confirm that our picture still exists"""
    ),
    nbf.v4.new_code_cell(
        r"""print("Number of pictures:", len(doc.pictures))"""
    ),
    nbf.v4.new_markdown_cell(
        r"""Expected:

Number of pictures: 2
Why possibly two?
Our sample PDF contains:

architecture diagram
formula image
So Docling may detect both as pictures."""
    ),
    # --- Step 8 ---
    nbf.v4.new_markdown_cell(
        r"""Step 8 — Inspect the first picture"""
    ),
    nbf.v4.new_code_cell(
        r"""for i, picture in enumerate(doc.pictures, start=1):

    print(f"\n========== PICTURE {i} ==========")

    print(type(picture))

    print(picture)"""
    ),
    nbf.v4.new_markdown_cell(
        r"""We're looking for evidence that the picture now has enrichment information."""
    ),
    # --- Step 9 ---
    nbf.v4.new_markdown_cell(
        r"""Step 9 — Look specifically for the picture description
Let's inspect the picture object's attributes:"""
    ),
    nbf.v4.new_code_cell(
        r"""picture = doc.pictures[0]

attributes = [
    name
    for name in dir(picture)
    if not name.startswith("_")
]

print(attributes)"""
    ),
    nbf.v4.new_markdown_cell(
        r"""Look for attributes related to:

annotation
description
caption
prov
image
The exact representation can vary by Docling version, which is why we're inspecting your actual 2.120.3 object rather than assuming the current API shape."""
    ),
    # --- Step 10 ---
    nbf.v4.new_markdown_cell(
        r"""Step 10 — Inspect the picture annotations
Try:"""
    ),
    nbf.v4.new_code_cell(
        r"""print(
    getattr(
        picture,
        "annotations",
        None
    )
)"""
    ),
    nbf.v4.new_markdown_cell(
        r"""If you get an object/list instead of None, inspect it:"""
    ),
    nbf.v4.new_code_cell(
        r"""annotations = getattr(
    picture,
    "annotations",
    None
)

print(type(annotations))

if annotations:
    for annotation in annotations:
        print(annotation)"""
    ),
    nbf.v4.new_markdown_cell(
        r"""This is where we expect to find the semantic description generated by the vision model."""
    ),
    # --- Step 11 ---
    nbf.v4.new_markdown_cell(
        r"""Step 11 — Inspect the complete picture object
For our learning experiment, I also want you to run:"""
    ),
    nbf.v4.new_code_cell(
        r"""print(picture.model_dump())"""
    ),
    nbf.v4.new_markdown_cell(
        r"""Because DoclingDocument elements are Pydantic models in the current Docling architecture.
This gives us a much better picture of what Docling actually stored.
Look for anything resembling:

annotations
description
text
provenance"""
    ),
    # --- Step 12 ---
    nbf.v4.new_markdown_cell(
        r"""Step 12 — Search the entire DoclingDocument
Now let's use the most important test.
We know the architecture contains:

Producer
Event Hubs
Stream Consumer
Data Explorer
Run:"""
    ),
    nbf.v4.new_code_cell(
        r"""architecture_words = [
    "Producer",
    "Event Hubs",
    "Stream Consumer",
    "Data Explorer",
]"""
    ),
    nbf.v4.new_markdown_cell(
        r"""Then:"""
    ),
    nbf.v4.new_code_cell(
        r"""markdown_text = doc.export_to_markdown()

print(markdown_text)"""
    ),
    nbf.v4.new_markdown_cell(
        r"""And:"""
    ),
    nbf.v4.new_code_cell(
        r"""print("\n========== ARCHITECTURE TEXT TEST ==========")

for word in architecture_words:

    found = word.lower() in markdown_text.lower()

    print(
        f"{word:20} -> "
        f"{'FOUND' if found else 'NOT FOUND'}"
    )"""
    ),
    # --- Step 13 ---
    nbf.v4.new_markdown_cell(
        r"""Step 13 — This is the critical comparison
Before Level 3 we had something like:

Architecture diagram detected     ✅
Picture extracted                 ✅
"Producer" in document text       ❌
"Event Hubs" in document text     ❌
After picture-description enrichment, we're testing whether we get:

Architecture diagram detected     ✅
Picture extracted                 ✅
Picture described by VLM          ✅
Semantic information available    ✅
However, do not expect the VLM description to necessarily reproduce every label verbatim.
For example, it might produce:

"The diagram shows an event processing
architecture in which a producer sends
events to Event Hubs, which forwards
them to a stream consumer and ultimately
to Data Explorer."
That is semantic understanding, even if it doesn't return the exact four labels."""
    ),
    # --- Step 14 ---
    nbf.v4.new_markdown_cell(
        r"""Step 14 — Very important: OCR vs semantic understanding
This is where I want you to make an important distinction.
Suppose the picture description is:

"An architecture diagram showing a producer sending events through Event Hubs to a stream consumer and Data Explorer."
That demonstrates:

Image
 ↓
Vision model
 ↓
Meaning
But it does not necessarily prove exact OCR of every text label.
Compare:

OCR
Producer
Event Hubs
Stream Consumer
Data Explorer
Semantic description
A producer sends events through
Event Hubs to a stream consumer
and then to Data Explorer.
These are different outputs.
Therefore our Level 3 is correctly called:

Image Content Understanding & Semantic Extraction
rather than simply:

Image OCR."""
    ),
    # --- Step 15 ---
    nbf.v4.new_markdown_cell(
        r"""Step 15 — Make the experiment more rigorous
Let's inspect both the raw picture and the generated description."""
    ),
    nbf.v4.new_code_cell(
        r"""for i, picture in enumerate(doc.pictures, start=1):

    print("\n" + "=" * 70)
    print(f"PICTURE {i}")
    print("=" * 70)

    print("\nType:")
    print(type(picture))

    print("\nImage:")
    image = picture.get_image(doc)
    print(type(image))

    print("\nAnnotations:")
    print(
        getattr(
            picture,
            "annotations",
            None
        )
    )"""
    ),
    nbf.v4.new_markdown_cell(
        r"""This gives us a clean:

Picture
├── actual image
└── semantic annotation"""
    ),
    # --- Step 16 ---
    nbf.v4.new_markdown_cell(
        r"""Step 16 — Inspect the complete document after enrichment
Now:"""
    ),
    nbf.v4.new_code_cell(
        r"""markdown_text = doc.export_to_markdown()

print(markdown_text)"""
    ),
    nbf.v4.new_markdown_cell(
        r"""This is particularly important.
We're asking:

Did the picture description become part of the document representation?
Docling's picture-description enrichment is specifically designed to add descriptions to the document for searchability/accessibility. (Docling Project)"""
    ),
    # --- Step 17 ---
    nbf.v4.new_markdown_cell(
        r"""Step 17 — Compare Level 2 vs Level 3
Your notebook should now document this very clearly.

Level 2
PDF
 ↓
Picture detection
 ↓
PictureItem
 ↓
Actual image
Level 3
PDF
 ↓
Picture detection
 ↓
PictureItem
 ↓
Actual image
 ↓
Vision-Language Model
 ↓
Picture description
 ↓
Semantic text
And ultimately:

Semantic text
      ↓
   Chunking
      ↓
  Embedding
      ↓
 Vector DB
      ↓
    RAG"""
    ),
    # --- Step 18 ---
    nbf.v4.new_markdown_cell(
        r"""Step 18 — What happens to our architecture diagram?
Our original image:

┌─────────────────────────────────────────┐
│       Event Processing Architecture     │
│                                         │
│ Producer → Event Hubs → Stream Consumer │
│                    ↓                    │
│              Data Explorer              │
└─────────────────────────────────────────┘
can potentially become something like:

Event Processing Architecture

A producer sends events to Azure Event Hubs.
The events are consumed by a stream consumer
and subsequently sent to Azure Data Explorer
for analytics.
That textual representation is much more useful to a text-based RAG pipeline."""
    ),
    # --- Step 19 ---
    nbf.v4.new_markdown_cell(
        r"""Step 19 — Why this is important for your production RAG
Consider a user asking:

"Where do the events go after Event Hubs?"
Without Level 3:

PDF
 ↓
Picture
 ↓
Vector DB
The text RAG pipeline may not know what is inside the picture.
With Level 3:

PDF
 ↓
Picture
 ↓
VLM
 ↓
"Events are consumed by Stream Consumer
and sent to Data Explorer."
 ↓
Chunk
 ↓
Embedding
 ↓
ChromaDB
Now retrieval can potentially return the semantic information from the architecture diagram."""
    ),
    # --- Step 20 ---
    nbf.v4.new_markdown_cell(
        r"""Step 20 — One important caveat
For exact labels, diagrams, and technical architecture, a generic picture-description model may not be sufficient.
For example, the model could say:

"A cloud architecture showing an event ingestion service and analytics service."
while missing:

Azure Event Hubs
Azure Data Explorer
Therefore production multimodal ingestion often combines:

              Image
                │
        ┌───────┴────────┐
        ↓                ↓
       OCR              VLM
        │                │
 exact text          semantic meaning
        │                │
        └───────┬────────┘
                ↓
        combined representation
This is an important lesson for your RAG journey:

OCR gives you text; VLM gives you meaning; combining them can give you a richer representation.
Our Stage 1.4.2.5.4 progress
We can now structure the stage as:

Stage 1.4.2.5.4
Docling Table / Image / Formula Understanding

│
├── Level 1
│   Picture Detection
│   ✅
│
├── Level 2
│   Picture Extraction
│   ✅
│
└── Level 3
    Image Content Understanding & Semantic Extraction
    🔵 CURRENT
And Level 3 itself is:

Step 1
Enable picture description
        ↓
Step 2
Run Docling conversion
        ↓
Step 3
Inspect PictureItem
        ↓
Step 4
Inspect picture annotations
        ↓
Step 5
Export Markdown
        ↓
Step 6
Verify semantic description
        ↓
Step 7
Compare OCR vs VLM understanding
        ↓
Step 8
Understand RAG implications
One note before you run it: because you're on Docling 2.120.3, if the smolvlm_picture_description import or the annotation fields differ in your environment, don't modify things randomly. Paste the exact error/output here. We'll adapt the implementation specifically to your installed version rather than silently using APIs from a newer Docling release."""
    ),
]

# Assign all cells to the notebook
nb["cells"] = cells

# Save to .ipynb file
output_file = "stage_1_4_2_5_4_level_3.ipynb"
with open(output_file, "w", encoding="utf-8") as f:
    nbf.write(nb, f)

print(f"Notebook successfully generated: {output_file}")