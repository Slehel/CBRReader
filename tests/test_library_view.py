import os
import zipfile
from PIL import Image
from src.library_view import LibraryView


def make_cbr(folder: str, name: str) -> str:
    cbr_path = os.path.join(folder, name)
    img = Image.new("RGB", (100, 150), color=(100, 100, 200))
    img_path = os.path.join(folder, "p.png")
    img.save(img_path)
    with zipfile.ZipFile(cbr_path, "w") as zf:
        zf.write(img_path, "p.png")
    return cbr_path


def test_scan_folder_finds_cbr_files(qapp, tmp_path):
    make_cbr(str(tmp_path), "comic1.cbr")
    make_cbr(str(tmp_path), "comic2.cbr")
    view = LibraryView(None)
    files = view.scan_folder(str(tmp_path))
    assert len(files) == 2
    assert all(f.endswith(".cbr") for f in files)


def test_scan_folder_ignores_non_cbr(qapp, tmp_path):
    make_cbr(str(tmp_path), "comic1.cbr")
    open(os.path.join(str(tmp_path), "readme.txt"), "w").close()
    view = LibraryView(None)
    files = view.scan_folder(str(tmp_path))
    assert len(files) == 1


def test_status_label_updates_after_scan(qapp, tmp_path):
    make_cbr(str(tmp_path), "comic1.cbr")
    make_cbr(str(tmp_path), "comic2.cbr")
    view = LibraryView(None)
    view.load_folder(str(tmp_path))
    assert "2" in view.status_label.text()
    view.close()  # ensures background loader threads are joined before GC
