from src.main_window import MainWindow


def test_main_window_shows_library_view_on_start(qapp):
    window = MainWindow()
    assert window.stack.currentIndex() == 0  # LibraryView is index 0


def test_main_window_can_switch_to_reader(qapp, tmp_path):
    from PIL import Image
    import zipfile, os
    # make a tiny fake cbr
    cbr = str(tmp_path / "test.cbr")
    img = Image.new("RGB", (10, 10), color=(255, 0, 0))
    img_path = str(tmp_path / "p001.png")
    img.save(img_path)
    with zipfile.ZipFile(cbr, "w") as zf:
        zf.write(img_path, "p001.png")

    window = MainWindow()
    window.show_reader(cbr)
    assert window.stack.currentIndex() == 1  # ReaderView is index 1


def test_main_window_can_go_back_to_library(qapp, tmp_path):
    from PIL import Image
    import zipfile
    cbr = str(tmp_path / "test.cbr")
    img = Image.new("RGB", (10, 10))
    img_path = str(tmp_path / "p001.png")
    img.save(img_path)
    with zipfile.ZipFile(cbr, "w") as zf:
        zf.write(img_path, "p001.png")

    window = MainWindow()
    window.show_reader(cbr)
    window.show_library()
    assert window.stack.currentIndex() == 0
