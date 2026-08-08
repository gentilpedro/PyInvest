import math

PERCENT_COLUMNS = {
    "FFO Yield", "Dividend Yield", "Cap Rate", "Vacância Média",
    "Div.Yield", "Mrg Bruta", "Mrg Ebit", "Mrg. Líq.", "ROIC", "ROE", "Cresc. Rec.5a",
}
INTEGER_COLUMNS = {"Valor de Mercado", "Liquidez", "Qtd de imóveis", "Liq.2meses", "Patrim. Líq"}
DECIMAL_COLUMNS = {
    "Cotação", "P/VP", "Preço do m2", "Aluguel por m2", "Score",
    "P/L", "PSR", "P/Ativo", "P/Cap.Giro", "P/EBIT", "P/Ativ Circ.Liq",
    "EV/EBIT", "EV/EBITDA", "Liq. Corr.", "Dív.Líq/ Patrim.",
}
NUMERIC_COLUMNS = PERCENT_COLUMNS | INTEGER_COLUMNS | DECIMAL_COLUMNS


def format_value(column: str, value) -> str:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return "-"

    if column in PERCENT_COLUMNS:
        return f"{value:.2f}%".replace(".", ",")

    if column in INTEGER_COLUMNS:
        return f"{value:,.0f}".replace(",", ".")

    if column in DECIMAL_COLUMNS:
        return f"{value:,.2f}".replace(",", "@").replace(".", ",").replace("@", ".")

    return str(value)


def sort_key(column: str, value):
    if column in NUMERIC_COLUMNS:
        if value is None or (isinstance(value, float) and math.isnan(value)):
            return float("-inf")
        return float(value)
    return "" if value is None else str(value)
