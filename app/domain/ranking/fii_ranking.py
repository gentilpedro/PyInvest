import pandas as pd

from app.domain.ranking.percentile_ranking import SCORE_COLUMN, move_column_after, normalize_percentile

# invert=True means lower raw values score higher (e.g. a cheaper P/VP or
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
            score += normalize_percentile(df[column], invert=invert) * weight

        df[SCORE_COLUMN] = score.round(1)
        return move_column_after(df, SCORE_COLUMN, after="Segmento")
