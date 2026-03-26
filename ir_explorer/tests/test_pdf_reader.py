# ir_explorer/tests/test_pdf_reader.py
import pytest
import os
from ir_explorer.core.pdf_reader import extract_simple, extract_sections


def _pymupdf_available():
    try:
        import fitz
        return True
    except ImportError:
        return False


def test_extract_simple_missing_file(tmp_path):
    with pytest.raises(Exception):
        extract_simple(str(tmp_path / "nonexistent.pdf"))


def test_extract_sections_missing_file(tmp_path):
    with pytest.raises(Exception):
        extract_sections(str(tmp_path / "nonexistent.pdf"))


@pytest.mark.skipif(not _pymupdf_available(), reason="PyMuPDF not installed")
def test_extract_simple_on_real_pdf():
    pdf_path = os.path.join(
        os.path.dirname(__file__), "..", "..", "the_multiverse_hierarchy_max_tegmark.pdf"
    )
    if not os.path.exists(pdf_path):
        pytest.skip("Test PDF not found")
    text = extract_simple(pdf_path)
    assert isinstance(text, str)
    assert len(text) > 100


@pytest.mark.skipif(not _pymupdf_available(), reason="PyMuPDF not installed")
def test_extract_sections_on_real_pdf():
    pdf_path = os.path.join(
        os.path.dirname(__file__), "..", "..", "the_multiverse_hierarchy_max_tegmark.pdf"
    )
    if not os.path.exists(pdf_path):
        pytest.skip("Test PDF not found")
    sections = extract_sections(pdf_path)
    assert isinstance(sections, list)
    assert len(sections) >= 1
    assert "title" in sections[0]
    assert "text" in sections[0]
