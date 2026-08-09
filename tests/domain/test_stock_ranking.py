import pandas as pd

from app.domain.ranking.stock_ranking import StockRanking


def _two_row_df(**overrides) -> pd.DataFrame:
    base = {
        "Papel": ["AAAA3", "BBBB4"],
        "P/L": [10.0, 10.0],
        "P/VP": [1.0, 1.0],
        "ROE": [12.0, 12.0],
        "ROIC": [10.0, 10.0],
        "Div.Yield": [5.0, 5.0],
        "Liq.2meses": [100_000, 100_000],
    }
    base.update(overrides)
    return pd.DataFrame(base)


def test_score_column_is_placed_right_after_papel(sample_stock_df):
    result = StockRanking().add_score(sample_stock_df)
    assert list(result.columns).index("Score") == list(result.columns).index("Papel") + 1


def test_score_is_between_0_and_100(sample_stock_df):
    result = StockRanking().add_score(sample_stock_df)
    assert result["Score"].between(0, 100).all()


def test_original_dataframe_is_not_mutated(sample_stock_df):
    original_columns = list(sample_stock_df.columns)
    StockRanking().add_score(sample_stock_df)
    assert list(sample_stock_df.columns) == original_columns


def test_higher_dividend_yield_scores_better():
    df = _two_row_df(**{"Div.Yield": [2.0, 10.0]})
    result = StockRanking().add_score(df)
    assert result.loc[result["Papel"] == "BBBB4", "Score"].iloc[0] > result.loc[result["Papel"] == "AAAA3", "Score"].iloc[0]


def test_lower_pvp_scores_better():
    df = _two_row_df(**{"P/VP": [0.5, 3.0]})
    result = StockRanking().add_score(df)
    assert result.loc[result["Papel"] == "AAAA3", "Score"].iloc[0] > result.loc[result["Papel"] == "BBBB4", "Score"].iloc[0]


def test_higher_roe_scores_better():
    df = _two_row_df(**{"ROE": [5.0, 30.0]})
    result = StockRanking().add_score(df)
    assert result.loc[result["Papel"] == "BBBB4", "Score"].iloc[0] > result.loc[result["Papel"] == "AAAA3", "Score"].iloc[0]


def test_higher_roic_scores_better():
    df = _two_row_df(**{"ROIC": [2.0, 25.0]})
    result = StockRanking().add_score(df)
    assert result.loc[result["Papel"] == "BBBB4", "Score"].iloc[0] > result.loc[result["Papel"] == "AAAA3", "Score"].iloc[0]


def test_higher_liquidez_scores_better():
    df = _two_row_df(**{"Liq.2meses": [1_000, 10_000_000]})
    result = StockRanking().add_score(df)
    assert result.loc[result["Papel"] == "BBBB4", "Score"].iloc[0] > result.loc[result["Papel"] == "AAAA3", "Score"].iloc[0]


def test_lower_positive_pl_scores_better():
    df = _two_row_df(**{"P/L": [5.0, 20.0]})
    result = StockRanking().add_score(df)
    assert result.loc[result["Papel"] == "AAAA3", "Score"].iloc[0] > result.loc[result["Papel"] == "BBBB4", "Score"].iloc[0]


def test_negative_pl_does_not_look_cheaper_than_positive_pl():
    # A company with losses (negative P/L) must not outrank profitable ones
    # just because -50 < 5 mathematically - that would reward loss-making
    # companies as if they were a bargain. Uses two positive P/L peers so the
    # comparison isn't a degenerate single-element percentile rank.
    df = pd.DataFrame(
        {
            "Papel": ["LOSS3", "CHEAP3", "PRICEY3"],
            "P/L": [-50.0, 5.0, 20.0],
            "P/VP": [1.0, 1.0, 1.0],
            "ROE": [12.0, 12.0, 12.0],
            "ROIC": [10.0, 10.0, 10.0],
            "Div.Yield": [5.0, 5.0, 5.0],
            "Liq.2meses": [100_000, 100_000, 100_000],
        }
    )
    result = StockRanking().add_score(df).set_index("Papel")
    assert result.loc["CHEAP3", "Score"] > result.loc["LOSS3", "Score"]
    assert result.loc["PRICEY3", "Score"] > result.loc["LOSS3", "Score"]
    assert result.loc["CHEAP3", "Score"] > result.loc["PRICEY3", "Score"]


def test_extreme_outlier_does_not_dominate_the_ranking():
    df = pd.DataFrame(
        {
            "Papel": ["OUTLIER3", "SOLID3", "WEAK3"],
            "Div.Yield": [200.0, 8.0, 1.0],
            "P/L": [0.4, 9.0, 40.0],
            "P/VP": [50.0, 1.0, 3.0],
            "ROE": [1.0, 20.0, 3.0],
            "ROIC": [0.0, 18.0, 2.0],
            "Liq.2meses": [0, 2_000_000, 10_000],
        }
    )
    result = StockRanking().add_score(df).set_index("Papel")
    assert result.loc["SOLID3", "Score"] > result.loc["OUTLIER3", "Score"]
    assert result.loc["SOLID3", "Score"] > result.loc["WEAK3", "Score"]
