import pandas as pd
import pytest


@pytest.fixture
def sample_fii_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Papel": ["AAAA11", "BBBB11", "CCCC11", "DDDD11"],
            "Segmento": ["Shoppings", "Logística", "Shoppings", "Outros"],
            "Cotação": [100.0, 50.0, 75.0, 10.0],
            "FFO Yield": [10.0, 8.0, 5.0, 0.0],
            "Dividend Yield": [9.0, 12.0, 6.0, 0.0],
            "P/VP": [0.9, 1.2, 1.0, 2.0],
            "Valor de Mercado": [1_000_000, 500_000, 2_000_000, 100_000],
            "Liquidez": [50_000, 10_000, 200_000, 0],
            "Qtd de imóveis": [5, 2, 10, 0],
            "Preço do m2": [1000.0, 500.0, 800.0, 0.0],
            "Aluguel por m2": [10.0, 5.0, 8.0, 0.0],
            "Cap Rate": [8.0, 6.0, 10.0, 0.0],
            "Vacância Média": [2.0, 5.0, 0.0, 100.0],
        }
    )


@pytest.fixture
def sample_stock_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Papel": ["AAAA3", "BBBB4", "CCCC3", "DDDD3"],
            "Cotação": [20.0, 50.0, 8.0, 100.0],
            "P/L": [8.0, 15.0, -5.0, 25.0],
            "P/VP": [1.2, 2.0, 0.8, 3.5],
            "PSR": [1.0, 2.0, 0.5, 4.0],
            "Div.Yield": [6.0, 3.0, 0.0, 8.0],
            "ROE": [18.0, 10.0, -20.0, 25.0],
            "ROIC": [15.0, 8.0, -10.0, 20.0],
            "Mrg. Líq.": [12.0, 5.0, -8.0, 20.0],
            "Liq.2meses": [1_000_000, 200_000, 50_000, 5_000_000],
            "Patrim. Líq": [500_000_000, 100_000_000, 10_000_000, 2_000_000_000],
            "Dív.Líq/ Patrim.": [0.5, 1.2, 2.0, -0.3],
        }
    )
