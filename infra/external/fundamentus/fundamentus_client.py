import undetected_chromedriver as uc
import pandas as pd
import time


class FundamentusClient:
    URL = "https://www.fundamentus.com.br/fii_resultado.php"

    def fetch_fiis(self) -> pd.DataFrame:
        options = uc.ChromeOptions()
        options.headless = True  # pode testar False se quiser ver

        driver = uc.Chrome(options=options)

        driver.get(self.URL)

        time.sleep(5)  # espera carregar Cloudflare

        html = driver.page_source

        driver.quit()

        df = pd.read_html(html)[0]
        df.columns = [col.strip() for col in df.columns]

        return df