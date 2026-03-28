import undetected_chromedriver as uc
import pandas as pd
import time


from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class FundamentusClient:
    URL = "https://www.fundamentus.com.br/fii_resultado.php"

    def fetch_fiis(self) -> pd.DataFrame:
        options = uc.ChromeOptions()
        options.headless = False  # pode testar False se quiser ver

        driver = uc.Chrome(version_main=146, options=options)
        driver.get(self.URL)
        
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//table//a"))
        )
        
        time.sleep(3)

        html = driver.page_source

        try:
            driver.quit()
        except Exception as e:
            print(f"Erro ao fechar o navegador: {e}")
            pass
    
        df = pd.read_html(html)[0]
        df.columns = [col.strip() for col in df.columns]

        return df