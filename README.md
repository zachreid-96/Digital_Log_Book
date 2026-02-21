# Digital Logbook

![Python](https://img.shields.io/badge/Python-3.12+-blue?logo=python&logoColor=white)
![CustomTkinter](https://img.shields.io/badge/GUI-CustomTkinter-green)
![SQLite](https://img.shields.io/badge/Database-SQLite-lightblue?logo=sqlite)
![Tesseract](https://img.shields.io/badge/OCR-Tesseract-orange)
![Status](https://img.shields.io/badge/Status-Mostly%20Complete-brightgreen)

**Author:** Zach Reid | [zforgehub.dev](https://zforgehub.dev)

---

## Overview

Digital Logbook is an OCR-powered replacement for the paper logbook used by copier and printer field technicians to track parts usage across service calls. It automates the extraction, organization, and reporting of service data — turning a manual, paper-based workflow into a searchable, data-backed system.

Built initially for personal use, the architecture is designed with broader adoption in mind.

---

## The Workflow It Replaces

Field technicians traditionally track parts usage by printing a **counter/meter page** directly from the device being serviced — a page that contains the machine's serial number, brand, and current meter reads. Parts used during the service call are recorded by affixing **barcoded parts stickers** directly onto the meter page, using the typically abundant whitespace to avoid covering key data.

This meter page with stickers becomes a self-documenting service record — tying machine identity, service date, and parts used together in a single physical document.

Previously, these pages were either filed physically or manually transcribed. Digital Logbook automates the entire pipeline:

1. Meter pages (with stickers) are scanned to PDF and dropped into a watched folder
2. OCR extracts machine metadata — brand, serial number, and date — using manufacturer-specific keywords
3. Barcode extraction pulls part numbers and quantities from the affixed stickers
4. All data is structured and stored in a central SQLite database
5. Reports are generated on demand for any time window

---

## Features

### OCR Pipeline
- Processes PDFs using **Tesseract OCR** with **multiprocessing** for significantly faster batch handling
- Identifies brand, serial number, and date using manufacturer-specific keyword matching
- Handles **Kyocera, HP, Canon**, and more
- Flags documents with missing or unreadable metadata for manual review rather than silently failing

### Barcode Extraction
- Extracts part numbers and quantities from barcoded stickers on the meter page
- Also multiprocessed for performance
- Flags pages with missing barcode data for manual review

### Manual Review System
- Built-in **PDF viewer** for inspecting flagged documents without leaving the application
- Auto-fills any data successfully extracted, leaving only the missing fields for manual entry
- On completion, feeds corrected data back into the main pipeline and clears it from the review queue

### Database & Reporting
- All processed data stored in a **SQLite database** for fast querying and long-term tracking
- Report generation for **1, 3, 6, 9, and 12-month** windows, exportable to CSV
- Reports include serial number, date, parts used, quantities, and file path references

### Inventory Management
- Import car stock (technician vehicle inventory) via CSV or manual entry
- **Stock comparison tool** — compares parts used in a report window against current car stock
- Highlights overstock, understock, and dead inventory (parts carried but never used)
- Suggests car stock values based on historical usage patterns

### File Organization
- Automatic folder structure setup — no manual prep required
- Successful files renamed with structured metadata and sorted into brand-specific folders
- Failed files routed to manual review folder automatically

### Settings
- All directory paths and configuration stored in a user-facing `config.json`
- Fully customizable folder structure via the Settings menu

---

## Technical Highlights

| Component | Technology |
|---|---|
| Language | Python 3.12+ |
| GUI | CustomTkinter |
| OCR | Tesseract (via pytesseract) |
| PDF Handling | PyMuPDF (fitz) |
| Barcode Extraction | pyzbar / similar |
| Database | SQLite |
| Performance | multiprocessing (OCR + barcode) |
| Image Processing | Pillow (PIL) |
| Fuzzy Matching | rapidfuzz |

### Architecture Notes

- **Multiprocessing** is applied to both the OCR and barcode extraction stages independently, keeping batch processing times low even on large document sets
- **Manufacturer-specific keyword matching** with fuzzy matching via `rapidfuzz` handles real-world OCR noise and inconsistent formatting across device brands
- The **manual review system** was designed as a first-class feature, not an afterthought — the assumption is that OCR will sometimes fail, and the workflow accounts for that gracefully
- Folder structure and database paths are fully configurable, making the tool portable across different technician setups

---

## Planned Enhancements

- Replace current update mechanism with a **HMAC-authenticated API update system** (consistent with other projects in this portfolio)
- Further report types and export formats

---

## Requirements

- Python 3.12+
- [Tesseract-OCR](https://github.com/tesseract-ocr/tesseract) installed and added to system PATH via Environment Variables
- Dependencies: `customtkinter`, `pytesseract`, `Pillow`, `PyMuPDF`, `rapidfuzz`, `sqlite3`

---

## Status

Core pipeline, manual review system, database, reporting, and inventory management are complete and working. Planned enhancements are noted above but are lower priority while other active projects take precedence.

---

## Links

- 🌐 [zforgehub.dev](https://zforgehub.dev) — Portfolio & DevHub
