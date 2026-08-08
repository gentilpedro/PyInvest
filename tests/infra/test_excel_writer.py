import pandas as pd

from infra.writers.excel_writer import ExcelWriter


def test_save_as_creates_file_with_expected_content(tmp_path):
    df = pd.DataFrame({"a": [1, 2], "b": ["x", "y"]})
    path = tmp_path / "nested" / "out.xlsx"

    ExcelWriter().save_as(df, path)

    assert path.exists()
    result = pd.read_excel(path)
    assert result["a"].tolist() == [1, 2]
    assert result["b"].tolist() == ["x", "y"]


def test_save_writes_into_output_directory(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    df = pd.DataFrame({"a": [1]})

    ExcelWriter().save(df, "test.xlsx")

    assert (tmp_path / "output" / "test.xlsx").exists()
