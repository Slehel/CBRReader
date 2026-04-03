import os
import tempfile
import zipfile
import pytest
from PIL import Image
from src.cbr_extractor import extract_cbr, get_cover_path, cleanup


def make_fake_cbr(path: str, num_pages: int = 3) -> str:
    """Creates a fake .cbr (actually a zip) with PNG pages for testing."""
    cbr_path = os.path.join(path, "test.cbr")
    with zipfile.ZipFile(cbr_path, "w") as zf:
        for i in range(num_pages):
            img = Image.new("RGB", (100, 150), color=(i * 80, 100, 200))
            img_path = os.path.join(path, f"page_{i:03d}.png")
            img.save(img_path)
            zf.write(img_path, f"page_{i:03d}.png")
    return cbr_path


def test_extract_cbr_returns_sorted_image_paths(tmp_path):
    cbr = make_fake_cbr(str(tmp_path))
    pages = extract_cbr(str(cbr))
    assert len(pages) == 3
    assert all(p.endswith(".png") for p in pages)
    assert pages == sorted(pages)


def test_extract_cbr_files_exist_on_disk(tmp_path):
    cbr = make_fake_cbr(str(tmp_path))
    pages = extract_cbr(str(cbr))
    for p in pages:
        assert os.path.isfile(p)


def test_get_cover_path_returns_first_page(tmp_path):
    cbr = make_fake_cbr(str(tmp_path))
    cover = get_cover_path(str(cbr))
    assert cover is not None
    assert os.path.isfile(cover)


def test_cleanup_removes_temp_dir(tmp_path):
    cbr = make_fake_cbr(str(tmp_path))
    pages = extract_cbr(str(cbr))
    temp_dir = os.path.dirname(pages[0])
    cleanup(temp_dir)
    assert not os.path.exists(temp_dir)
