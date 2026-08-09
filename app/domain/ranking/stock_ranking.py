import pandas as pd

from app.domain.ranking.percentile_ranking import SCORE_COLUMN, move_column_after, normalize_percentile

# invert=True means lower raw values score higher (e.g. a cheaper P/VP is
# better for the stock).
FACTORS = [
    ("Div.Yield", 0.25, False),
    ("P/VP", 0.15, True),
    ("ROE", 0.15, False),
    ("ROIC", 0.15, False),
    ("Liq.2meses", 0.10, False),
]
PL_WEIGHT = 0.20


class StockRanking:
    """Adds a 0-100 composite Score column ranking stocks relative to each other."""

    def add_score(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        score = pd.Series(0.0, index=df.index)

        for column, weight, invert in FACTORS:
            if column not in df.columns:
                continue
            score += normalize_percentile(df[column], invert=invert) * weight

        if "P/L" in df.columns:
            score += self._normalize_pl(df["P/L"]) * PL_WEIGHT

        df[SCORE_COLUMN] = score.round(1)
        return move_column_after(df, SCORE_COLUMN, after="Papel")

    @staticmethod
    def _normalize_pl(series: pd.Series) -> pd.Series:
        # A negative or zero P/L means the company had losses in the period -
        # that is not "cheap", so it must not be treated as a top percentile
        # once inverted. Only positive P/L values are ranked (lower is
        # better); non-positive P/L scores the worst (0) on this factor. The
        # positive range is compressed to (1, 100] - rather than [0, 100] -
        # so even the least attractive *profitable* company still outscores
        # any loss-making one, instead of both collapsing to the same 0.
        values = series.astype(float)
        result = pd.Series(0.0, index=series.index)
        positive = values > 0
        if positive.any():
            ranked = normalize_percentile(values[positive], invert=True)
            result.loc[positive] = 1 + ranked * 0.99
        return result
