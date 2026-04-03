from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QPixmap
from PIL import Image
from src.cbr_extractor import get_cover_path, cleanup

THUMB_W = 88
THUMB_H = 110


class ThumbnailLoader(QThread):
    thumbnail_ready = pyqtSignal(QPixmap)

    def __init__(self, cbr_path: str):
        super().__init__()
        self.cbr_path = cbr_path

    def run(self):
        try:
            result = get_cover_path(self.cbr_path)
            if not result:
                return
            cover, temp_dir = result

            img = Image.open(cover)
            img.thumbnail((THUMB_W, THUMB_H), Image.LANCZOS)

            import os
            thumb_path = os.path.join(temp_dir, "_thumb.png")
            img.save(thumb_path)
            pixmap = QPixmap(thumb_path)

            cleanup(temp_dir)

            if not pixmap.isNull():
                self.thumbnail_ready.emit(pixmap)
        except Exception:
            pass  # Silently skip broken archives
