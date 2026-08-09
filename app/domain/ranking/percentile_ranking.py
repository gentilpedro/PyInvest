import pandas as pd

SCORE_COLUMN = "Score"


def normalize_percentile(series: pd.Series, invert: bool = False) -> pd.Series:
    """Converts a column to a 0-100 percentile rank.

    Percentile rank (rather than min-max scaling) keeps a single extreme
    outlier - e.g. a one-off 100%+ dividend yield or a near-zero P/VP
    denominator - from dominating a composite score. "invert=True" means
    lower raw values score higher (e.g. a cheaper P/VP is better).
    """
    values = series.astype(float)
    filled = values.fillna(values.min())
    percentile = filled.rank(pct=True, method="average") * 100
    return 100 - percentile if invert else percentile


def move_column_after(df: pd.DataFrame, column: str, after: str) -> pd.DataFrame:
    columns = [c for c in df.columns if c != column]
    if after in columns:
        columns.insert(columns.index(after) + 1, column)
    else:
        columns.insert(0, column)
    return df[columns]
