import pandas as pd

from infra.external.fundamentus.fundamentus_client import FundamentusClient


class FetchStocksUseCase:
    def __init__(self, client: FundamentusClient | None = None):
        self.client = client or FundamentusClient()

    def execute(self) -> pd.DataFrame:
        return self.client.fetch_stocks()
