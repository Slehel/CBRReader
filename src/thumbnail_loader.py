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
        import os
        print(f"[THUMB] starting: {os.path.basename(self.cbr_path)}")
        try:
            result = get_cover_path(self.cbr_path)
            if not result:
                print(f"[THUMB] get_cover_path returned None for {self.cbr_path}")
                return
            cover, temp_dir = result
            print(f"[THUMB] cover extracted: {cover}")

            img = Image.open(cover)
            img.thumbnail((THUMB_W, THUMB_H), Image.LANCZOS)

            thumb_path = os.path.join(temp_dir, "_thumb.png")
            img.save(thumb_path)
            print(f"[THUMB] thumb saved: {thumb_path}")

            pixmap = QPixmap(thumb_path)
            print(f"[THUMB] pixmap null={pixmap.isNull()} size={pixmap.size()}")

            cleanup(temp_dir)

            if not pixmap.isNull():
                self.thumbnail_ready.emit(pixmap)
                print(f"[THUMB] signal emitted for {os.path.basename(self.cbr_path)}")
            else:
                print(f"[THUMB] pixmap was null, not emitting")
        except Exception as e:
            print(f"[THUMB ERROR] {self.cbr_path}: {e}")
