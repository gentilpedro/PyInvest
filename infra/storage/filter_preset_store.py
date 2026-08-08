import json
import os
from dataclasses import asdict
from pathlib import Path

from app.domain.filters.fii_filter import FiiFilterCriteria


class FilterPresetStore:
    """Persists named FiiFilterCriteria presets as JSON in the user's app data folder."""

    def __init__(self, path: Path | None = None):
        self.path = path or self._default_path()

    def _default_path(self) -> Path:
        base = Path(os.environ.get("APPDATA", Path.home())) / "PyInvest"
        base.mkdir(parents=True, exist_ok=True)
        return base / "filter_presets.json"

    def list_names(self) -> list[str]:
        return sorted(self._read_all().keys())

    def save(self, name: str, criteria: FiiFilterCriteria):
        presets = self._read_all()
        presets[name] = asdict(criteria)
        self._write_all(presets)

    def load(self, name: str) -> FiiFilterCriteria:
        presets = self._read_all()
        return FiiFilterCriteria(**presets[name])

    def delete(self, name: str):
        presets = self._read_all()
        presets.pop(name, None)
        self._write_all(presets)

    def _read_all(self) -> dict:
        if not self.path.exists():
            return {}
        with open(self.path, encoding="utf-8") as f:
            return json.load(f)

    def _write_all(self, presets: dict):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(presets, f, ensure_ascii=False, indent=2)
