import json
import os
from dataclasses import asdict
from pathlib import Path
from typing import Type, TypeVar

CriteriaT = TypeVar("CriteriaT")


class FilterPresetStore:
    """Persists named filter-criteria presets as JSON in the user's app data folder.

    Works with any dataclass (FiiFilterCriteria, StockFilterCriteria, ...);
    pass the class so `load()` knows how to reconstruct it.
    """

    def __init__(self, criteria_cls: Type[CriteriaT], filename: str = "filter_presets.json", path: Path | None = None):
        self.criteria_cls = criteria_cls
        self.path = path or self._default_path(filename)

    def _default_path(self, filename: str) -> Path:
        base = Path(os.environ.get("APPDATA", Path.home())) / "PyInvest"
        base.mkdir(parents=True, exist_ok=True)
        return base / filename

    def list_names(self) -> list[str]:
        return sorted(self._read_all().keys())

    def save(self, name: str, criteria: CriteriaT):
        presets = self._read_all()
        presets[name] = asdict(criteria)
        self._write_all(presets)

    def load(self, name: str) -> CriteriaT:
        presets = self._read_all()
        return self.criteria_cls(**presets[name])

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
