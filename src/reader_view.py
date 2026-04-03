from PyQt6.QtWidgets import QWidget


class ReaderView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._pages: list[str] = []
        self._temp_dir: str | None = None

    def load_comic(self, cbr_path: str) -> None:
        from src.cbr_extractor import extract_cbr
        self.cleanup()
        self._pages = extract_cbr(cbr_path)
        if self._pages:
            import os
            self._temp_dir = os.path.dirname(self._pages[0])

    def cleanup(self) -> None:
        if self._temp_dir:
            from src.cbr_extractor import cleanup
            cleanup(self._temp_dir)
            self._temp_dir = None
        self._pages = []
