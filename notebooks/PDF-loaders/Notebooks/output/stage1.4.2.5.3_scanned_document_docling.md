## Azure Event Processing Architecture

This sample document is designed for Stage 1.4.2.5.3 - Docling Layout &amp; Reading Order. It contains headings, paragraphs, a two-column layout, a table, a caption, and content whose logical reading order differs from simple top-to-bottom visual scanning.

## 1. Overview

An enterprise application publishes events to Azure Event Hubs. A downstream processing component consumes those events and sends selected records to Azure Data Explorer for analytics. The architecture contains independent ingestion and analytics stages.

## Ingestion Layer

The producer sends events to Event Hubs. Event Hubs provides scalable event ingestion and partitions the event stream for parallel consumption.

Key responsibility: reliably accept high-volume event data.

Figure 1 - Logical processing flow

## 2. Processing Stages

|   Stage | Component           | Purpose                              |
|---------|---------------------|--------------------------------------|
|       1 | Event Producer      | Publishes business events            |
|       2 | Azure Event Hubs    | Ingests and partitions event streams |
|       3 | Stream Consumer     | Reads and transforms events          |
|       4 | Azure Data Explorer | Stores data for analytics            |

## 3. Important Design Considerations

The document intentionally places related content in different visual regions. A document parser must identify headings, paragraphs, table content, and the intended reading order rather than simply concatenating text according to raw page coordinates.

The expected logical order is: Overview fi Ingestion Layer fi Analytics Layer fi Processing Stages fi Design Considerations.

## Analytics Layer

A consumer reads events and writes analytical records into Azure Data Explorer. Queries can then be used for operational monitoring and historical analysis.

Key responsibility: provide fast analytical querying.

## 4. Reading Order Test Page

This second page provides a deliberately simple test. The left column describes the producer, while the right column describes the consumer. A useful document parser should preserve the logical relationship between the headings and their associated paragraphs.

| A. Producer                                                                              | B. Consumer                                                                       |
|------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------|
| The producer creates an event containing an identifier, timestamp, and business payload. | The consumer reads events, validates the payload, and forwards analytical fields. |
| Producer output                                                                          | Consumer output                                                                   |
| Event Hub message                                                                        | Analytics record                                                                  |

End of sample document.