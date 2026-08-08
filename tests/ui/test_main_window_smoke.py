from ui.main_window import MainWindow


def test_main_window_can_be_built_and_destroyed():
    window = MainWindow()
    try:
        window.update()
        assert window.winfo_exists()
    finally:
        window.destroy()
