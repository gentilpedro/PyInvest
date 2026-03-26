import requests
import pandas as pd


class FundamentusClient:
    URL = "https://www.fundamentus.com.br/fii_resultado.php"

    def fetch_fiis(self) -> pd.DataFrame:
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept-Language": "pt-BR,pt;q=0.9",
        }

        response = requests.get(self.URL, headers=headers, timeout=30)
        response.raise_for_status()

        df = pd.read_html(response.text, flavor="lxml")[0]
        
        # limpa colunas
        df.columns = [col.strip() for col in df.columns]

        return df