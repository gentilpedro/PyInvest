import pandas as pd

SCORE_COLUMN = "Score"

# Each factor is converted to a 0-100 percentile rank across the current
# dataset, then combined with these weights. Percentile rank (rather than
# min-max scaling) keeps single extreme outliers - e.g. a one-off 100%+
# dividend yield or a near-zero P/VP denominator - from dominating the score.
# "invert=True" means lower raw values score higher (e.g. a cheaper P/VP or
# lower vacancy is better for the fund).
FACTORS = [
    ("Dividend Yield", 0.30, False),
    ("P/VP", 0.20, True),
    ("Cap Rate", 0.20, False),
    ("Vacância Média", 0.15, True),
    ("Liquidez", 0.15, False),
]


class FiiRanking:
    """Adds a 0-100 composite Score column ranking FIIs relative to each other."""

    def add_score(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        score = pd.Series(0.0, index=df.index)

        for column, weight, invert in FACTORS:
            if column not in df.columns:
                continue
            score += self._normalize(df[column], invert=invert) * weight

        df[SCORE_COLUMN] = score.round(1)
        return self._move_after(df, SCORE_COLUMN, after="Segmento")

    @staticmethod
    def _normalize(series: pd.Series, invert: bool = False) -> pd.Series:
        values = series.astype(float)
        filled = values.fillna(values.min())
        percentile = filled.rank(pct=True, method="average") * 100
        return 100 - percentile if invert else percentile

    @staticmethod
    def _move_after(df: pd.DataFrame, column: str, after: str) -> pd.DataFrame:
        columns = [c for c in df.columns if c != column]
        if after in columns:
            columns.insert(columns.index(after) + 1, column)
        else:
            columns.insert(0, column)
        return df[columns]
