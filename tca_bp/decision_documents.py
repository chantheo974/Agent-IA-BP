"""Local bounded extraction. Document contents are data, never instructions.

No source is changed and no formula/macro/external link is evaluated. Numeric
facts remain proposals to confirm, including numbers from native spreadsheet
cells. Optional OCR uses an installed local Tesseract with fra+eng models.
"""
from __future__ import annotations

import csv
import hashlib
import io
import os
import posixpath
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import tempfile
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation
import xml.etree.ElementTree as ET
import zipfile

MAX_FILE_BYTES = 50 * 1024 * 1024
_NUMBER = re.compile(r"(?<![\w])(?:\(\s*)?[+-]?\d+(?:[ \u00a0\u202f]\d{3})*(?:[.,]\d+)*(?:\s*\))?(?:\s*(?:%|[kKMm]?€|EUR|USD|[kKMm]?\$))?(?![\w])")
_DATE = re.compile(r"\b(?:\d{4}[-/]\d{1,2}[-/]\d{1,2}|\d{1,2}[-/]\d{1,2}[-/]\d{2,4})\b")
_NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
       "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
       "s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
       "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}


def parse_number(raw: str, numeric_locale: str = "fr", *, typed: bool = False) -> dict:
    """Strict numeric proposal. ``value`` uses the displayed unit, never %/100.

``normalized_value`` is a fraction for percentages and base currency for k/M.
One separator followed by three digits is ambiguous in untyped text regardless
of locale. Native OOXML numeric cells bypass locale because their grammar is
specified. Locale never guesses a unit, period, or business field.
"""
    if numeric_locale not in {"fr", "en"}:
        raise ValueError("numeric_locale doit être fr ou en")
    text = str(raw).strip().replace("\u00a0", " ").replace("\u202f", " ")
    result = {"raw": str(raw), "value": None, "normalized_value": None,
              "unit": None, "status": "A_CONFIRMER", "ambiguities": []}
    match = re.search(r"\s*(%|[kKMm]?€|EUR|USD|[kKMm]?\$)$", text)
    factor = Decimal(1)
    if match:
        unit = match.group(1)
        result["unit"] = unit
        text = text[:match.start()].strip()
        if unit == "%":
            factor = Decimal("0.01")
        elif unit[0] in "kK" and len(unit) > 1:
            factor = Decimal(1000)
        elif unit[0] in "mM" and len(unit) > 1:
            factor = Decimal(1000000)
    if text.startswith("(") and text.endswith(")"):
        text = "-" + text[1:-1].strip()
    if typed:
        valid = re.fullmatch(r"[+-]?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?", text)
        canonical = text
    else:
        if re.fullmatch(r"[+-]?\d{1,3}[.,]\d{3}", text):
            result.update(status="AMBIGU", ambiguities=["SEPARATEUR_DECIMAL_OU_MILLIERS"])
            return result
        decimal_sep, group_sep = (",", ".") if numeric_locale == "fr" else (".", ",")
        # French grouping uses spaces. A dot is accepted only as an explicit
        # multi-group thousands sequence or together with the decimal comma.
        d, g = re.escape(decimal_sep), re.escape(group_sep)
        valid = re.fullmatch(rf"[+-]?(?:\d+|\d{{1,3}}(?: \d{{3}})+|\d{{1,3}}(?:{g}\d{{3}})+)(?:{d}\d+)?", text)
        canonical = text.replace(" ", "").replace(group_sep, "").replace(decimal_sep, ".")
    if not valid:
        result.update(status="AMBIGU", ambiguities=["FORMAT_NUMERIQUE_NON_CONFORME_A_LA_LOCALE"])
        return result
    try:
        value = Decimal(canonical)
        if not value.is_finite():
            raise InvalidOperation
    except InvalidOperation:
        result.update(status="AMBIGU", ambiguities=["NOMBRE_NON_FINI_OU_INVALIDE"])
        return result
    result.update(value=format(value, "f"), normalized_value=format(value * factor, "f"))
    return result


def _xml(data: bytes):
    if b"<!DOCTYPE" in data.upper() or b"<!ENTITY" in data.upper():
        raise ValueError("Déclarations XML externes interdites")
    return ET.fromstring(data)


def _zip(data: bytes):
    archive = zipfile.ZipFile(io.BytesIO(data))
    names = set()
    total = 0
    for item in archive.infolist():
        name = PurePosixPath(item.filename)
        total += item.file_size
        if (item.filename in names or name.is_absolute() or ".." in name.parts
                or "\\" in item.filename or item.flag_bits & 1
                or total > 200 * 1024 * 1024 or len(names) > 20000
                or item.file_size > max(item.compress_size, 1) * 2000):
            archive.close()
            raise ValueError("Archive documentaire invalide ou trop volumineuse")
        names.add(item.filename)
    return archive


def _tesseract(explicit=None):
    candidates = [explicit, os.environ.get("TCA_TESSERACT_PATH"), shutil.which("tesseract"),
                  Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "TCA_BP/runtimes/tesseract/tesseract.exe",
                  Path(os.environ.get("ProgramFiles", "C:/Program Files")) / "Tesseract-OCR/tesseract.exe",
                  Path(__file__).resolve().parent / "vendor/tesseract/tesseract.exe"]
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return str(Path(candidate).resolve())
    return None


def _ocr(image, executable, timeout):
    if image.width * image.height > 24_000_000:
        raise ValueError("Image OCR supérieure à 24 millions de pixels")
    with tempfile.TemporaryDirectory(prefix="tca-ocr-") as directory:
        path = Path(directory) / "page.png"
        image.save(path)
        command = [executable, str(path), "stdout", "-l", "fra+eng", "--psm", "3", "tsv"]
        local_models = Path(executable).parent / "tessdata"
        if local_models.is_dir():
            command[3:3] = ["--tessdata-dir", str(local_models)]
        result = subprocess.run(command, capture_output=True, timeout=timeout,
                                encoding="utf-8", errors="replace", check=False,
                                creationflags=0x08000000 if os.name == "nt" else 0)
        if result.returncode:
            raise RuntimeError("OCR indisponible : Tesseract ou modèles fra+eng non opérationnels")
        lines = {}
        for row in csv.DictReader(io.StringIO(result.stdout), delimiter="\t"):
            if not row.get("text", "").strip():
                continue
            key = tuple(row.get(k) for k in ("page_num", "block_num", "par_num", "line_num"))
            try:
                confidence = max(0, min(100, float(row["conf"]))) / 100
            except (ValueError, KeyError):
                confidence = 0.0
            lines.setdefault(key, []).append((row["text"], confidence))
        return [(" ".join(w[0] for w in words), sum(w[1] for w in words) / len(words))
                for words in lines.values()]


def extract_document(path, numeric_locale="fr", *, tesseract_path=None,
                     max_pages=200, max_blocks=20000, max_bytes=MAX_FILE_BYTES,
                     ocr=True, ocr_timeout=45) -> dict:
    """Extract PDF, DOCX, PPTX, XLSX/XLSM, CSV/TXT and common local images.

``blocks`` preserve text and locations. ``facts`` are numeric proposals with
source SHA, method and confidence; none has authority or CONFIRME status.
Truncation, formula caches and OCR unavailability are explicit warnings.
DOCX pagination is unknown until rendered and is never fabricated.
"""
    if numeric_locale not in {"fr", "en"}:
        raise ValueError("numeric_locale doit être fr ou en")
    for name, value, ceiling in (("max_pages", max_pages, 1000), ("max_blocks", max_blocks, 100000),
                                  ("max_bytes", max_bytes, 200 * 1024 * 1024), ("ocr_timeout", ocr_timeout, 120)):
        if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= ceiling:
            raise ValueError(f"Limite {name} invalide")
    source = Path(path)
    if source.is_symlink() or not source.is_file() or source.stat().st_size > max_bytes:
        raise ValueError("Source régulière requise, dans la limite de taille")
    data = source.read_bytes()
    if len(data) > max_bytes:
        raise ValueError("Source trop volumineuse")
    digest = hashlib.sha256(data).hexdigest()
    blocks, facts, warnings = [], [], []
    executable = _tesseract(tesseract_path) if ocr else None

    def warn(code):
        if code not in warnings:
            warnings.append(code)

    def add(text, location, *, method="TEXT", confidence=1.0, typed=False, label=None, extra=None):
        text = str(text).strip()
        if not text:
            return
        if len(blocks) >= max_blocks:
            warn("EXTRACTION_TRONQUEE_MAX_BLOCKS")
            return
        if len(text) > 100000:
            text = text[:100000]
            warn("BLOC_TRONQUE")
        block_id = f"b{len(blocks) + 1:06d}"
        provenance = {"source_sha256": digest, "location": location, "method": method, "confidence": confidence}
        block = {"id": block_id, "text": text, "location": location,
                 "confidence": confidence, "provenance": provenance, "authority": "DATA_ONLY"}
        if extra:
            block.update(extra)
        blocks.append(block)
        if extra and extra.get("formula"):
            # Cached outputs cannot be presented as fresh input evidence.
            warn("FORMULES_CACHEES_NON_RECALCULEES")
        if extra and extra.get("excel_type") == "d":
            return  # An Excel date/clock serial is never a financial amount.
        dates = list(_DATE.finditer(text))
        matches = [None] if typed else _NUMBER.finditer(text)
        for match in matches:
            if len(facts) >= max_blocks:
                warn("EXTRACTION_TRONQUEE_MAX_FACTS")
                break
            if match and any(match.start() < date.end() and match.end() > date.start() for date in dates):
                continue
            raw = text if typed else match.group()
            parsed = parse_number(raw, numeric_locale, typed=typed)
            fact = {"id": f"f{len(facts) + 1:06d}", "block_id": block_id,
                    "label": str(label or text)[:500], **parsed, "period": None,
                    "location": location, "provenance": provenance, "confidence": confidence,
                    "requires_confirmation": True}
            if extra and extra.get("formula"):
                fact["cached_formula"] = extra["formula"]
                fact["freshness"] = "NON_VERIFIEE"
            facts.append(fact)

    suffix = source.suffix.lower()
    if suffix == ".pdf":
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(data))
        if reader.is_encrypted:
            raise ValueError("PDF chiffré non pris en charge")
        if len(reader.pages) > max_pages:
            warn("EXTRACTION_TRONQUEE_MAX_PAGES")
        pdfium = None
        try:
            for index, page in enumerate(reader.pages[:max_pages]):
                text = page.extract_text() or ""
                if len(re.sub(r"\s", "", text)) >= 20:
                    for line, content in enumerate(text.splitlines(), 1):
                        add(content, {"page": index + 1, "line": line})
                elif ocr and executable:
                    try:
                        import pypdfium2
                        if pdfium is None:
                            pdfium = pypdfium2.PdfDocument(data)
                        pdfpage = pdfium[index]
                        try:
                            if pdfpage.get_width() * pdfpage.get_height() * 4 > 24_000_000:
                                raise ValueError("Page OCR trop grande")
                            bitmap = pdfpage.render(scale=2)
                            try:
                                for line, (content, confidence) in enumerate(_ocr(bitmap.to_pil(), executable, ocr_timeout), 1):
                                    add(content, {"page": index + 1, "line": line}, method="OCR", confidence=confidence)
                            finally:
                                bitmap.close()
                        finally:
                            pdfpage.close()
                    except (ImportError, RuntimeError, subprocess.TimeoutExpired, ValueError):
                        warn(f"OCR_ECHEC_PAGE_{index + 1}")
                        add(text, {"page": index + 1}, method="TEXT_PARTIAL")
                else:
                    warn("OCR_REQUIS_INDISPONIBLE" if ocr else "OCR_DESACTIVE")
                    add(text, {"page": index + 1}, method="TEXT_PARTIAL")
        finally:
            if pdfium is not None:
                pdfium.close()
    elif suffix in {".docx", ".pptx", ".xlsx", ".xlsm"}:
        with _zip(data) as archive:
            if suffix == ".docx":
                members = ["word/document.xml"] + sorted(n for n in archive.namelist()
                    if re.fullmatch(r"word/(?:header\d+|footer\d+|footnotes|endnotes)\.xml", n))
                for member in members:
                    root = _xml(archive.read(member))
                    parents = {child: parent for parent in root.iter() for child in parent}
                    cells = {}
                    for table_index, table in enumerate(root.findall(".//w:tbl", _NS), 1):
                        for row_index, row in enumerate(table.findall("w:tr", _NS), 1):
                            for col_index, cell in enumerate(row.findall("w:tc", _NS), 1):
                                cells[cell] = {"table": table_index, "row": row_index, "column": col_index}
                    for i, paragraph in enumerate(root.findall(".//w:p", _NS), 1):
                        text = "".join(t.text or "" for t in paragraph.findall(".//w:t", _NS))
                        location = {"part": member, "paragraph": i, "page": None}
                        ancestor = paragraph
                        while ancestor in parents:
                            ancestor = parents[ancestor]
                            if ancestor in cells:
                                location.update(cells[ancestor])
                                break
                        add(text, location)
                warn("PAGINATION_DOCX_NON_DETERMINEE")
            elif suffix == ".pptx":
                # Presentation relationships define user-visible slide order.
                rels = _xml(archive.read("ppt/_rels/presentation.xml.rels"))
                targets = {r.get("Id"): r.get("Target") for r in rels if r.get("TargetMode") != "External"}
                pres = _xml(archive.read("ppt/presentation.xml"))
                ids = pres.findall(".//{http://schemas.openxmlformats.org/presentationml/2006/main}sldId")
                if len(ids) > max_pages:
                    warn("EXTRACTION_TRONQUEE_MAX_PAGES")
                for i, sid in enumerate(ids[:max_pages], 1):
                    target = targets[sid.get(f"{{{_NS['r']}}}id")]
                    member = target.lstrip("/") if target.startswith("/") else "ppt/" + target
                    root = _xml(archive.read(member))
                    for j, paragraph in enumerate(root.findall(".//a:p", _NS), 1):
                        add("".join(t.text or "" for t in paragraph.findall(".//a:t", _NS)), {"slide": i, "paragraph": j})
                    chart_ns = "http://schemas.openxmlformats.org/drawingml/2006/chart"
                    charts = root.findall(f".//{{{chart_ns}}}chart")
                    relation_name = posixpath.dirname(member) + "/_rels/" + posixpath.basename(member) + ".rels"
                    if charts and relation_name in archive.namelist():
                        relations = {r.get("Id"): r.get("Target") for r in _xml(archive.read(relation_name)) if r.get("TargetMode") != "External"}
                        for chart in charts:
                            target = relations.get(chart.get(f"{{{_NS['r']}}}id"))
                            if not target:
                                warn("GRAPHIQUE_PPTX_EXTERNE_NON_LU")
                                continue
                            part = target.lstrip("/") if target.startswith("/") else posixpath.normpath(posixpath.dirname(member) + "/" + target)
                            chart_root = _xml(archive.read(part))
                            cns = {"c": chart_ns}
                            for series_index, series in enumerate(chart_root.findall(".//c:ser", cns), 1):
                                series_name = series.find("c:tx//c:v", cns)
                                series_label = series_name.text if series_name is not None else f"Série {series_index}"
                                categories = {point.get("idx"): point.find("c:v", cns).text for point in series.findall("c:cat//c:pt", cns) if point.find("c:v", cns) is not None}
                                for point in series.findall("c:val//c:pt", cns):
                                    value = point.find("c:v", cns)
                                    if value is not None and value.text:
                                        add(value.text, {"slide": i, "chart": part, "series": series_index, "point": int(point.get("idx", 0)) + 1},
                                            typed=True, label=f"{series_label} | {categories.get(point.get('idx'), '')}",
                                            extra={"chart_cache": True})
                            warn("GRAPHIQUES_PPTX_CACHE_NON_RECALCULE")
                warn("IMAGES_PPTX_NON_OCRISEES")
            else:
                strings = []
                if "xl/sharedStrings.xml" in archive.namelist():
                    strings = ["".join(t.text or "" for t in s.findall(".//s:t", _NS))
                               for s in _xml(archive.read("xl/sharedStrings.xml"))]
                rels = _xml(archive.read("xl/_rels/workbook.xml.rels"))
                targets = {r.get("Id"): r.get("Target") for r in rels if r.get("TargetMode") != "External"}
                book = _xml(archive.read("xl/workbook.xml"))
                properties = book.find("s:workbookPr", _NS)
                date1904 = properties is not None and properties.get("date1904") in {"1", "true"}
                date_styles = set()
                if "xl/styles.xml" in archive.namelist():
                    style_root = _xml(archive.read("xl/styles.xml"))
                    formats = {int(f.get("numFmtId")): f.get("formatCode", "") for f in style_root.findall("s:numFmts/s:numFmt", _NS)}
                    for index, style in enumerate(style_root.findall("s:cellXfs/s:xf", _NS)):
                        fmt_id = int(style.get("numFmtId", 0))
                        fmt = re.sub(r'"[^\"]*"|\\.', "", formats.get(fmt_id, ""))
                        if fmt_id in set(range(14, 23)) | {45, 46, 47} or re.search(r"[ymdhHsS]", fmt):
                            date_styles.add(index)
                sheets = book.findall(".//s:sheet", _NS)
                if len(sheets) > max_pages:
                    warn("EXTRACTION_TRONQUEE_MAX_PAGES")
                for sheet in sheets[:max_pages]:
                    target = targets[sheet.get(f"{{{_NS['r']}}}id")]
                    member = target.lstrip("/") if target.startswith("/") else "xl/" + target
                    sheet_root = _xml(archive.read(member))
                    row_labels, col_labels = {}, {}
                    for cell in sheet_root.findall(".//s:sheetData/s:row/s:c", _NS):
                        val = cell.find("s:v", _NS)
                        formula = cell.find("s:f", _NS)
                        typ = cell.get("t", "n")
                        value = val.text if val is not None else ""
                        if typ == "s" and value:
                            value = strings[int(value)]
                        elif typ == "inlineStr":
                            value = "".join(t.text or "" for t in cell.findall(".//s:t", _NS))
                        elif typ in {"e", "b"}:
                            value = ""  # Errors and booleans are not monetary facts.
                        address = cell.get("r", "")
                        address_match = re.fullmatch(r"([A-Z]+)(\d+)", address)
                        column, row = address_match.groups() if address_match else ("", "")
                        if value and typ in {"s", "inlineStr", "str"}:
                            row_labels.setdefault(row, value)
                            col_labels.setdefault(column, value)
                        excel_date = None
                        if typ == "n" and value and int(cell.get("s", 0)) in date_styles:
                            try:
                                serial = Decimal(value)
                                if not date1904 and int(serial) == 60:
                                    excel_date = "1900-02-29 (jour fictif Excel)"
                                    warn("DATE_FICTIVE_EXCEL_1900")
                                else:
                                    adjusted = serial if date1904 or serial < 60 else serial - 1
                                    epoch = datetime(1904, 1, 1) if date1904 else datetime(1899, 12, 31)
                                    excel_date = (epoch + timedelta(days=float(adjusted))).isoformat()
                                value = excel_date
                                typ = "d"
                            except (ValueError, InvalidOperation, OverflowError):
                                warn("DATE_EXCEL_NON_INTERPRETABLE")
                        if formula is not None and not value:
                            warn("FORMULE_SANS_CACHE")
                        label = " | ".join(dict.fromkeys(str(v) for v in (sheet.get("name"), row_labels.get(row), col_labels.get(column)) if v))
                        add(value or "", {"sheet": sheet.get("name"), "cell": cell.get("r")}, label=label,
                            typed=typ == "n", extra={"formula": None if formula is None else "=" + (formula.text or ""),
                                                       "style_index": cell.get("s"), "excel_type": typ,
                                                       "excel_date": excel_date})
                warn("FORMATS_DATES_UNITES_EXCEL_A_CONFIRMER")
    elif suffix in {".csv", ".txt"}:
        try:
            text = data.decode("utf-8-sig")
        except UnicodeDecodeError:
            text = data.decode("cp1252")
            warn("ENCODAGE_CP1252_SUPPOSE")
        if suffix == ".txt":
            for index, line in enumerate(text.splitlines(), 1):
                add(line, {"line": index})
        else:
            try:
                dialect = csv.Sniffer().sniff(text[:8192], delimiters=";,\t|")
            except csv.Error:
                dialect = csv.excel
                warn("SEPARATEUR_CSV_NON_DETERMINE")
            rows = csv.reader(io.StringIO(text), dialect)
            headers = None
            for index, row in enumerate(rows, 1):
                if headers is None:
                    headers = row
                for col, value in enumerate(row, 1):
                    label = f"{headers[col - 1] if col <= len(headers) else col} : {value}"
                    add(value, {"row": index, "column": col}, label=label)
    elif suffix in {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".webp"}:
        if not executable:
            warn("OCR_REQUIS_INDISPONIBLE" if ocr else "OCR_DESACTIVE")
        else:
            from PIL import Image, ImageOps
            with Image.open(io.BytesIO(data)) as picture:
                frames = getattr(picture, "n_frames", 1)
                if frames > max_pages:
                    warn("EXTRACTION_TRONQUEE_MAX_PAGES")
                for index in range(min(frames, max_pages)):
                    picture.seek(index)
                    try:
                        corrected = ImageOps.exif_transpose(picture).convert("RGB")
                        for line, (content, confidence) in enumerate(_ocr(corrected, executable, ocr_timeout), 1):
                            add(content, {"page": index + 1, "line": line}, method="OCR", confidence=confidence)
                    except (RuntimeError, subprocess.TimeoutExpired, ValueError):
                        warn(f"OCR_ECHEC_PAGE_{index + 1}")
    else:
        raise ValueError("Format documentaire non pris en charge")
    if hashlib.sha256(source.read_bytes()).hexdigest() != digest:
        raise ValueError("La source a changé pendant l'extraction")
    return {"schema_version": "tca-document/1", "source_name": source.name,
            "source_sha256": digest, "numeric_locale": numeric_locale,
            "status": "PARTIAL" if warnings else "EXTRACTED", "blocks": blocks,
            "facts": facts, "warnings": warnings, "authority": "DATA_ONLY",
            "confirmation_required": True}
