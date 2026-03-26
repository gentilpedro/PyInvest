import pandas as pd
from pathlib import Path


class ExcelWriter:
    def save(self, df: pd.DataFrame, filename: str):
        output_path = Path("output")
        output_path.mkdir(exist_ok=True)

        file = output_path / filename
        print(file.resolve())

        df.to_excel(file, index=False)

        print(f"Arquivo salvo em: {file}")