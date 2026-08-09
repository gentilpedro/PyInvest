import pytest

from app.domain.filters.fii_filter import FiiFilterCriteria
from app.domain.filters.stock_filter import StockFilterCriteria
from infra.storage.filter_preset_store import FilterPresetStore


@pytest.fixture
def store(tmp_path):
    return FilterPresetStore(FiiFilterCriteria, path=tmp_path / "presets.json")


def test_list_names_starts_empty(store):
    assert store.list_names() == []


def test_save_then_load_roundtrips_criteria(store):
    criteria = FiiFilterCriteria(dy_min=8.5, pvp_max=1.0, segmento="Shoppings", ticker="hglg")
    store.save("Meu preset", criteria)

    assert store.load("Meu preset") == criteria


def test_save_persists_across_new_store_instances(tmp_path):
    path = tmp_path / "presets.json"
    FilterPresetStore(FiiFilterCriteria, path=path).save("A", FiiFilterCriteria(dy_min=5))

    reloaded = FilterPresetStore(FiiFilterCriteria, path=path)
    assert reloaded.list_names() == ["A"]
    assert reloaded.load("A").dy_min == 5


def test_list_names_is_sorted(store):
    store.save("Zebra", FiiFilterCriteria())
    store.save("Alpha", FiiFilterCriteria())

    assert store.list_names() == ["Alpha", "Zebra"]


def test_delete_removes_preset(store):
    store.save("Temp", FiiFilterCriteria())
    store.delete("Temp")

    assert store.list_names() == []


def test_delete_missing_preset_does_not_raise(store):
    store.delete("does-not-exist")


def test_save_overwrites_existing_preset_with_same_name(store):
    store.save("Preset", FiiFilterCriteria(dy_min=1))
    store.save("Preset", FiiFilterCriteria(dy_min=99))

    assert store.load("Preset").dy_min == 99
    assert store.list_names() == ["Preset"]


def test_works_with_stock_filter_criteria_too(tmp_path):
    store = FilterPresetStore(StockFilterCriteria, path=tmp_path / "stock_presets.json")
    criteria = StockFilterCriteria(roe_min=15, pl_max=12, ticker="petr")

    store.save("Blue chips", criteria)

    assert store.load("Blue chips") == criteria


def test_fii_and_stock_stores_are_independent(tmp_path):
    fii_store = FilterPresetStore(FiiFilterCriteria, filename="fii.json", path=tmp_path / "fii.json")
    stock_store = FilterPresetStore(StockFilterCriteria, filename="stock.json", path=tmp_path / "stock.json")

    fii_store.save("Meu preset", FiiFilterCriteria(dy_min=8))
    stock_store.save("Meu preset", StockFilterCriteria(dy_min=3))

    assert fii_store.load("Meu preset").dy_min == 8
    assert stock_store.load("Meu preset").dy_min == 3
