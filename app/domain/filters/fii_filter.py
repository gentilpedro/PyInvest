import pandas as pd

class FiiFilter:

    def apply(self, df: pd.DataFrame, filters: dict) -> pd.DataFrame:
        df = df.copy()

        # 🔹 Converter colunas (IMPORTANTE)
        df["DY"] = df["DY"].str.replace("%", "").str.replace(",", ".").astype(float)
        df["P/VP"] = df["P/VP"].str.replace(",", ".").astype(float)
        df["Liquidez"] = df["Liquidez"].astype(str).str.replace(".", "").astype(float)

        # 🔹 Aplicar filtros
        if filters.get("dy_min"):
            df = df[df["DY"] >= filters["dy_min"]]

        if filters.get("pvp_max"):
            df = df[df["P/VP"] <= filters["pvp_max"]]

        if filters.get("liquidez_min"):
            df = df[df["Liquidez"] >= filters["liquidez_min"]]

        return df

    def rank(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # 🔥 Score simples (tu pode evoluir isso MUITO depois)
        df["SCORE"] = (
            (df["DY"] * 0.5) +
            ((1 / df["P/VP"]) * 0.3) +
            (df["Liquidez"] / df["Liquidez"].max() * 0.2)
        )

        df = df.sort_values(by="SCORE", ascending=False)

        return df