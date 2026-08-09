from dataclasses import dataclass
from typing import Optional

import pandas as pd


@dataclass
class StockFilterCriteria:
    dy_min: Optional[float] = None
    cotacao_max: Optional[float] = None
    pl_max: Optional[float] = None
    pvp_max: Optional[float] = None
    psr_max: Optional[float] = None
    p_ativo_max: Optional[float] = None
    p_cap_giro_max: Optional[float] = None
    p_ebit_max: Optional[float] = None
    p_ativ_circ_liq_max: Optional[float] = None
    ev_ebit_max: Optional[float] = None
    ev_ebitda_max: Optional[float] = None
    margem_bruta_min: Optional[float] = None
    margem_ebit_min: Optional[float] = None
    margem_liquida_min: Optional[float] = None
    liquidez_corrente_min: Optional[float] = None
    roic_min: Optional[float] = None
    roe_min: Optional[float] = None
    liquidez_min: Optional[float] = None
    patrimonio_liquido_min: Optional[float] = None
    divida_patrimonio_max: Optional[float] = None
    crescimento_receita_5a_min: Optional[float] = None
    ticker: Optional[str] = None


# Maps each criteria attribute to (column name, comparison). "min" keeps
# rows with column >= value; "max" keeps rows with column <= value.
_FIELD_RULES = [
    ("dy_min", "Div.Yield", "min"),
    ("cotacao_max", "Cotação", "max"),
    ("pl_max", "P/L", "max"),
    ("pvp_max", "P/VP", "max"),
    ("psr_max", "PSR", "max"),
    ("p_ativo_max", "P/Ativo", "max"),
    ("p_cap_giro_max", "P/Cap.Giro", "max"),
    ("p_ebit_max", "P/EBIT", "max"),
    ("p_ativ_circ_liq_max", "P/Ativ Circ.Liq", "max"),
    ("ev_ebit_max", "EV/EBIT", "max"),
    ("ev_ebitda_max", "EV/EBITDA", "max"),
    ("margem_bruta_min", "Mrg Bruta", "min"),
    ("margem_ebit_min", "Mrg Ebit", "min"),
    ("margem_liquida_min", "Mrg. Líq.", "min"),
    ("liquidez_corrente_min", "Liq. Corr.", "min"),
    ("roic_min", "ROIC", "min"),
    ("roe_min", "ROE", "min"),
    ("liquidez_min", "Liq.2meses", "min"),
    ("patrimonio_liquido_min", "Patrim. Líq", "min"),
    ("divida_patrimonio_max", "Dív.Líq/ Patrim.", "max"),
    ("crescimento_receita_5a_min", "Cresc. Rec.5a", "min"),
]


class StockFilter:
    """Applies user-defined filters on top of a cleaned stocks DataFrame."""

    def apply(self, df: pd.DataFrame, criteria: StockFilterCriteria) -> pd.DataFrame:
        result = df.copy()

        for attr, column, comparison in _FIELD_RULES:
            value = getattr(criteria, attr)
            if value is None or column not in result.columns:
                continue
            if comparison == "min":
                result = result[result[column] >= value]
            else:
                result = result[result[column] <= value]

        if criteria.ticker:
            result = result[result["Papel"].str.contains(criteria.ticker, case=False, na=False)]

        return result.reset_index(drop=True)
