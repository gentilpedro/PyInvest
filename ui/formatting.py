import math

PERCENT_COLUMNS = {"FFO Yield", "Dividend Yield", "Cap Rate", "Vacância Média"}
INTEGER_COLUMNS = {"Valor de Mercado", "Liquidez", "Qtd de imóveis"}
DECIMAL_COLUMNS = {"Cotação", "P/VP", "Preço do m2", "Aluguel por m2", "Score"}
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
