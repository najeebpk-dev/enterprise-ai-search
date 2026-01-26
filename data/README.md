# Documents Folder

This folder is where you place PDF documents to be ingested into the search system.

## Current Documents

This folder contains 10 PDF documents:

1. Audio Enhancement MS-700-Optimum Manual.pdf
2. Cisco IP Phone 8841 Manual.pdf
3. Dell Latitude 3120 Manual.pdf
4. HP EliteDesk 800 G6 Manual.pdf
5. Lenovo Yoga 11e Manual.pdf
6. Lumens Ladibug Doc Camera Manual.pdf
7. Samsung 3820dw Printer Manual.pdf
8. Samsung ML-3712 Manual.pdf
9. SMART Board SPNL-6065 Manual.pdf
10. SMART Doc Camera 550 Manual.pdf

## Adding New Documents

To add more documents:

1. Copy PDF files to this directory
2. Run the ingestion pipeline: `python src/ingest.py`

## Notes

- Only PDF files are currently supported
- Large files may take longer to process
- Each page is indexed separately for precise citations
- Ensure PDFs contain extractable text (not scanned images without OCR)
