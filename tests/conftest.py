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
