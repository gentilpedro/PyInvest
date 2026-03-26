from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

import pandas as pd
import time


class FundamentusClient:
    URL = "https://www.fundamentus.com.br/fii_resultado.php"

    def fetch_fiis(self) -> pd.DataFrame:
        options = Options()
        options.add_argument("--headless")  # roda sem abrir janela
        options.add_argument("--disable-blink-features=AutomationControlled")

        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )

        driver.get(self.URL)

        # espera carregar (importante)
        time.sleep(5)

        html = driver.page_source
        driver.quit()

        df = pd.read_html(html)[0]
        df.columns = [col.strip() for col in df.columns]

        return df