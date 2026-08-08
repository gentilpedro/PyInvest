import pytest

from app.domain.filters.fii_filter import FiiFilterCriteria
from infra.storage.filter_preset_store import FilterPresetStore


@pytest.fixture
def store(tmp_path):
    return FilterPresetStore(path=tmp_path / "presets.json")


def test_list_names_starts_empty(store):
    assert store.list_names() == []


def test_save_then_load_roundtrips_criteria(store):
    criteria = FiiFilterCriteria(dy_min=8.5, pvp_max=1.0, segmento="Shoppings", ticker="hglg")
    store.save("Meu preset", criteria)

    assert store.load("Meu preset") == criteria


def test_save_persists_across_new_store_instances(tmp_path):
    path = tmp_path / "presets.json"
    FilterPresetStore(path=path).save("A", FiiFilterCriteria(dy_min=5))

    reloaded = FilterPresetStore(path=path)
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
