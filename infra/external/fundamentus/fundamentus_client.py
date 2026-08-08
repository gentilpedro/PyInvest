import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from io import StringIO

FII_URL = "https://www.fundamentus.com.br/fii_resultado.php"
FII_PERCENT_COLUMNS = ["FFO Yield", "Dividend Yield", "Cap Rate", "Vacância Média"]

STOCK_URL = "https://www.fundamentus.com.br/resultado.php"
STOCK_PERCENT_COLUMNS = [
    "Div.Yield", "Mrg Bruta", "Mrg Ebit", "Mrg. Líq.", "ROIC", "ROE", "Cresc. Rec.5a"
]


class FundamentusClient:
    def fetch_fiis(self) -> pd.DataFrame:
        return self._fetch_table(FII_URL, FII_PERCENT_COLUMNS, "Tabela de FIIs não encontrada")

    def fetch_stocks(self) -> pd.DataFrame:
        return self._fetch_table(STOCK_URL, STOCK_PERCENT_COLUMNS, "Tabela de ações não encontrada")

    def _fetch_table(self, url: str, percent_columns: list[str], not_found_message: str) -> pd.DataFrame:
        html = self._fetch_html(url)

        # Fundamentus formats numbers using the Brazilian convention
        # ("." as thousands separator, "," as decimal separator), which is
        # the opposite of pandas' default. Without this, pd.read_html
        # mangles values like "6,41" into "641".
        tables = pd.read_html(StringIO(html), decimal=",", thousands=".")

        if not tables:
            raise Exception("Nenhuma tabela encontrada")

        df = None
        for table in tables:
            if "Papel" in table.columns:
                df = table
                break

        if df is None:
            raise Exception(not_found_message)

        df.columns = [col.strip() for col in df.columns]

        return self._clean(df, percent_columns)

    def _fetch_html(self, url: str) -> str:
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-blink-features=AutomationControlled")

        driver = webdriver.Chrome(options=options)
        try:
            driver.get(url)
            time.sleep(5)
            return driver.page_source
        finally:
            driver.quit()

    def _clean(self, df: pd.DataFrame, percent_columns: list[str]) -> pd.DataFrame:
        df = df.copy()

        for col in percent_columns:
            if col in df.columns:
                df[col] = (
                    df[col]
                    .astype(str)
                    .str.replace("%", "", regex=False)
                    .str.replace(",", ".", regex=False)
                )
                df[col] = pd.to_numeric(df[col], errors="coerce")

        # pandas.read_html occasionally leaves an otherwise-numeric column as
        # object dtype (e.g. "Dív.Líq/ Patrim." on the stocks page). Coerce
        # any leftover text column - besides the identifying ones - to numeric.
        text_id_columns = {"Papel", "Segmento"}
        for col in df.columns:
            if col in text_id_columns or col in percent_columns:
                continue
            if not pd.api.types.is_numeric_dtype(df[col]):
                df[col] = pd.to_numeric(df[col], errors="coerce")

        return df
