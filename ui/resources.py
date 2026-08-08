import sys
from pathlib import Path


def resource_path(relative: str) -> Path:
    """Resolves a path to a bundled asset, both in dev and in a frozen PyInstaller build."""
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent))
    return base / relative
