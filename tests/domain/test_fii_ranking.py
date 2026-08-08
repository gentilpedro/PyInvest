import pandas as pd

from app.domain.ranking.fii_ranking import FiiRanking


def _two_row_df(**overrides) -> pd.DataFrame:
    base = {
        "Papel": ["AAAA11", "BBBB11"],
        "Segmento": ["Shoppings", "Shoppings"],
        "Dividend Yield": [8.0, 8.0],
        "P/VP": [1.0, 1.0],
        "Cap Rate": [7.0, 7.0],
        "Vacância Média": [5.0, 5.0],
        "Liquidez": [10_000, 10_000],
    }
    base.update(overrides)
    return pd.DataFrame(base)


def test_score_column_is_placed_right_after_segmento(sample_fii_df):
    result = FiiRanking().add_score(sample_fii_df)
    assert list(result.columns).index("Score") == list(result.columns).index("Segmento") + 1


def test_score_is_between_0_and_100(sample_fii_df):
    result = FiiRanking().add_score(sample_fii_df)
    assert result["Score"].between(0, 100).all()


def test_original_dataframe_is_not_mutated(sample_fii_df):
    original_columns = list(sample_fii_df.columns)
    FiiRanking().add_score(sample_fii_df)
    assert list(sample_fii_df.columns) == original_columns


def test_higher_dividend_yield_scores_better():
    df = _two_row_df(**{"Dividend Yield": [5.0, 12.0]})
    result = FiiRanking().add_score(df)
    assert result.loc[result["Papel"] == "BBBB11", "Score"].iloc[0] > result.loc[result["Papel"] == "AAAA11", "Score"].iloc[0]


def test_lower_pvp_scores_better():
    df = _two_row_df(**{"P/VP": [0.5, 1.8]})
    result = FiiRanking().add_score(df)
    assert result.loc[result["Papel"] == "AAAA11", "Score"].iloc[0] > result.loc[result["Papel"] == "BBBB11", "Score"].iloc[0]


def test_higher_cap_rate_scores_better():
    df = _two_row_df(**{"Cap Rate": [3.0, 15.0]})
    result = FiiRanking().add_score(df)
    assert result.loc[result["Papel"] == "BBBB11", "Score"].iloc[0] > result.loc[result["Papel"] == "AAAA11", "Score"].iloc[0]


def test_lower_vacancia_scores_better():
    df = _two_row_df(**{"Vacância Média": [1.0, 30.0]})
    result = FiiRanking().add_score(df)
    assert result.loc[result["Papel"] == "AAAA11", "Score"].iloc[0] > result.loc[result["Papel"] == "BBBB11", "Score"].iloc[0]


def test_higher_liquidez_scores_better():
    df = _two_row_df(**{"Liquidez": [1_000, 5_000_000]})
    result = FiiRanking().add_score(df)
    assert result.loc[result["Papel"] == "BBBB11", "Score"].iloc[0] > result.loc[result["Papel"] == "AAAA11", "Score"].iloc[0]


def test_extreme_outlier_does_not_dominate_the_ranking():
    # A single absurd Dividend Yield (data anomaly) should not overrule an
    # otherwise weak fund - percentile-rank normalization caps its influence,
    # unlike naive min-max scaling which would let it dominate the score.
    df = pd.DataFrame(
        {
            "Papel": ["OUTLIER11", "SOLID11", "WEAK11"],
            "Segmento": ["Outros", "Outros", "Outros"],
            "Dividend Yield": [200.0, 10.0, 2.0],
            "P/VP": [50.0, 0.8, 1.5],
            "Cap Rate": [0.0, 9.0, 3.0],
            "Vacância Média": [0.0, 1.0, 20.0],
            "Liquidez": [0, 100_000, 5_000],
        }
    )
    result = FiiRanking().add_score(df).set_index("Papel")
    assert result.loc["SOLID11", "Score"] > result.loc["OUTLIER11", "Score"]
    assert result.loc["SOLID11", "Score"] > result.loc["WEAK11", "Score"]
