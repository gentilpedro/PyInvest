from infra.external.fundamentus.fundamentus_client import FundamentusClient
from infra.writers.excel_writer import ExcelWriter
from app.domain.filters.fii_filter import FiiFilter


class AnalyzeAssetsUseCase:
    def __init__(self):
        self.client = FundamentusClient()
        self.writer = ExcelWriter()

    def execute(self):
        print("🔎 Buscando dados...")

        df = self.client.fetch_fiis()

        print(df.head())  # debug opcional

        print("💾 Salvando Excel...")

        self.writer.save(df, "fiis.xlsx")
        print("✅ Finalizado!")

        filter_engine = FiiFilter()

        filters = {
            "dy_min": 8,
            "pvp_max": 1.0,
            "liquidez_min": 100000
        }

        df = filter_engine.apply(df, filters)
        df = filter_engine.rank(df)
