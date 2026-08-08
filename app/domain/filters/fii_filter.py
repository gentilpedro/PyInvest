from dataclasses import dataclass
from typing import Optional

import pandas as pd


@dataclass
class FiiFilterCriteria:
    dy_min: Optional[float] = None
    pvp_max: Optional[float] = None
    liquidez_min: Optional[float] = None
    segmento: Optional[str] = None
    ffo_yield_min: Optional[float] = None
    valor_mercado_min: Optional[float] = None
    qtd_imoveis_min: Optional[int] = None
    cap_rate_min: Optional[float] = None
    vacancia_max: Optional[float] = None
    ticker: Optional[str] = None


class FiiFilter:
    """Applies user-defined filters on top of a cleaned FII DataFrame."""

    def segments(self, df: pd.DataFrame) -> list[str]:
        if "Segmento" not in df.columns:
            return []
        return sorted(df["Segmento"].dropna().unique().tolist())

    def apply(self, df: pd.DataFrame, criteria: FiiFilterCriteria) -> pd.DataFrame:
        result = df.copy()

        if criteria.dy_min is not None:
            result = result[result["Dividend Yield"] >= criteria.dy_min]

        if criteria.pvp_max is not None:
            result = result[result["P/VP"] <= criteria.pvp_max]

        if criteria.liquidez_min is not None:
            result = result[result["Liquidez"] >= criteria.liquidez_min]

        if criteria.segmento and criteria.segmento != "Todos":
            result = result[result["Segmento"] == criteria.segmento]

        if criteria.ffo_yield_min is not None:
            result = result[result["FFO Yield"] >= criteria.ffo_yield_min]

        if criteria.valor_mercado_min is not None:
            result = result[result["Valor de Mercado"] >= criteria.valor_mercado_min]

        if criteria.qtd_imoveis_min is not None:
            result = result[result["Qtd de imóveis"] >= criteria.qtd_imoveis_min]

        if criteria.cap_rate_min is not None:
            result = result[result["Cap Rate"] >= criteria.cap_rate_min]

        if criteria.vacancia_max is not None:
            result = result[result["Vacância Média"] <= criteria.vacancia_max]

        if criteria.ticker:
            result = result[result["Papel"].str.contains(criteria.ticker, case=False, na=False)]

        return result.reset_index(drop=True)
