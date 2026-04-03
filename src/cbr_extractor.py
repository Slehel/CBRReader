import os
import shutil
import sys
import tempfile
import zipfile

import rarfile

# Prefer explicit env var, then auto-detect WinRAR on Windows
_unrar = os.environ.get("UNRAR_TOOL")
if not _unrar and sys.platform == "win32":
    _candidates = [
        r"C:\Program Files\WinRAR\UnRAR.exe",
        r"C:\Program Files (x86)\WinRAR\UnRAR.exe",
    ]
    for _path in _candidates:
        if os.path.isfile(_path):
            _unrar = _path
            break
if _unrar:
    rarfile.UNRAR_TOOL = _unrar
    print(f"[EXTRACTOR] Using unrar tool: {_unrar}")
else:
    print("[EXTRACTOR] Warning: no unrar tool found — .cbr (RAR) files will fail")

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

    return sorted(pages, key=lambda p: os.path.basename(p))


def get_cover_path(cbr_path: str) -> tuple[str, str] | None:
    """Extract only the first page of a CBR.

    Returns (cover_path, temp_dir) tuple, or None if no pages found.
    Caller is responsible for calling cleanup(temp_dir) when done.
    """
    pages = extract_cbr(cbr_path)
    if not pages:
        return None
    cover = pages[0]
    temp_dir = os.path.dirname(cover)
    # Walk up to find the cbr_ temp root if cover is in a subdirectory
    while not os.path.basename(temp_dir).startswith("cbr_"):
        parent = os.path.dirname(temp_dir)
        if parent == temp_dir:  # reached filesystem root
            break
        temp_dir = parent
    for p in pages[1:]:
        try:
            os.remove(p)
        except OSError:
            pass
    return cover, temp_dir


def cleanup(temp_dir: str) -> None:
    """Remove a temp directory created by extract_cbr."""
    shutil.rmtree(temp_dir, ignore_errors=True)
