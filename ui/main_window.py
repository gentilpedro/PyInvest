import queue
import tkinter as tk

import pandas as pd
import ttkbootstrap as ttk
from ttkbootstrap.constants import INFO, OUTLINE, PRIMARY, SECONDARY, SUCCESS
from ttkbootstrap.dialogs import Messagebox
from tkinter import filedialog

from app.domain.filters.fii_filter import FiiFilter, FiiFilterCriteria
from infra.writers.excel_writer import ExcelWriter
from ui.fetch_worker import FetchFiisWorker
from ui.fii_table import FiiTable
from ui.resources import resource_path

TODOS_SEGMENTOS = "Todos"
PVP_MAX_LIMIT = 100.0
VACANCIA_MAX_LIMIT = 100.0
THEME = "flatly"


class MainWindow(ttk.Window):
    def __init__(self):
        super().__init__(title="PyInvest — Ranking de FIIs", theme=THEME, size=(1300, 760), resizable=(True, True))
        self._set_icon()

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
        self.row_count_var = tk.StringVar(value="0 FIIs")
        self.status_var = tk.StringVar(value='Pronto. Clique em "Buscar dados" para começar.')

        self._build_ui()

    def _set_icon(self):
        icon_path = resource_path("assets/icon.ico")
        if icon_path.exists():
            try:
                self.iconbitmap(icon_path)
            except tk.TclError:
                pass

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------
    def _build_ui(self):
        container = ttk.Frame(self, padding=16)
        container.pack(fill="both", expand=True)

        self._build_filter_panel(container)
        self._build_actions_row(container)
        ttk.Separator(container).pack(fill="x", pady=(4, 10))
        self._build_table(container)
        self._build_status_bar()

    def _build_filter_panel(self, parent):
        panel = ttk.Labelframe(parent, text="Filtros", padding=14)
        panel.pack(fill="x", pady=(0, 12))

        fields = [
            ("Dividend Yield mínimo (%):", lambda p: ttk.Spinbox(
                p, textvariable=self.dy_min_var, width=10, from_=0, to=100, increment=0.1
            )),
            ("P/VP máximo:", lambda p: ttk.Spinbox(
                p, textvariable=self.pvp_max_var, width=10, from_=0, to=PVP_MAX_LIMIT, increment=0.01
            )),
            ("Liquidez diária mínima (R$):", lambda p: ttk.Spinbox(
                p, textvariable=self.liquidez_min_var, width=14, from_=0, to=1_000_000_000, increment=1000
            )),
            ("FFO Yield mínimo (%):", lambda p: ttk.Spinbox(
                p, textvariable=self.ffo_yield_min_var, width=10, from_=0, to=100, increment=0.1
            )),
            ("Valor de Mercado mínimo (R$):", lambda p: ttk.Spinbox(
                p, textvariable=self.valor_mercado_min_var, width=16,
                from_=0, to=100_000_000_000, increment=1_000_000,
            )),
            ("Qtd de imóveis mínima:", lambda p: ttk.Spinbox(
                p, textvariable=self.qtd_imoveis_min_var, width=10, from_=0, to=1000, increment=1
            )),
            ("Cap Rate mínimo (%):", lambda p: ttk.Spinbox(
                p, textvariable=self.cap_rate_min_var, width=10, from_=0, to=100, increment=0.1
            )),
            ("Vacância máxima (%):", lambda p: ttk.Spinbox(
                p, textvariable=self.vacancia_max_var, width=10, from_=0, to=VACANCIA_MAX_LIMIT, increment=0.5
            )),
            ("Segmento:", lambda p: ttk.Combobox(
                p, textvariable=self.segmento_var, state="readonly", values=[TODOS_SEGMENTOS], width=18
            )),
            ("Buscar ticker:", lambda p: ttk.Entry(p, textvariable=self.ticker_var, width=14)),
        ]

        columns = 3
        widgets = []
        for i, (label_text, factory) in enumerate(fields):
            row, col = divmod(i, columns)
            ttk.Label(panel, text=label_text).grid(
                row=row, column=col * 2, padx=(0 if col == 0 else 24, 6), pady=8, sticky="w"
            )
            widget = factory(panel)
            widget.grid(row=row, column=col * 2 + 1, padx=6, pady=8, sticky="w")
            widgets.append(widget)

        self.segmento_combo = widgets[8]

    def _build_actions_row(self, parent):
        row = ttk.Frame(parent)
        row.pack(fill="x", pady=(0, 4))

        self.fetch_button = ttk.Button(row, text="Buscar dados", command=self.on_fetch_clicked, bootstyle=PRIMARY)
        self.fetch_button.pack(side="left")

        self.apply_filters_button = ttk.Button(
            row, text="Aplicar filtros", command=self.on_apply_filters_clicked, bootstyle=INFO, state="disabled"
        )
        self.apply_filters_button.pack(side="left", padx=(8, 0))

        self.clear_filters_button = ttk.Button(
            row, text="Limpar filtros", command=self.on_clear_filters_clicked,
            bootstyle=(SECONDARY, OUTLINE), state="disabled",
        )
        self.clear_filters_button.pack(side="left", padx=(8, 0))

        ttk.Label(row, textvariable=self.row_count_var, bootstyle=(INFO, "inverse"), padding=(10, 4)).pack(
            side="left", padx=20
        )

        self.save_button = ttk.Button(
            row, text="Salvar como XLSX", command=self.on_save_clicked, bootstyle=SUCCESS, state="disabled"
        )
        self.save_button.pack(side="right")

    def _build_table(self, parent):
        self.table = FiiTable(parent)
        self.table.pack(fill="both", expand=True)

    def _build_status_bar(self):
        bar = ttk.Frame(self, padding=(16, 6))
        bar.pack(fill="x", side="bottom")
        ttk.Label(bar, textvariable=self.status_var, bootstyle=SECONDARY).pack(side="left")

    # ------------------------------------------------------------------
    # Fetching
    # ------------------------------------------------------------------
    def on_fetch_clicked(self):
        self.fetch_button.configure(state="disabled")
        self.apply_filters_button.configure(state="disabled")
        self.clear_filters_button.configure(state="disabled")
        self.save_button.configure(state="disabled")
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
        self.fetch_button.configure(state="normal")
        self.apply_filters_button.configure(state="normal")
        self.clear_filters_button.configure(state="normal")
        self.save_button.configure(state="normal")

        self.raw_df = df

        segments = [TODOS_SEGMENTOS] + self.filter_engine.segments(df)
        self.segmento_combo.configure(values=segments)
        self.segmento_var.set(TODOS_SEGMENTOS)

        self._show_dataframe(df)
        self.status_var.set(f"{len(df)} FIIs carregados.")

    def _on_fetch_failed(self, message: str):
        self.config(cursor="")
        self.fetch_button.configure(state="normal")
        self.status_var.set("Falha ao buscar dados.")
        Messagebox.show_error(message, "Erro ao buscar dados", parent=self)

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
            Messagebox.show_info("Não há dados para salvar.", "Nada para salvar", parent=self)
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
            Messagebox.show_error(str(exc), "Erro ao salvar", parent=self)
            return

        self.status_var.set(f"Arquivo salvo em: {path}")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _show_dataframe(self, df: pd.DataFrame):
        self.filtered_df = df
        self.table.set_dataframe(df)
        self.row_count_var.set(f"{len(df)} FIIs")
