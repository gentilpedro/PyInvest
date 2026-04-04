import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from io import StringIO

class FundamentusClient:
    URL = "https://www.fundamentus.com.br/fii_resultado.php"

    def fetch_fiis(self) -> pd.DataFrame:
        options = Options()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")

        driver = webdriver.Chrome(options=options)

        driver.get(self.URL)

        time.sleep(5)

        html = driver.page_source

        driver.quit()


        tables = pd.read_html(StringIO(html))

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

        return df