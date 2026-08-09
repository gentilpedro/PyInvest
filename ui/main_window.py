import queue
import tkinter as tk

import pandas as pd
import ttkbootstrap as ttk
from ttkbootstrap.constants import INFO, OUTLINE, PRIMARY, SECONDARY, SUCCESS
from ttkbootstrap.dialogs import Messagebox, Querybox
from tkinter import filedialog

from app.domain.filters.fii_filter import FiiFilter, FiiFilterCriteria
from app.domain.filters.stock_filter import StockFilter, StockFilterCriteria
from app.domain.ranking.fii_ranking import FiiRanking
from app.domain.ranking.stock_ranking import StockRanking
from app.use_cases.fetch_fiis import FetchFiisUseCase
from app.use_cases.fetch_stocks import FetchStocksUseCase
from infra.storage.filter_preset_store import FilterPresetStore
from infra.writers.excel_writer import ExcelWriter
from ui.fetch_worker import FetchWorker
from ui.fii_table import SCORE_HIGH_COLOR, SCORE_HIGH_THRESHOLD, SCORE_LOW_COLOR, SCORE_LOW_THRESHOLD, FiiTable
from ui.resources import resource_path

TODOS_SEGMENTOS = "Todos"
PVP_MAX_LIMIT = 100.0
VACANCIA_MAX_LIMIT = 100.0
PL_MAX_LIMIT = 500.0
DIVIDA_PATRIMONIO_MAX_LIMIT = 50.0
THEME = "flatly"
ASSET_FIIS = "FIIs"
ASSET_STOCKS = "Ações"


class MainWindow(ttk.Window):
    def __init__(self):
        super().__init__(
            title="PyInvest — Ranking de FIIs e Ações", theme=THEME, size=(1300, 800), resizable=(True, True)
        )
        self._set_icon()

        self.raw_df: pd.DataFrame | None = None
        self.filtered_df: pd.DataFrame = pd.DataFrame()

        self.filter_engine = FiiFilter()
        self.ranking_engine = FiiRanking()
        self.stock_filter_engine = StockFilter()
        self.stock_ranking_engine = StockRanking()
        self.writer = ExcelWriter()
        self.fii_preset_store = FilterPresetStore(FiiFilterCriteria)
        self.stock_preset_store = FilterPresetStore(StockFilterCriteria, filename="stock_filter_presets.json")
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
        self.fii_preset_var = tk.StringVar(value="")

        self.stock_dy_min_var = tk.DoubleVar(value=0.0)
        self.stock_pl_max_var = tk.DoubleVar(value=PL_MAX_LIMIT)
        self.stock_pvp_max_var = tk.DoubleVar(value=PVP_MAX_LIMIT)
        self.stock_roe_min_var = tk.DoubleVar(value=0.0)
        self.stock_roic_min_var = tk.DoubleVar(value=0.0)
        self.stock_margem_liquida_min_var = tk.DoubleVar(value=0.0)
        self.stock_divida_patrimonio_max_var = tk.DoubleVar(value=DIVIDA_PATRIMONIO_MAX_LIMIT)
        self.stock_liquidez_min_var = tk.DoubleVar(value=0.0)
        self.stock_patrimonio_liquido_min_var = tk.DoubleVar(value=0.0)
        self.stock_ticker_var = tk.StringVar(value="")
        self.stock_preset_var = tk.StringVar(value="")

        self.asset_type_var = tk.StringVar(value=ASSET_FIIS)
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
        self.fii_filter_frame = self._build_fii_filter_panel(parent)
        self.stock_filter_frame = self._build_stock_filter_panel(parent)
        self.stock_filter_frame.pack_forget()

    def _build_fii_filter_panel(self, parent) -> ttk.Labelframe:
        panel = ttk.Labelframe(parent, text="Filtros de FIIs", padding=14)
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

        widgets = self._add_fields(panel, fields)
        self.segmento_combo = widgets[8]
        self.fii_filter_widgets = widgets

        preset_row = 4
        ttk.Separator(panel).grid(row=preset_row, column=0, columnspan=6, sticky="ew", pady=(12, 10))
        (
            self.fii_preset_combo, self.fii_load_preset_button,
            self.fii_save_preset_button, self.fii_delete_preset_button,
        ) = self._build_preset_row(
            panel, preset_row + 1, self.fii_preset_var, self.fii_preset_store,
            on_load=self.on_load_fii_preset_clicked,
            on_save=self.on_save_fii_preset_clicked,
            on_delete=self.on_delete_fii_preset_clicked,
        )
        self.fii_preset_widgets = [
            self.fii_preset_combo, self.fii_load_preset_button,
            self.fii_save_preset_button, self.fii_delete_preset_button,
        ]

        return panel

    def _build_stock_filter_panel(self, parent) -> ttk.Labelframe:
        panel = ttk.Labelframe(parent, text="Filtros de Ações", padding=14)
        panel.pack(fill="x", pady=(0, 12))

        fields = [
            ("Dividend Yield mínimo (%):", lambda p: ttk.Spinbox(
                p, textvariable=self.stock_dy_min_var, width=10, from_=0, to=100, increment=0.1
            )),
            ("P/L máximo:", lambda p: ttk.Spinbox(
                p, textvariable=self.stock_pl_max_var, width=10, from_=0, to=PL_MAX_LIMIT, increment=0.5
            )),
            ("P/VP máximo:", lambda p: ttk.Spinbox(
                p, textvariable=self.stock_pvp_max_var, width=10, from_=0, to=PVP_MAX_LIMIT, increment=0.01
            )),
            ("ROE mínimo (%):", lambda p: ttk.Spinbox(
                p, textvariable=self.stock_roe_min_var, width=10, from_=0, to=100, increment=0.5
            )),
            ("ROIC mínimo (%):", lambda p: ttk.Spinbox(
                p, textvariable=self.stock_roic_min_var, width=10, from_=0, to=100, increment=0.5
            )),
            ("Margem Líquida mínima (%):", lambda p: ttk.Spinbox(
                p, textvariable=self.stock_margem_liquida_min_var, width=10, from_=0, to=100, increment=0.5
            )),
            ("Dívida/Patrimônio máximo:", lambda p: ttk.Spinbox(
                p, textvariable=self.stock_divida_patrimonio_max_var, width=10,
                from_=0, to=DIVIDA_PATRIMONIO_MAX_LIMIT, increment=0.1,
            )),
            ("Liquidez (2 meses) mínima (R$):", lambda p: ttk.Spinbox(
                p, textvariable=self.stock_liquidez_min_var, width=14, from_=0, to=1_000_000_000, increment=1000
            )),
            ("Patrimônio Líquido mínimo (R$):", lambda p: ttk.Spinbox(
                p, textvariable=self.stock_patrimonio_liquido_min_var, width=16,
                from_=0, to=100_000_000_000, increment=1_000_000,
            )),
            ("Buscar ticker:", lambda p: ttk.Entry(p, textvariable=self.stock_ticker_var, width=14)),
        ]

        widgets = self._add_fields(panel, fields)
        self.stock_filter_widgets = widgets

        preset_row = 4
        ttk.Separator(panel).grid(row=preset_row, column=0, columnspan=6, sticky="ew", pady=(12, 10))
        (
            self.stock_preset_combo, self.stock_load_preset_button,
            self.stock_save_preset_button, self.stock_delete_preset_button,
        ) = self._build_preset_row(
            panel, preset_row + 1, self.stock_preset_var, self.stock_preset_store,
            on_load=self.on_load_stock_preset_clicked,
            on_save=self.on_save_stock_preset_clicked,
            on_delete=self.on_delete_stock_preset_clicked,
        )
        self.stock_preset_widgets = [
            self.stock_preset_combo, self.stock_load_preset_button,
            self.stock_save_preset_button, self.stock_delete_preset_button,
        ]

        return panel

    def _add_fields(self, panel, fields):
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
        return widgets

    def _build_preset_row(self, panel, row, preset_var, preset_store, on_load, on_save, on_delete):
        ttk.Label(panel, text="Preset:").grid(row=row, column=0, padx=(0, 6), pady=4, sticky="w")
        combo = ttk.Combobox(
            panel, textvariable=preset_var, state="readonly", values=preset_store.list_names(), width=18
        )
        combo.grid(row=row, column=1, padx=6, pady=4, sticky="w")

        load_btn = ttk.Button(panel, text="Carregar preset", command=on_load, bootstyle=(INFO, OUTLINE))
        load_btn.grid(row=row, column=2, padx=(18, 6), pady=4, sticky="w")
        save_btn = ttk.Button(panel, text="Salvar preset...", command=on_save, bootstyle=(SUCCESS, OUTLINE))
        save_btn.grid(row=row, column=3, padx=6, pady=4, sticky="w")
        delete_btn = ttk.Button(panel, text="Excluir preset", command=on_delete, bootstyle=(SECONDARY, OUTLINE))
        delete_btn.grid(row=row, column=4, padx=6, pady=4, sticky="w")

        return combo, load_btn, save_btn, delete_btn

    def _build_actions_row(self, parent):
        row = ttk.Frame(parent)
        row.pack(fill="x", pady=(0, 4))
        self.actions_row = row

        ttk.Label(row, text="Tipo:").pack(side="left", padx=(0, 6))
        self.asset_type_combo = ttk.Combobox(
            row, textvariable=self.asset_type_var, state="readonly",
            values=[ASSET_FIIS, ASSET_STOCKS], width=8,
        )
        self.asset_type_combo.pack(side="left", padx=(0, 12))
        self.asset_type_combo.bind("<<ComboboxSelected>>", self.on_asset_type_changed)

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
        self.score_legend = legend = ttk.Frame(parent)
        legend.pack(fill="x", pady=(0, 4))
        ttk.Label(
            legend, text="  ", background=SCORE_HIGH_COLOR, relief="solid", borderwidth=1
        ).pack(side="left")
        ttk.Label(legend, text=f" Score ≥ {SCORE_HIGH_THRESHOLD}", bootstyle=SECONDARY).pack(side="left", padx=(4, 16))
        ttk.Label(
            legend, text="  ", background=SCORE_LOW_COLOR, relief="solid", borderwidth=1
        ).pack(side="left")
        ttk.Label(legend, text=f" Score ≤ {SCORE_LOW_THRESHOLD}", bootstyle=SECONDARY).pack(side="left", padx=(4, 0))
        legend.pack_forget()

        self.table = FiiTable(parent)
        self.table.pack(fill="both", expand=True)

    def _build_status_bar(self):
        bar = ttk.Frame(self, padding=(16, 6))
        bar.pack(fill="x", side="bottom")
        ttk.Label(bar, textvariable=self.status_var, bootstyle=SECONDARY).pack(side="left")

    # ------------------------------------------------------------------
    # Asset type
    # ------------------------------------------------------------------
    def _is_fiis_selected(self) -> bool:
        return self.asset_type_var.get() == ASSET_FIIS

    def on_asset_type_changed(self, event=None):
        if self._is_fiis_selected():
            self.stock_filter_frame.pack_forget()
            self.fii_filter_frame.pack(fill="x", pady=(0, 12), before=self.actions_row)
        else:
            self.fii_filter_frame.pack_forget()
            self.stock_filter_frame.pack(fill="x", pady=(0, 12), before=self.actions_row)

        self.raw_df = None
        self._set_filter_features_enabled(False)
        self.save_button.configure(state="disabled")
        self._show_dataframe(pd.DataFrame())
        self.status_var.set(f'Pronto. Clique em "Buscar dados" para buscar {self.asset_type_var.get()}.')

    # ------------------------------------------------------------------
    # Fetching
    # ------------------------------------------------------------------
    def on_fetch_clicked(self):
        self.fetch_button.configure(state="disabled")
        self.asset_type_combo.configure(state="disabled")
        self.apply_filters_button.configure(state="disabled")
        self.clear_filters_button.configure(state="disabled")
        self.save_button.configure(state="disabled")
        asset_label = self.asset_type_var.get()
        self.status_var.set(f"Buscando {asset_label} no Fundamentus... isso pode levar alguns segundos.")
        self.config(cursor="watch")

        fetch_callable = (
            FetchFiisUseCase().execute if self._is_fiis_selected() else FetchStocksUseCase().execute
        )
        self.result_queue = queue.Queue()
        worker = FetchWorker(fetch_callable, self.result_queue)
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
        self.asset_type_combo.configure(state="readonly")
        self.save_button.configure(state="normal")

        if self._is_fiis_selected():
            self.raw_df = self.ranking_engine.add_score(df)
            segments = [TODOS_SEGMENTOS] + self.filter_engine.segments(self.raw_df)
            self.segmento_combo.configure(values=segments)
            self.segmento_var.set(TODOS_SEGMENTOS)
        else:
            self.raw_df = self.stock_ranking_engine.add_score(df)

        self._set_filter_features_enabled(True)
        self._show_dataframe(self.raw_df)
        self.status_var.set(f"{len(self.raw_df)} {self.asset_type_var.get()} carregados.")

    def _on_fetch_failed(self, message: str):
        self.config(cursor="")
        self.fetch_button.configure(state="normal")
        self.asset_type_combo.configure(state="readonly")
        self.status_var.set("Falha ao buscar dados.")
        Messagebox.show_error(message, "Erro ao buscar dados", parent=self)

    def _set_filter_features_enabled(self, enabled: bool):
        widget_state = "normal" if enabled else "disabled"
        combo_state = "readonly" if enabled else "disabled"

        if enabled:
            self.score_legend.pack(fill="x", pady=(0, 4), before=self.table)
        else:
            self.score_legend.pack_forget()

        self.apply_filters_button.configure(state=widget_state)
        self.clear_filters_button.configure(state=widget_state)

        active_preset_widgets = self.fii_preset_widgets if self._is_fiis_selected() else self.stock_preset_widgets
        for widget in active_preset_widgets:
            if isinstance(widget, ttk.Combobox):
                widget.configure(state=combo_state)
            else:
                widget.configure(state=widget_state)

    # ------------------------------------------------------------------
    # Filtering
    # ------------------------------------------------------------------
    def _fii_criteria_from_vars(self) -> FiiFilterCriteria:
        pvp_value = self.pvp_max_var.get()
        vacancia_value = self.vacancia_max_var.get()

        return FiiFilterCriteria(
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

    def _apply_fii_criteria_to_vars(self, criteria: FiiFilterCriteria):
        self.dy_min_var.set(criteria.dy_min or 0.0)
        self.pvp_max_var.set(criteria.pvp_max if criteria.pvp_max is not None else PVP_MAX_LIMIT)
        self.liquidez_min_var.set(criteria.liquidez_min or 0.0)
        self.segmento_var.set(criteria.segmento or TODOS_SEGMENTOS)
        self.ffo_yield_min_var.set(criteria.ffo_yield_min or 0.0)
        self.valor_mercado_min_var.set(criteria.valor_mercado_min or 0.0)
        self.qtd_imoveis_min_var.set(criteria.qtd_imoveis_min or 0)
        self.cap_rate_min_var.set(criteria.cap_rate_min or 0.0)
        self.vacancia_max_var.set(criteria.vacancia_max if criteria.vacancia_max is not None else VACANCIA_MAX_LIMIT)
        self.ticker_var.set(criteria.ticker or "")

    def _stock_criteria_from_vars(self) -> StockFilterCriteria:
        pl_value = self.stock_pl_max_var.get()
        pvp_value = self.stock_pvp_max_var.get()
        divida_value = self.stock_divida_patrimonio_max_var.get()

        return StockFilterCriteria(
            dy_min=self.stock_dy_min_var.get() or None,
            pl_max=pl_value if pl_value < PL_MAX_LIMIT else None,
            pvp_max=pvp_value if pvp_value < PVP_MAX_LIMIT else None,
            roe_min=self.stock_roe_min_var.get() or None,
            roic_min=self.stock_roic_min_var.get() or None,
            margem_liquida_min=self.stock_margem_liquida_min_var.get() or None,
            divida_patrimonio_max=divida_value if divida_value < DIVIDA_PATRIMONIO_MAX_LIMIT else None,
            liquidez_min=self.stock_liquidez_min_var.get() or None,
            patrimonio_liquido_min=self.stock_patrimonio_liquido_min_var.get() or None,
            ticker=self.stock_ticker_var.get().strip() or None,
        )

    def _apply_stock_criteria_to_vars(self, criteria: StockFilterCriteria):
        self.stock_dy_min_var.set(criteria.dy_min or 0.0)
        self.stock_pl_max_var.set(criteria.pl_max if criteria.pl_max is not None else PL_MAX_LIMIT)
        self.stock_pvp_max_var.set(criteria.pvp_max if criteria.pvp_max is not None else PVP_MAX_LIMIT)
        self.stock_roe_min_var.set(criteria.roe_min or 0.0)
        self.stock_roic_min_var.set(criteria.roic_min or 0.0)
        self.stock_margem_liquida_min_var.set(criteria.margem_liquida_min or 0.0)
        self.stock_divida_patrimonio_max_var.set(
            criteria.divida_patrimonio_max
            if criteria.divida_patrimonio_max is not None
            else DIVIDA_PATRIMONIO_MAX_LIMIT
        )
        self.stock_liquidez_min_var.set(criteria.liquidez_min or 0.0)
        self.stock_patrimonio_liquido_min_var.set(criteria.patrimonio_liquido_min or 0.0)
        self.stock_ticker_var.set(criteria.ticker or "")

    def on_apply_filters_clicked(self):
        if self.raw_df is None:
            return

        if self._is_fiis_selected():
            criteria = self._fii_criteria_from_vars()
            filtered = self.filter_engine.apply(self.raw_df, criteria)
        else:
            criteria = self._stock_criteria_from_vars()
            filtered = self.stock_filter_engine.apply(self.raw_df, criteria)

        self._show_dataframe(filtered)
        asset_label = self.asset_type_var.get()
        self.status_var.set(f"{len(filtered)} de {len(self.raw_df)} {asset_label} após aplicar os filtros.")

    def on_clear_filters_clicked(self):
        if self._is_fiis_selected():
            self._apply_fii_criteria_to_vars(FiiFilterCriteria())
        else:
            self._apply_stock_criteria_to_vars(StockFilterCriteria())

        if self.raw_df is not None:
            self._show_dataframe(self.raw_df)
            self.status_var.set(f"{len(self.raw_df)} {self.asset_type_var.get()} (sem filtros).")

    # ------------------------------------------------------------------
    # Filter presets
    # ------------------------------------------------------------------
    def on_save_fii_preset_clicked(self):
        self._save_preset(self.fii_preset_store, self.fii_preset_var, self.fii_preset_combo, self._fii_criteria_from_vars())

    def on_load_fii_preset_clicked(self):
        self._load_preset(self.fii_preset_store, self.fii_preset_var, self._apply_fii_criteria_to_vars)

    def on_delete_fii_preset_clicked(self):
        self._delete_preset(self.fii_preset_store, self.fii_preset_var, self.fii_preset_combo)

    def on_save_stock_preset_clicked(self):
        self._save_preset(
            self.stock_preset_store, self.stock_preset_var, self.stock_preset_combo, self._stock_criteria_from_vars()
        )

    def on_load_stock_preset_clicked(self):
        self._load_preset(self.stock_preset_store, self.stock_preset_var, self._apply_stock_criteria_to_vars)

    def on_delete_stock_preset_clicked(self):
        self._delete_preset(self.stock_preset_store, self.stock_preset_var, self.stock_preset_combo)

    def _save_preset(self, store, preset_var, preset_combo, criteria):
        name = Querybox.get_string(prompt="Nome do preset:", title="Salvar preset de filtros", parent=self)
        name = (name or "").strip()
        if not name:
            return

        store.save(name, criteria)
        preset_combo.configure(values=store.list_names())
        preset_var.set(name)
        self.status_var.set(f'Preset "{name}" salvo.')

    def _load_preset(self, store, preset_var, apply_criteria_to_vars):
        name = preset_var.get()
        if not name:
            Messagebox.show_info("Selecione um preset na lista.", "Nenhum preset selecionado", parent=self)
            return

        criteria = store.load(name)
        apply_criteria_to_vars(criteria)

        if self.raw_df is not None:
            self.on_apply_filters_clicked()
        self.status_var.set(f'Preset "{name}" carregado.')

    def _delete_preset(self, store, preset_var, preset_combo):
        name = preset_var.get()
        if not name:
            Messagebox.show_info("Selecione um preset na lista.", "Nenhum preset selecionado", parent=self)
            return

        confirmed = Messagebox.yesno(f'Excluir o preset "{name}"?', "Confirmar exclusão", parent=self)
        if confirmed != "Yes":
            return

        store.delete(name)
        preset_combo.configure(values=store.list_names())
        preset_var.set("")
        self.status_var.set(f'Preset "{name}" excluído.')

    # ------------------------------------------------------------------
    # Saving
    # ------------------------------------------------------------------
    def on_save_clicked(self):
        if self.filtered_df.empty:
            Messagebox.show_info("Não há dados para salvar.", "Nada para salvar", parent=self)
            return

        default_name = "fiis.xlsx" if self._is_fiis_selected() else "acoes.xlsx"
        path = filedialog.asksaveasfilename(
            title="Salvar como XLSX",
            defaultextension=".xlsx",
            initialfile=default_name,
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
        self.row_count_var.set(f"{len(df)} {self.asset_type_var.get()}")
