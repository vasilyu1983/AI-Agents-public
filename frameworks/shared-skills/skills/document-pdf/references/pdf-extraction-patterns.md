# PDF Extraction Patterns

Patterns for extracting text, tables, images, and metadata from PDF documents.

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

---

## Image Extraction

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
                # Fall back to OCR
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
