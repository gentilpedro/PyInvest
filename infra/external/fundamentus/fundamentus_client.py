import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from io import StringIO

PERCENT_COLUMNS = ["FFO Yield", "Dividend Yield", "Cap Rate", "Vacância Média"]


class FundamentusClient:
    URL = "https://www.fundamentus.com.br/fii_resultado.php"

    def fetch_fiis(self) -> pd.DataFrame:
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-blink-features=AutomationControlled")

        driver = webdriver.Chrome(options=options)

        driver.get(self.URL)

        time.sleep(5)

        html = driver.page_source

        driver.quit()

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
            raise Exception("Tabela de FIIs não encontrada")

        df.columns = [col.strip() for col in df.columns]

        return self._clean(df)

    def _clean(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        for col in PERCENT_COLUMNS:
            if col in df.columns:
                df[col] = (
                    df[col]
                    .astype(str)
                    .str.replace("%", "", regex=False)
                    .str.replace(",", ".", regex=False)
                )
                df[col] = pd.to_numeric(df[col], errors="coerce")

        return df
