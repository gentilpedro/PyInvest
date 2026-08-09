from dataclasses import dataclass
from typing import Optional

import pandas as pd


@dataclass
class StockFilterCriteria:
    dy_min: Optional[float] = None
    pl_max: Optional[float] = None
    pvp_max: Optional[float] = None
    roe_min: Optional[float] = None
    roic_min: Optional[float] = None
    margem_liquida_min: Optional[float] = None
    divida_patrimonio_max: Optional[float] = None
    liquidez_min: Optional[float] = None
    patrimonio_liquido_min: Optional[float] = None
    ticker: Optional[str] = None


class StockFilter:
    """Applies user-defined filters on top of a cleaned stocks DataFrame."""

    def apply(self, df: pd.DataFrame, criteria: StockFilterCriteria) -> pd.DataFrame:
        result = df.copy()

        if criteria.dy_min is not None:
            result = result[result["Div.Yield"] >= criteria.dy_min]

        if criteria.pl_max is not None:
            result = result[result["P/L"] <= criteria.pl_max]

        if criteria.pvp_max is not None:
            result = result[result["P/VP"] <= criteria.pvp_max]

        if criteria.roe_min is not None:
            result = result[result["ROE"] >= criteria.roe_min]

        if criteria.roic_min is not None:
            result = result[result["ROIC"] >= criteria.roic_min]

        if criteria.margem_liquida_min is not None:
            result = result[result["Mrg. Líq."] >= criteria.margem_liquida_min]

        if criteria.divida_patrimonio_max is not None:
            result = result[result["Dív.Líq/ Patrim."] <= criteria.divida_patrimonio_max]

        if criteria.liquidez_min is not None:
            result = result[result["Liq.2meses"] >= criteria.liquidez_min]

        if criteria.patrimonio_liquido_min is not None:
            result = result[result["Patrim. Líq"] >= criteria.patrimonio_liquido_min]

        if criteria.ticker:
            result = result[result["Papel"].str.contains(criteria.ticker, case=False, na=False)]

        return result.reset_index(drop=True)
