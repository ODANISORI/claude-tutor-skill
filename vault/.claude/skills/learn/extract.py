#!/usr/bin/env python3
"""Extract readable text from study files that Claude's Read tool can't open directly.

Usage:  python3 -I .claude/skills/learn/extract.py <file> [--max-chars N]

Handles: .docx .pptx .xlsx .odt .odp .ods .epub .html .htm .xhtml .rtf .doc
Standard library only (plus macOS `textutil` for .rtf/.doc). Prints plain text with
section markers such as "=== Slide 3 ===" so notes can cite where things came from.
PDF, images, .ipynb, .md, .txt, code and .csv: use the Read tool instead.
"""
import html
import re
import subprocess
import sys
import zipfile
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path

NS = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "text": "urn:oasis:names:tc:opendocument:xmlns:text:1.0",
    "table": "urn:oasis:names:tc:opendocument:xmlns:table:1.0",
    "draw": "urn:oasis:names:tc:opendocument:xmlns:drawing:1.0",
}
MAX_XML = 50_000_000  # refuse absurdly large zip members


def read_xml(z, name):
    info = z.getinfo(name)
    if info.file_size > MAX_XML:
        raise ValueError(f"{name} is too large to parse safely")
    return ET.fromstring(z.read(name))


def natural_key(name):
    return [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", name)]


def para_text(p, ns):
    """Text of one paragraph, keeping line breaks, tabs and indentation."""
    t_tag, br_tag, tab_tag = (f"{{{NS[ns]}}}{x}" for x in ("t", "br", "tab"))
    parts = []
    for el in p.iter():
        if el.tag == t_tag:
            parts.append(el.text or "")
        elif el.tag == br_tag:
            parts.append("\n")
        elif el.tag == tab_tag and ns == "w":
            parts.append("\t")
    return "".join(parts).rstrip()


def docx(z):
    root = read_xml(z, "word/document.xml")
    out = []
    for p in root.iter(f"{{{NS['w']}}}p"):
        style = p.find("w:pPr/w:pStyle", NS)
        text = para_text(p, "w")
        if not text.strip():
            continue
        sval = style.get(f"{{{NS['w']}}}val", "") if style is not None else ""
        m = re.match(r"Heading(\d)", sval)
        out.append(("#" * int(m.group(1)) + " " if m else "") + text)
    return "\n".join(out)


def pptx(z):
    slides = sorted(
        (n for n in z.namelist() if re.fullmatch(r"ppt/slides/slide\d+\.xml", n)),
        key=natural_key,
    )
    out = []
    for name in slides:
        i = int(re.search(r"(\d+)\.xml$", name).group(1))
        root = read_xml(z, name)
        paras = []
        for p in root.iter(f"{{{NS['a']}}}p"):
            t = para_text(p, "a")
            if t.strip():
                paras.append(t)
        out.append(f"=== Slide {i} ===")
        out.extend(paras)
        notes = f"ppt/notesSlides/notesSlide{i}.xml"
        if notes in z.namelist():
            nroot = read_xml(z, notes)
            ntext = " ".join(
                (x.text or "").strip() for x in nroot.iter(f"{{{NS['a']}}}t")
            ).strip()
            # notes slides repeat the slide number as text; drop a bare number
            if ntext and not ntext.isdigit():
                out.append(f"[Speaker notes] {ntext}")
    return "\n".join(out)


def xlsx(z):
    shared = []
    if "xl/sharedStrings.xml" in z.namelist():
        for si in read_xml(z, "xl/sharedStrings.xml").findall("s:si", NS):
            shared.append("".join(t.text or "" for t in si.iter(f"{{{NS['s']}}}t")))
    names = {}
    if "xl/workbook.xml" in z.namelist():
        for i, sh in enumerate(read_xml(z, "xl/workbook.xml").iter(f"{{{NS['s']}}}sheet"), 1):
            names[i] = sh.get("name")
    sheets = sorted(
        (n for n in z.namelist() if re.fullmatch(r"xl/worksheets/sheet\d+\.xml", n)),
        key=natural_key,
    )
    out = []
    for name in sheets:
        idx = int(re.search(r"(\d+)\.xml$", name).group(1))
        out.append(f"=== Sheet: {names.get(idx, idx)} ===")
        for row in read_xml(z, name).iter(f"{{{NS['s']}}}row"):
            cells = []
            for c in row.findall("s:c", NS):
                v = c.find("s:v", NS)
                t = c.get("t")
                if t == "s" and v is not None:
                    cells.append(shared[int(v.text)])
                elif t == "inlineStr":
                    cells.append("".join(x.text or "" for x in c.iter(f"{{{NS['s']}}}t")))
                else:
                    cells.append(v.text if v is not None and v.text else "")
            if any(cells):
                out.append(" | ".join(cells))
    return "\n".join(out)


def odf(z):
    root = read_xml(z, "content.xml")
    out = []
    pages = root.findall(f".//{{{NS['draw']}}}page")
    tables = root.findall(f".//{{{NS['table']}}}table")
    if pages:  # presentation
        for i, page in enumerate(pages, 1):
            out.append(f"=== Slide {i} ===")
            for p in page.iter():
                if p.tag in (f"{{{NS['text']}}}p", f"{{{NS['text']}}}h"):
                    t = "".join(p.itertext()).strip()
                    if t:
                        out.append(t)
        return "\n".join(out)
    if tables and root.find(f".//{{{NS['text']}}}h") is None:  # spreadsheet
        name_attr = "{%s}name" % NS["table"]
        for tb in tables:
            out.append(f"=== Sheet: {tb.get(name_attr)} ===")
            for row in tb.iter(f"{{{NS['table']}}}table-row"):
                cells = ["".join(c.itertext()).strip() for c in row.findall(f"{{{NS['table']}}}table-cell")]
                if any(cells):
                    out.append(" | ".join(cells))
        return "\n".join(out)
    for el in root.iter():
        if el.tag == f"{{{NS['text']}}}h":
            lvl = int(el.get(f"{{{NS['text']}}}outline-level", "1"))
            out.append("#" * lvl + " " + "".join(el.itertext()).strip())
        elif el.tag == f"{{{NS['text']}}}p":
            t = "".join(el.itertext()).strip()
            if t:
                out.append(t)
    return "\n".join(out)


class _Text(HTMLParser):
    SKIP = {"script", "style", "nav", "head"}
    BLOCK = {"p", "div", "br", "li", "tr", "h1", "h2", "h3", "h4", "h5", "h6", "section"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts, self.skip = [], 0

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP:
            self.skip += 1
        elif tag in self.BLOCK:
            self.parts.append("\n")
            if re.fullmatch(r"h[1-6]", tag):
                self.parts.append("#" * int(tag[1]) + " ")

    def handle_endtag(self, tag):
        if tag in self.SKIP and self.skip:
            self.skip -= 1
        elif tag in self.BLOCK:
            self.parts.append("\n")

    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)


def html_to_text(raw):
    p = _Text()
    p.feed(raw)
    text = html.unescape("".join(p.parts))
    return re.sub(r"\n\s*\n+", "\n\n", text).strip()


def epub(z):
    # order chapters by the OPF spine when available
    opf = next((n for n in z.namelist() if n.endswith(".opf")), None)
    order = []
    if opf:
        root = read_xml(z, opf)
        base = str(Path(opf).parent)
        items = {i.get("id"): i.get("href") for i in root.iter() if i.tag.endswith("item")}
        for ref in root.iter():
            if ref.tag.endswith("itemref") and ref.get("idref") in items:
                href = items[ref.get("idref")]
                order.append(href if base in ("", ".") else f"{base}/{href}")
    if not order:
        order = sorted((n for n in z.namelist() if n.endswith((".xhtml", ".html", ".htm"))), key=natural_key)
    out = []
    for i, name in enumerate(order, 1):
        if name not in z.namelist():
            continue
        text = html_to_text(z.read(name).decode("utf-8", "replace"))
        if text:
            out.append(f"=== Chapter file {i}: {Path(name).name} ===\n{text}")
    return "\n\n".join(out)


def textutil(path):
    res = subprocess.run(
        ["/usr/bin/textutil", "-convert", "txt", "-stdout", str(path)],
        capture_output=True, text=True, timeout=120,
    )
    if res.returncode != 0:
        raise RuntimeError(res.stderr.strip() or "textutil failed")
    return res.stdout


ZIP_HANDLERS = {".docx": docx, ".pptx": pptx, ".xlsx": xlsx,
                ".odt": odf, ".odp": odf, ".ods": odf, ".epub": epub}


def extract(path):
    ext = path.suffix.lower()
    if ext in ZIP_HANDLERS:
        with zipfile.ZipFile(path) as z:
            return ZIP_HANDLERS[ext](z)
    if ext in (".html", ".htm", ".xhtml"):
        return html_to_text(path.read_text("utf-8", "replace"))
    if ext in (".rtf", ".doc", ".webarchive"):
        return textutil(path)
    if ext in (".key", ".pages", ".numbers"):
        raise ValueError("Apple iWork files can't be read. Export to PDF (File > Export To > PDF) and use that.")
    raise ValueError(f"No extractor for {ext}. Try the Read tool, or export the file to PDF.")


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(2)
    max_chars = None
    if "--max-chars" in args:
        i = args.index("--max-chars")
        max_chars = int(args[i + 1])
        del args[i:i + 2]
    path = Path(args[0]).expanduser()
    if not path.is_file():
        sys.exit(f"Not a file: {path}")
    try:
        text = extract(path)
    except Exception as e:  # report cleanly to the caller
        sys.exit(f"Could not extract {path.name}: {e}")
    if not text.strip():
        sys.exit(f"{path.name}: no text found (it may be scanned images; export pages as images or PDF and use Read).")
    total = len(text)
    if max_chars and total > max_chars:
        text = text[:max_chars] + f"\n\n[... truncated at {max_chars} of {total} characters; rerun without --max-chars or read in parts ...]"
    print(f"[{path.name} · {total} characters]\n")
    print(text)


if __name__ == "__main__":
    main()
