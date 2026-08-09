# PDF Extraction Patterns

Patterns for extracting text, tables, images, and metadata from PDF documents.

---
## Table of Contents

- [Choose the Extractor First](#choose-the-extractor-first)
- [Text Extraction](#text-extraction)
- [Basic Text (pdfplumber)](#basic-text-pdfplumber)
- [Text with Layout Preservation](#text-with-layout-preservation)
- [Specific Page Regions](#specific-page-regions)
- [Example: Extract header region](#example-extract-header-region)
- [Table Extraction](#table-extraction)
- [Simple Tables (pdfplumber)](#simple-tables-pdfplumber)
- [Custom Table Settings](#custom-table-settings)
- [Camelot for Complex Tables](#camelot-for-complex-tables)
- [Lattice mode - for tables with visible borders](#lattice-mode-for-tables-with-visible-borders)
- [Stream mode - for tables without visible borders](#stream-mode-for-tables-without-visible-borders)
- [Access table data](#access-table-data)
- [Image Extraction](#image-extraction)
- [Extract Images (PyMuPDF/fitz)](#extract-images-pymupdffitz)
- [Image with Metadata](#image-with-metadata)
- [Metadata Extraction](#metadata-extraction)
- [Document Metadata (pypdf)](#document-metadata-pypdf)
- [Form Fields](#form-fields)
- [OCR Integration](#ocr-integration)
- [OCRmyPDF for Full Scanned PDFs](#ocrmypdf-for-full-scanned-pdfs)
- [Extract Text After OCR](#extract-text-after-ocr)
- [Tesseract OCR for Custom Page Pipelines](#tesseract-ocr-for-custom-page-pipelines)
- [Tesseract OCR for Scanned PDFs](#tesseract-ocr-for-scanned-pdfs)
- [Hybrid Extraction (Text + OCR)](#hybrid-extraction-text-ocr)
- [Batch Processing](#batch-processing)
- [Process Multiple PDFs](#process-multiple-pdfs)
- [Error Handling](#error-handling)
- [Robust Extraction](#robust-extraction)
- [Related](#related)


## Choose the Extractor First

| PDF Shape | Default Path | Why |
|-----------|--------------|-----|
| Born-digital text PDF | `pdfplumber` | Best default for selectable text and layout-aware extraction |
| Scanned/image-only PDF | `OCRmyPDF` first, then `pdfplumber` | Adds a searchable text layer before extraction |
| Table-heavy PDF | `pdfplumber` first, `Camelot` for hard cases | Faster iteration before using heavier table heuristics |
| Image/raster workflow | `PyMuPDF` | Precise page rendering, image extraction, and OCR preparation |

---

## Text Extraction

### Basic Text (pdfplumber)

```python
import pdfplumber

def extract_all_text(pdf_path: str) -> str:
    """Extract text from all pages."""
    text_parts = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                text_parts.append(text)

    return '\n\n'.join(text_parts)
```

### Text with Layout Preservation

```python
import pdfplumber

def extract_with_layout(pdf_path: str) -> str:
    """Preserve original layout using character positions."""
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[0]

        # Extract with layout preservation
        text = page.extract_text(
            layout=True,           # Preserve layout
            x_tolerance=3,         # Horizontal tolerance
            y_tolerance=3,         # Vertical tolerance
        )

        return text
```

### Specific Page Regions

```python
import pdfplumber

def extract_region(pdf_path: str, bbox: tuple) -> str:
    """Extract text from specific region (x0, y0, x1, y1)."""
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[0]

        # Crop to region
        cropped = page.crop(bbox)
        text = cropped.extract_text()

        return text

# Example: Extract header region
header_text = extract_region('doc.pdf', (0, 0, 612, 100))
```

---

## Table Extraction

### Simple Tables (pdfplumber)

```python
import pdfplumber
import pandas as pd

def extract_tables(pdf_path: str) -> list[pd.DataFrame]:
    """Extract all tables as DataFrames."""
    dataframes = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()

            for table in tables:
                if table and len(table) > 1:
                    # First row as header
                    df = pd.DataFrame(table[1:], columns=table[0])
                    dataframes.append(df)

    return dataframes
```

### Custom Table Settings

```python
import pdfplumber

def extract_complex_table(pdf_path: str, page_num: int = 0) -> list:
    """Extract table with custom settings for complex layouts."""
    table_settings = {
        'vertical_strategy': 'text',      # 'lines', 'text', or 'explicit'
        'horizontal_strategy': 'text',
        'snap_tolerance': 3,
        'snap_x_tolerance': 3,
        'snap_y_tolerance': 3,
        'join_tolerance': 3,
        'edge_min_length': 3,
        'min_words_vertical': 3,
        'min_words_horizontal': 1,
        'intersection_tolerance': 3,
    }

    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[page_num]
        tables = page.extract_tables(table_settings)
        return tables
```

### Camelot for Complex Tables

`camelot-py` is the actively maintained package (2026 releases add an optional neural backend alongside the original lattice/stream heuristics); avoid the older `camelot-fork` PyPI package, which has had no recent releases.

```python
import camelot

# Lattice mode - for tables with visible borders
tables = camelot.read_pdf('document.pdf', flavor='lattice')

# Stream mode - for tables without visible borders
tables = camelot.read_pdf('document.pdf', flavor='stream')

# Access table data
for table in tables:
    print(f'Accuracy: {table.accuracy}')
    df = table.df
    print(df)

    # Export
    table.to_csv('table.csv')
    table.to_excel('table.xlsx')
```

**Judgment call, not a formality**: `table.accuracy` is Camelot's own confidence score, not ground truth — a high score can still hide a merged-cell or multi-line-header misread. On any table feeding a financial, legal, or otherwise consequential downstream decision, render the source page (or open it) and eyeball at least the header row and one data row against the DataFrame before trusting it. `pdfplumber`'s `extract_tables()` has no accuracy score at all, so the same manual check applies there, arguably more so.

---

## Image Extraction

**License note**: PyMuPDF (`fitz`) is dual-licensed AGPL-3.0/commercial. Using it inside a closed-source application or as part of a SaaS backend can trigger AGPL's source-disclosure obligations; get a commercial license from Artifex or use a permissively-licensed alternative (e.g. `pypdf` for page/metadata work, `pdfplumber` for text/tables) where it covers the need. Image extraction and rasterization specifically have no equivalent lightweight substitute, so budget for licensing rather than skip the check.

### Extract Images (PyMuPDF/fitz)

```python
import fitz  # PyMuPDF
from pathlib import Path

def extract_images(pdf_path: str, output_dir: str) -> list[str]:
    """Extract all images from PDF."""
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    doc = fitz.open(pdf_path)
    saved_images = []

    for page_num, page in enumerate(doc):
        images = page.get_images()

        for img_index, img in enumerate(images):
            xref = img[0]
            base_image = doc.extract_image(xref)

            image_bytes = base_image['image']
            image_ext = base_image['ext']

            filename = f'page{page_num + 1}_img{img_index + 1}.{image_ext}'
            filepath = output_path / filename

            with open(filepath, 'wb') as f:
                f.write(image_bytes)

            saved_images.append(str(filepath))

    doc.close()
    return saved_images
```

### Image with Metadata

```python
import fitz

def get_image_info(pdf_path: str) -> list[dict]:
    """Get detailed image information."""
    doc = fitz.open(pdf_path)
    image_info = []

    for page_num, page in enumerate(doc):
        for img in page.get_images():
            xref = img[0]
            base = doc.extract_image(xref)

            info = {
                'page': page_num + 1,
                'xref': xref,
                'width': base['width'],
                'height': base['height'],
                'colorspace': base['colorspace'],
                'bpc': base['bpc'],  # bits per component
                'ext': base['ext'],
                'size_bytes': len(base['image']),
            }
            image_info.append(info)

    doc.close()
    return image_info
```

---

## Metadata Extraction

### Document Metadata (pypdf)

```python
from pypdf import PdfReader

def extract_metadata(pdf_path: str) -> dict:
    """Extract PDF metadata."""
    reader = PdfReader(pdf_path)

    metadata = {
        'num_pages': len(reader.pages),
        'is_encrypted': reader.is_encrypted,
    }

    if reader.metadata:
        metadata.update({
            'title': reader.metadata.get('/Title'),
            'author': reader.metadata.get('/Author'),
            'subject': reader.metadata.get('/Subject'),
            'creator': reader.metadata.get('/Creator'),
            'producer': reader.metadata.get('/Producer'),
            'creation_date': reader.metadata.get('/CreationDate'),
            'modification_date': reader.metadata.get('/ModDate'),
        })

    return metadata
```

### Form Fields

```python
from pypdf import PdfReader

def extract_form_fields(pdf_path: str) -> dict:
    """Extract form field values."""
    reader = PdfReader(pdf_path)
    fields = {}

    if reader.get_fields():
        for field_name, field_data in reader.get_fields().items():
            value = field_data.get('/V')
            field_type = field_data.get('/FT')

            fields[field_name] = {
                'value': value,
                'type': str(field_type) if field_type else None,
            }

    return fields
```

---

## OCR Integration

### OCRmyPDF for Full Scanned PDFs

```bash
ocrmypdf --skip-text --rotate-pages --deskew input.pdf searchable.pdf
```

After OCR, treat `searchable.pdf` as a born-digital PDF for downstream extraction. This is the preferred 2026 default for full scanned documents because it preserves the original pages while adding a searchable text layer.

### Extract Text After OCR

```python
import pdfplumber

with pdfplumber.open('searchable.pdf') as pdf:
    text = '\n\n'.join(page.extract_text() or '' for page in pdf.pages)
```

### Tesseract OCR for Custom Page Pipelines

### Tesseract OCR for Scanned PDFs

```python
import fitz
from PIL import Image
import pytesseract
import io

def ocr_pdf(pdf_path: str) -> str:
    """Extract text from scanned PDF using OCR."""
    doc = fitz.open(pdf_path)
    text_parts = []

    for page in doc:
        # Render page as image
        pix = page.get_pixmap(dpi=300)
        img_data = pix.tobytes('png')

        # OCR with Tesseract
        image = Image.open(io.BytesIO(img_data))
        text = pytesseract.image_to_string(image)
        text_parts.append(text)

    doc.close()
    return '\n\n'.join(text_parts)
```

### Hybrid Extraction (Text + OCR)

```python
import pdfplumber
import fitz
from PIL import Image
import pytesseract
import io

def hybrid_extract(pdf_path: str, ocr_threshold: int = 50) -> str:
    """Use OCR only when text extraction fails."""
    text_parts = []

    with pdfplumber.open(pdf_path) as pdf:
        doc = fitz.open(pdf_path)

        for i, page in enumerate(pdf.pages):
            text = page.extract_text()

            if text and len(text.strip()) > ocr_threshold:
                # Text extraction worked
                text_parts.append(text)
            else:
                # Fall back to custom OCR when no text layer exists
                fitz_page = doc[i]
                pix = fitz_page.get_pixmap(dpi=300)
                img = Image.open(io.BytesIO(pix.tobytes('png')))
                ocr_text = pytesseract.image_to_string(img)
                text_parts.append(ocr_text)

        doc.close()

    return '\n\n'.join(text_parts)
```

---

## Batch Processing

### Process Multiple PDFs

```python
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
import pdfplumber

def process_pdf(pdf_path: Path) -> dict:
    """Process single PDF and return results."""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = '\n'.join(
                page.extract_text() or ''
                for page in pdf.pages
            )

            return {
                'file': pdf_path.name,
                'pages': len(pdf.pages),
                'text': text,
                'success': True,
            }
    except Exception as e:
        return {
            'file': pdf_path.name,
            'error': str(e),
            'success': False,
        }

def batch_process(input_dir: str, workers: int = 4) -> list[dict]:
    """Process all PDFs in directory using multiprocessing."""
    pdf_files = list(Path(input_dir).glob('*.pdf'))

    with ProcessPoolExecutor(max_workers=workers) as executor:
        results = list(executor.map(process_pdf, pdf_files))

    return results
```

---

## Error Handling

### Robust Extraction

```python
import pdfplumber
from pypdf import PdfReader

def safe_extract(pdf_path: str) -> dict:
    """Extract with fallback strategies."""
    result = {
        'text': None,
        'tables': [],
        'metadata': {},
        'errors': [],
    }

    # Try pdfplumber first
    try:
        with pdfplumber.open(pdf_path) as pdf:
            result['text'] = '\n'.join(
                page.extract_text() or ''
                for page in pdf.pages
            )

            for page in pdf.pages:
                result['tables'].extend(page.extract_tables())

    except Exception as e:
        result['errors'].append(f'pdfplumber: {e}')

    # Get metadata with pypdf
    try:
        reader = PdfReader(pdf_path)
        if reader.metadata:
            result['metadata'] = dict(reader.metadata)
    except Exception as e:
        result['errors'].append(f'pypdf: {e}')

    return result
```

---

## Related

- [pdf-generation-patterns.md](pdf-generation-patterns.md) - Creating PDFs
- [../SKILL.md](../SKILL.md) - Quick reference
