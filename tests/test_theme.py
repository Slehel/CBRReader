from PyQt6.QtWidgets import QApplication
from src.theme import ThemeManager, DARK, LIGHT


def test_theme_manager_defaults_to_dark():
    tm = ThemeManager()
    assert tm.is_dark is True


def test_toggle_flips_is_dark():
    tm = ThemeManager()
    tm.toggle()
    assert tm.is_dark is False
    tm.toggle()
    assert tm.is_dark is True


def test_toggle_label_dark_shows_sun():
    tm = ThemeManager()
    assert tm.toggle_label() == "☀"


def test_toggle_label_light_shows_moon():
    tm = ThemeManager()
    tm.toggle()
    assert tm.toggle_label() == "☾"


def test_apply_does_not_crash_with_qapp(qapp):
    tm = ThemeManager()
    tm.apply()  # should not raise


def test_toggle_does_not_crash_with_qapp(qapp):
    tm = ThemeManager()
    tm.toggle()  # should not raise
