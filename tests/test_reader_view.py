import os
import zipfile
from PIL import Image
from src.reader_view import ReaderView


def make_cbr(folder: str, num_pages: int = 5) -> str:
    cbr_path = os.path.join(folder, "comic.cbr")
    with zipfile.ZipFile(cbr_path, "w") as zf:
        for i in range(num_pages):
            img = Image.new("RGB", (200, 300), color=(i * 40, 100, 200))
            img_path = os.path.join(folder, f"p{i:03d}.png")
            img.save(img_path)
            zf.write(img_path, f"p{i:03d}.png")
    return cbr_path


def test_load_comic_sets_page_count(qapp, tmp_path):
    view = ReaderView(None)
    cbr = make_cbr(str(tmp_path), num_pages=5)
    view.load_comic(cbr)
    assert view.total_pages == 5


def test_initial_page_is_zero(qapp, tmp_path):
    view = ReaderView(None)
    cbr = make_cbr(str(tmp_path))
    view.load_comic(cbr)
    assert view.current_page == 0


def test_next_page_increments(qapp, tmp_path):
    view = ReaderView(None)
    cbr = make_cbr(str(tmp_path))
    view.load_comic(cbr)
    view.next_page()
    assert view.current_page == 1


def test_prev_page_decrements(qapp, tmp_path):
    view = ReaderView(None)
    cbr = make_cbr(str(tmp_path))
    view.load_comic(cbr)
    view.next_page()
    view.prev_page()
    assert view.current_page == 0


def test_next_page_does_not_go_past_end(qapp, tmp_path):
    view = ReaderView(None)
    cbr = make_cbr(str(tmp_path), num_pages=2)
    view.load_comic(cbr)
    view.next_page()
    view.next_page()  # should clamp
    assert view.current_page == 1


def test_prev_page_does_not_go_below_zero(qapp, tmp_path):
    view = ReaderView(None)
    cbr = make_cbr(str(tmp_path))
    view.load_comic(cbr)
    view.prev_page()  # should clamp
    assert view.current_page == 0
