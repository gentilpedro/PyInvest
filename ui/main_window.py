import queue
import tkinter as tk
from tkinter import messagebox, filedialog, ttk

import pandas as pd

from app.domain.filters.fii_filter import FiiFilter, FiiFilterCriteria
from infra.writers.excel_writer import ExcelWriter
from ui.fetch_worker import FetchFiisWorker
from ui.fii_table import FiiTable

TODOS_SEGMENTOS = "Todos"
PVP_MAX_LIMIT = 100.0
VACANCIA_MAX_LIMIT = 100.0


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PyInvest - Ranking de FIIs")
        self.geometry("1200x700")

        self.raw_df: pd.DataFrame | None = None
        self.filtered_df: pd.DataFrame = pd.DataFrame()

        self.filter_engine = FiiFilter()
        self.writer = ExcelWriter()
        self.result_queue: "queue.Queue | None" = None

        self.dy_min_var = tk.DoubleVar(value=0.0)
        self.pvp_max_var = tk.DoubleVar(value=PVP_MAX_LIMIT)
        self.liquidez_min_var = tk.DoubleVar(value=0.0)
        self.segmento_var = tk.StringVar(value=TODOS_SEGMENTOS)
        self.ffo_yield_min_var = tk.DoubleVar(value=0.0)
        self.valor_mercado_min_var = tk.DoubleVar(value=0.0)
        self.qtd_imoveis_min_var = tk.IntVar(value=0)
        self.cap_rate_min_var = tk.DoubleVar(value=0.0)
        self.vacancia_max_var = tk.DoubleVar(value=VACANCIA_MAX_LIMIT)
        self.ticker_var = tk.StringVar(value="")
        self.row_count_var = tk.StringVar(value="")
        self.status_var = tk.StringVar(value='Pronto. Clique em "Buscar dados" para começar.')

        self._build_ui()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------
    def _build_ui(self):
        self._build_filter_panel()
        self._build_actions_row()
        self._build_table()
        self._build_status_bar()

    def _build_filter_panel(self):
        panel = ttk.LabelFrame(self, text="Filtros")
        panel.pack(fill="x", padx=8, pady=(8, 4))

        self._add_spinbox(panel, 0, 0, "Dividend Yield mínimo (%):", self.dy_min_var, from_=0, to=100, increment=0.1)
        self._add_spinbox(panel, 0, 1, "P/VP máximo:", self.pvp_max_var, from_=0, to=PVP_MAX_LIMIT, increment=0.01)
        self._add_spinbox(
            panel, 0, 2, "Liquidez diária mínima (R$):", self.liquidez_min_var,
            from_=0, to=1_000_000_000, increment=1000, width=14,
        )
        self._add_spinbox(
            panel, 0, 3, "FFO Yield mínimo (%):", self.ffo_yield_min_var, from_=0, to=100, increment=0.1
        )
        self._add_spinbox(
            panel, 0, 4, "Valor de Mercado mínimo (R$):", self.valor_mercado_min_var,
            from_=0, to=100_000_000_000, increment=1_000_000, width=16,
        )

        self._add_spinbox(
            panel, 1, 0, "Qtd de imóveis mínima:", self.qtd_imoveis_min_var, from_=0, to=1000, increment=1
        )
        self._add_spinbox(
            panel, 1, 1, "Cap Rate mínimo (%):", self.cap_rate_min_var, from_=0, to=100, increment=0.1
        )
        self._add_spinbox(
            panel, 1, 2, "Vacância máxima (%):", self.vacancia_max_var,
            from_=0, to=VACANCIA_MAX_LIMIT, increment=0.5,
        )

        ttk.Label(panel, text="Segmento:").grid(row=1, column=6, padx=6, pady=4, sticky="w")
        self.segmento_combo = ttk.Combobox(
            panel, textvariable=self.segmento_var, state="readonly", values=[TODOS_SEGMENTOS], width=18
        )
        self.segmento_combo.grid(row=1, column=7, padx=6, pady=4, sticky="w")

        ttk.Label(panel, text="Buscar ticker:").grid(row=1, column=8, padx=6, pady=4, sticky="w")
        ttk.Entry(panel, textvariable=self.ticker_var, width=12).grid(
            row=1, column=9, padx=6, pady=4, sticky="w"
        )

    def _add_spinbox(self, panel, row, col, label, var, width=10, **spin_kwargs):
        ttk.Label(panel, text=label).grid(row=row, column=col * 2, padx=6, pady=4, sticky="w")
        ttk.Spinbox(panel, textvariable=var, width=width, **spin_kwargs).grid(
            row=row, column=col * 2 + 1, padx=6, pady=4, sticky="w"
        )

    def _build_actions_row(self):
        row = ttk.Frame(self)
        row.pack(fill="x", padx=8, pady=4)

        self.fetch_button = ttk.Button(row, text="Buscar dados", command=self.on_fetch_clicked)
        self.fetch_button.pack(side="left")

        self.apply_filters_button = ttk.Button(
            row, text="Aplicar filtros", command=self.on_apply_filters_clicked, state="disabled"
        )
        self.apply_filters_button.pack(side="left", padx=(6, 0))

        self.clear_filters_button = ttk.Button(
            row, text="Limpar filtros", command=self.on_clear_filters_clicked, state="disabled"
        )
        self.clear_filters_button.pack(side="left", padx=(6, 0))

        ttk.Label(row, textvariable=self.row_count_var).pack(side="left", padx=20)

        self.save_button = ttk.Button(
            row, text="Salvar como XLSX", command=self.on_save_clicked, state="disabled"
        )
        self.save_button.pack(side="right")

    def _build_table(self):
        self.table = FiiTable(self)
        self.table.pack(fill="both", expand=True, padx=8, pady=4)

    def _build_status_bar(self):
        bar = ttk.Label(self, textvariable=self.status_var, relief="sunken", anchor="w")
        bar.pack(fill="x", side="bottom")

    # ------------------------------------------------------------------
    # Fetching
    # ------------------------------------------------------------------
    def on_fetch_clicked(self):
        self.fetch_button.state(["disabled"])
        self.apply_filters_button.state(["disabled"])
        self.clear_filters_button.state(["disabled"])
        self.save_button.state(["disabled"])
        self.status_var.set("Buscando dados no Fundamentus... isso pode levar alguns segundos.")
        self.config(cursor="watch")

        self.result_queue = queue.Queue()
        worker = FetchFiisWorker(self.result_queue)
        worker.start()
        self.after(100, self._poll_fetch_result)

    def _poll_fetch_result(self):
        try:
            status, payload = self.result_queue.get_nowait()
        except queue.Empty:
            self.after(100, self._poll_fetch_result)
            return

        if status == "ok":
            self._on_fetch_finished(payload)
        else:
            self._on_fetch_failed(payload)

    def _on_fetch_finished(self, df: pd.DataFrame):
        self.config(cursor="")
        self.fetch_button.state(["!disabled"])
        self.apply_filters_button.state(["!disabled"])
        self.clear_filters_button.state(["!disabled"])
        self.save_button.state(["!disabled"])

        self.raw_df = df

        segments = [TODOS_SEGMENTOS] + self.filter_engine.segments(df)
        self.segmento_combo.configure(values=segments)
        self.segmento_var.set(TODOS_SEGMENTOS)

        self._show_dataframe(df)
        self.status_var.set(f"{len(df)} FIIs carregados.")

    def _on_fetch_failed(self, message: str):
        self.config(cursor="")
        self.fetch_button.state(["!disabled"])
        self.status_var.set("Falha ao buscar dados.")
        messagebox.showerror("Erro ao buscar dados", message)

    # ------------------------------------------------------------------
    # Filtering
    # ------------------------------------------------------------------
    def on_apply_filters_clicked(self):
        if self.raw_df is None:
            return

        pvp_value = self.pvp_max_var.get()
        vacancia_value = self.vacancia_max_var.get()

        criteria = FiiFilterCriteria(
            dy_min=self.dy_min_var.get() or None,
            pvp_max=pvp_value if pvp_value < PVP_MAX_LIMIT else None,
            liquidez_min=self.liquidez_min_var.get() or None,
            segmento=self.segmento_var.get(),
            ffo_yield_min=self.ffo_yield_min_var.get() or None,
            valor_mercado_min=self.valor_mercado_min_var.get() or None,
            qtd_imoveis_min=self.qtd_imoveis_min_var.get() or None,
            cap_rate_min=self.cap_rate_min_var.get() or None,
            vacancia_max=vacancia_value if vacancia_value < VACANCIA_MAX_LIMIT else None,
            ticker=self.ticker_var.get().strip() or None,
        )

        filtered = self.filter_engine.apply(self.raw_df, criteria)
        self._show_dataframe(filtered)
        self.status_var.set(f"{len(filtered)} de {len(self.raw_df)} FIIs após aplicar os filtros.")

    def on_clear_filters_clicked(self):
        self.dy_min_var.set(0.0)
        self.pvp_max_var.set(PVP_MAX_LIMIT)
        self.liquidez_min_var.set(0.0)
        self.segmento_var.set(TODOS_SEGMENTOS)
        self.ffo_yield_min_var.set(0.0)
        self.valor_mercado_min_var.set(0.0)
        self.qtd_imoveis_min_var.set(0)
        self.cap_rate_min_var.set(0.0)
        self.vacancia_max_var.set(VACANCIA_MAX_LIMIT)
        self.ticker_var.set("")

        if self.raw_df is not None:
            self._show_dataframe(self.raw_df)
            self.status_var.set(f"{len(self.raw_df)} FIIs (sem filtros).")

    # ------------------------------------------------------------------
    # Saving
    # ------------------------------------------------------------------
    def on_save_clicked(self):
        if self.filtered_df.empty:
            messagebox.showinfo("Nada para salvar", "Não há dados para salvar.")
            return

        path = filedialog.asksaveasfilename(
            title="Salvar como XLSX",
            defaultextension=".xlsx",
            initialfile="fiis.xlsx",
            filetypes=[("Planilhas Excel", "*.xlsx")],
        )
        if not path:
            return

        try:
            self.writer.save_as(self.filtered_df, path)
        except Exception as exc:
            messagebox.showerror("Erro ao salvar", str(exc))
            return

        self.status_var.set(f"Arquivo salvo em: {path}")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _show_dataframe(self, df: pd.DataFrame):
        self.filtered_df = df
        self.table.set_dataframe(df)
        self.row_count_var.set(f"{len(df)} FIIs")
