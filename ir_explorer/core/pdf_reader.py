"""PDF text extraction: simple (whole doc) and section-level splitting."""

import re

# font name patterns that indicate bold weight
_BOLD_PATTERNS = re.compile(
    r"Bold|BOLD|\.B$|\.B[,\s]|-B$|-Bd|-Bold|BX\d|Demi|Heavy|Black",
    re.IGNORECASE,
)


def _is_bold_font(font_name, flags):
    """Check if a span is bold via flags OR font name."""
    if flags & (1 << 4):
        return True
    if _BOLD_PATTERNS.search(font_name):
        return True
    return False


def extract_simple(path):
    import fitz
    doc = fitz.open(path)
    pages = [page.get_text() for page in doc]
    doc.close()
    return "\n".join(pages)


def extract_sections(path, min_length=100, split_on="titles"):
    """Extract text split into sections.

    split_on:
        "titles"    — split on major headings (large font or bold+uppercase)
        "subtitles" — split on titles AND subtitles (bold at body size too)
    """
    import fitz
    doc = fitz.open(path)

    blocks = []
    for page in doc:
        page_dict = page.get_text("dict")
        for block in page_dict.get("blocks", []):
            if block.get("type") != 0:
                continue
            for line in block.get("lines", []):
                text = ""
                max_size = 0
                bold = False
                for span in line.get("spans", []):
                    text += span.get("text", "")
                    max_size = max(max_size, span.get("size", 0))
                    font = span.get("font", "")
                    flags = span.get("flags", 0)
                    if _is_bold_font(font, flags):
                        bold = True
                text = text.strip()
                if text:
                    blocks.append({
                        "text": text,
                        "size": max_size,
                        "bold": bold,
                    })
    doc.close()

    if not blocks:
        return [{"title": "Full Document", "text": extract_simple(path)}]

    # find body size (most common)
    size_counts = {}
    for b in blocks:
        s = round(b["size"], 1)
        size_counts[s] = size_counts.get(s, 0) + 1
    body_size = max(size_counts, key=size_counts.get)

    def _looks_like_heading(b):
        """Strict: numbered section headings, uppercase titles, or larger font."""
        txt = b["text"]
        if len(txt) > 200:
            return False
        # clearly larger font
        if b["size"] > body_size + 1.5:
            return True
        if not b["bold"]:
            return False
        # standalone roman numeral: "I.", "II.", "IV." etc.
        if re.match(r"^[IVXLC]+\.$", txt.strip()):
            return True
        # numbered heading with text: "I. TITLE", "1. Title"
        if re.match(r"^[IVXLC]+\.\s", txt):
            return True
        if re.match(r"^\d+[\.\)]\s", txt):
            return True
        # bold ALL-CAPS line with enough words (like "LEVEL I: REGIONS BEYOND OUR COSMIC")
        alpha = [c for c in txt if c.isalpha()]
        words = txt.split()
        if len(alpha) > 10 and len(words) >= 3 and all(c.isupper() for c in alpha) and len(txt) < 80:
            return True
        return False

    def _looks_like_subtitle(b):
        """Moderate: numbered headings + bold titled lines (not bullets/refs)."""
        txt = b["text"]
        if len(txt) > 150:
            return False
        # larger font always counts
        if b["size"] > body_size + 0.5:
            return True
        if not b["bold"]:
            return False
        # skip bullet points
        if txt.startswith("•") or txt.startswith("-"):
            return False
        # skip references (author, year pattern)
        if re.match(r"^[A-Z][a-z]+,\s[A-Z]", txt):
            return False
        # skip lines that are ALL CAPS and very short (likely figure labels)
        alpha = [c for c in txt if c.isalpha()]
        if alpha and all(c.isupper() for c in alpha) and len(txt) < 25:
            return False
        # numbered heading
        if re.match(r"^[IVXLC]+\.\s|^\d+[\.\)]\s|^[A-Z][\.\)]\s", txt):
            return True
        # capitalized bold line that reads like a title (first word capitalized, not a sentence fragment)
        if txt[0].isupper() and len(txt) < 80 and not txt.endswith(",") and not txt.endswith("-"):
            return True
        return False

    if split_on == "subtitles":
        is_heading = _looks_like_subtitle
    else:
        is_heading = _looks_like_heading

    sections = []
    current_title = "Introduction"
    current_text = []

    for b in blocks:
        if is_heading(b):
            if current_text:
                joined = " ".join(current_text)
                if len(joined) >= min_length:
                    sections.append({"title": current_title, "text": joined})
            current_title = b["text"]
            current_text = []
        else:
            current_text.append(b["text"])

    if current_text:
        joined = " ".join(current_text)
        if len(joined) >= min_length:
            sections.append({"title": current_title, "text": joined})

    if not sections:
        return _split_by_paragraphs(path, min_length)

    return sections


def _split_by_paragraphs(path, min_length=100):
    full_text = extract_simple(path)
    paragraphs = re.split(r"\n\s*\n", full_text)
    sections = []
    for i, para in enumerate(paragraphs):
        para = para.strip()
        if len(para) >= min_length:
            sections.append({"title": f"Section {i+1}", "text": para})

    if not sections:
        sections = [{"title": "Full Document", "text": full_text}]

    return sections
