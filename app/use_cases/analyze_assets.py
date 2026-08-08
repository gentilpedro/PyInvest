from app.use_cases.fetch_fiis import FetchFiisUseCase
from infra.writers.excel_writer import ExcelWriter


class AnalyzeAssetsUseCase:
    """CLI fallback: fetches all FIIs and saves them to output/fiis.xlsx without filtering.

    For interactive filtering and a data preview before exporting, use `main.py` (GUI).
    """

    def __init__(self):
        self.fetch_use_case = FetchFiisUseCase()
        self.writer = ExcelWriter()

    def execute(self):
        print("Buscando dados...")

        df = self.fetch_use_case.execute()

        print(df.head())

        print("Salvando Excel...")

        self.writer.save(df, "fiis.xlsx")
        print("Finalizado!")
