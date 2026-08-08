import pandas as pd

from infra.external.fundamentus.fundamentus_client import FundamentusClient


def test_clean_converts_percent_strings_to_float():
    df = pd.DataFrame({"Papel": ["AAAA11"], "Dividend Yield": ["8,79%"]})

    result = FundamentusClient()._clean(df, ["Dividend Yield"])

    assert result["Dividend Yield"].iloc[0] == 8.79
    assert pd.api.types.is_float_dtype(result["Dividend Yield"])


def test_clean_handles_negative_percent_values():
    df = pd.DataFrame({"Papel": ["AAAA11"], "Cap Rate": ["-30,24%"]})

    result = FundamentusClient()._clean(df, ["Cap Rate"])

    assert result["Cap Rate"].iloc[0] == -30.24


def test_clean_coerces_leftover_text_numeric_columns_to_float():
    # Reproduces a real pandas.read_html quirk: a numeric-looking column
    # (e.g. "Dív.Líq/ Patrim." on the stocks page) sometimes comes back as
    # a text dtype instead of float, even without a "%" suffix.
    df = pd.DataFrame({"Papel": ["AAAA11"], "Segmento": ["Shoppings"], "Alguma Razão": ["-0.74"]})

    result = FundamentusClient()._clean(df, [])

    assert result["Alguma Razão"].iloc[0] == -0.74
    assert pd.api.types.is_float_dtype(result["Alguma Razão"])


def test_clean_leaves_identifying_text_columns_untouched():
    df = pd.DataFrame({"Papel": ["AAAA11"], "Segmento": ["Outros"]})

    result = FundamentusClient()._clean(df, [])

    assert result["Papel"].iloc[0] == "AAAA11"
    assert result["Segmento"].iloc[0] == "Outros"


def test_clean_does_not_mutate_the_original_dataframe():
    df = pd.DataFrame({"Papel": ["AAAA11"], "Dividend Yield": ["8,79%"]})

    FundamentusClient()._clean(df, ["Dividend Yield"])

    assert df["Dividend Yield"].iloc[0] == "8,79%"
