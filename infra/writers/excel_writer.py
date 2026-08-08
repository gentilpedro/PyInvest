import pandas as pd
from pathlib import Path


class ExcelWriter:
    def save(self, df: pd.DataFrame, filename: str):
        output_path = Path("output")
        output_path.mkdir(exist_ok=True)

        file = output_path / filename
        self.save_as(df, file)

    def save_as(self, df: pd.DataFrame, path: str | Path):
        file = Path(path)
        file.parent.mkdir(parents=True, exist_ok=True)

        df.to_excel(file, index=False)

        print(f"Arquivo salvo em: {file.resolve()}")