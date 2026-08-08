import os
import sys
import traceback


def _fix_frozen_streams():
    # PyInstaller's --windowed mode has no console, so sys.stdout/stderr
    # are None. Anything that calls print() would crash without this.
    if sys.stdout is None:
        sys.stdout = open(os.devnull, "w")
    if sys.stderr is None:
        sys.stderr = open(os.devnull, "w")


def _log_crash(exc: BaseException):
    base_dir = os.path.dirname(sys.executable if getattr(sys, "frozen", False) else os.path.abspath(__file__))
    log_path = os.path.join(base_dir, "pyinvest_error.log")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write("".join(traceback.format_exception(type(exc), exc, exc.__traceback__)))


def main():
    _fix_frozen_streams()
    from ui.main_window import MainWindow

    app = MainWindow()
    app.mainloop()


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        _log_crash(exc)
        raise
