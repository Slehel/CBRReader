import os
import shutil
import tempfile
import zipfile

import rarfile

rarfile.UNRAR_TOOL = "/mnt/c/Program Files/WinRAR/UnRAR.exe"

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"}


def _is_image(filename: str) -> bool:
    return os.path.splitext(filename.lower())[1] in IMAGE_EXTENSIONS


def extract_cbr(cbr_path: str) -> list[str]:
    """Extract all pages from a CBR file to a temp dir. Returns sorted image paths."""
    temp_dir = tempfile.mkdtemp(prefix="cbr_")
    try:
        if zipfile.is_zipfile(cbr_path):
            with zipfile.ZipFile(cbr_path, "r") as zf:
                zf.extractall(temp_dir)
        else:
            with rarfile.RarFile(cbr_path, "r") as rf:
                rf.extractall(temp_dir)
    except Exception as e:
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise RuntimeError(f"Failed to extract {cbr_path}: {e}") from e

    pages = []
    for root, _, files in os.walk(temp_dir):
        for f in files:
            if _is_image(f):
                pages.append(os.path.join(root, f))

    return sorted(pages)


def get_cover_path(cbr_path: str) -> str | None:
    """Extract only the first page of a CBR and return its path."""
    pages = extract_cbr(cbr_path)
    if not pages:
        return None
    cover = pages[0]
    for p in pages[1:]:
        try:
            os.remove(p)
        except OSError:
            pass
    return cover


def cleanup(temp_dir: str) -> None:
    """Remove a temp directory created by extract_cbr."""
    shutil.rmtree(temp_dir, ignore_errors=True)
