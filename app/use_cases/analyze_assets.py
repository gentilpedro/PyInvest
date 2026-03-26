from infra.external.fundamentus.fundamentus_client import FundamentusClient
from infra.writers.excel_writer import ExcelWriter


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