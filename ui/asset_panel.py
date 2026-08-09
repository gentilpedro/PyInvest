import queue
import tkinter as tk
from dataclasses import dataclass, field
from tkinter import filedialog
from typing import Any, Callable, Optional

import pandas as pd
import ttkbootstrap as ttk
from ttkbootstrap.constants import INFO, OUTLINE, PRIMARY, SECONDARY, SUCCESS
from ttkbootstrap.dialogs import Messagebox, Querybox

from infra.writers.excel_writer import ExcelWriter
from ui.fetch_worker import FetchWorker
from ui.fii_table import SCORE_HIGH_COLOR, SCORE_HIGH_THRESHOLD, SCORE_LOW_COLOR, SCORE_LOW_THRESHOLD, FiiTable


@dataclass
class FilterField:
    """Declarative spec for one filter field, bound to a criteria dataclass attribute."""

    attr: str
    label: str
    kind: str  # "double" | "int" | "combobox" | "entry"
    no_filter_value: Any
    widget_kwargs: dict = field(default_factory=dict)


class AssetPanel(ttk.Frame):
    """Self-contained tab: filter panel + presets + fetch/apply/save actions + table.

    One instance is built per asset type (FIIs, Ações, ...); each keeps its own
    data, so switching tabs never clears the other tab's results.
    """

    def __init__(
        self,
        master,
        *,
        asset_noun: str,
        fetch_callable_factory: Callable[[], Callable[[], pd.DataFrame]],
        filter_engine,
        ranking_engine,
        criteria_cls,
        field_specs: list[FilterField],
        preset_store,
        default_export_filename: str,
        columns: int = 3,
        segments_field_attr: Optional[str] = None,
        segments_fn: Optional[Callable[[pd.DataFrame], list[str]]] = None,
    ):
        super().__init__(master, padding=16)
        self.asset_noun = asset_noun
        self.fetch_callable_factory = fetch_callable_factory
        self.filter_engine = filter_engine
        self.ranking_engine = ranking_engine
        self.criteria_cls = criteria_cls
        self.field_specs = field_specs
        self.preset_store = preset_store
        self.default_export_filename = default_export_filename
        self.columns = columns
        self.segments_field_attr = segments_field_attr
        self.segments_fn = segments_fn

        self.writer = ExcelWriter()
        self.raw_df: Optional[pd.DataFrame] = None
        self.filtered_df: pd.DataFrame = pd.DataFrame()
        self.result_queue: Optional["queue.Queue"] = None

        self._vars: dict[str, tk.Variable] = {}
        self._widgets: dict[str, tk.Widget] = {}

        self.preset_var = tk.StringVar(value="")
        self.row_count_var = tk.StringVar(value=f"0 {asset_noun}")
        self.status_var = tk.StringVar(value='Pronto. Clique em "Buscar dados" para começar.')

        self._build_ui()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------
    def _build_ui(self):
        self._build_filter_panel()
        self._build_actions_row()
        ttk.Separator(self).pack(fill="x", pady=(4, 10))
        self._build_table()
        self._build_status_bar()

    def _build_filter_panel(self):
        panel = ttk.Labelframe(self, text=f"Filtros de {self.asset_noun}", padding=14)
        panel.pack(fill="x", pady=(0, 12))

        for i, spec in enumerate(self.field_specs):
            row, col = divmod(i, self.columns)
            ttk.Label(panel, text=spec.label).grid(
                row=row, column=col * 2, padx=(0 if col == 0 else 22, 6), pady=8, sticky="w"
            )
            var = self._make_var(spec)
            self._vars[spec.attr] = var
            widget = self._make_widget(panel, spec, var)
            widget.grid(row=row, column=col * 2 + 1, padx=6, pady=8, sticky="w")
            self._widgets[spec.attr] = widget

        preset_row = (len(self.field_specs) + self.columns - 1) // self.columns
        ttk.Separator(panel).grid(
            row=preset_row, column=0, columnspan=self.columns * 2, sticky="ew", pady=(12, 10)
        )

        ttk.Label(panel, text="Preset:").grid(row=preset_row + 1, column=0, padx=(0, 6), pady=4, sticky="w")
        self.preset_combo = ttk.Combobox(
            panel, textvariable=self.preset_var, state="readonly", values=self.preset_store.list_names(), width=18
        )
        self.preset_combo.grid(row=preset_row + 1, column=1, padx=6, pady=4, sticky="w")

        self.load_preset_button = ttk.Button(
            panel, text="Carregar preset", command=self.on_load_preset_clicked, bootstyle=(INFO, OUTLINE)
        )
        self.load_preset_button.grid(row=preset_row + 1, column=2, padx=(18, 6), pady=4, sticky="w")
        self.save_preset_button = ttk.Button(
            panel, text="Salvar preset...", command=self.on_save_preset_clicked, bootstyle=(SUCCESS, OUTLINE)
        )
        self.save_preset_button.grid(row=preset_row + 1, column=3, padx=6, pady=4, sticky="w")
        self.delete_preset_button = ttk.Button(
            panel, text="Excluir preset", command=self.on_delete_preset_clicked, bootstyle=(SECONDARY, OUTLINE)
        )
        self.delete_preset_button.grid(row=preset_row + 1, column=4, padx=6, pady=4, sticky="w")

        self.preset_widgets = [
            self.preset_combo, self.load_preset_button, self.save_preset_button, self.delete_preset_button
        ]

    def _make_var(self, spec: FilterField) -> tk.Variable:
        if spec.kind == "int":
            return tk.IntVar(value=spec.no_filter_value)
        if spec.kind == "double":
            return tk.DoubleVar(value=spec.no_filter_value)
        return tk.StringVar(value=spec.no_filter_value)

    def _make_widget(self, panel, spec: FilterField, var: tk.Variable):
        if spec.kind in ("double", "int"):
            return ttk.Spinbox(panel, textvariable=var, **spec.widget_kwargs)
        if spec.kind == "combobox":
            return ttk.Combobox(panel, textvariable=var, **spec.widget_kwargs)
        return ttk.Entry(panel, textvariable=var, **spec.widget_kwargs)

    def _build_actions_row(self):
        row = ttk.Frame(self)
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

    def _build_table(self):
        self.score_legend = legend = ttk.Frame(self)
        ttk.Label(legend, text="  ", background=SCORE_HIGH_COLOR, relief="solid", borderwidth=1).pack(side="left")
        ttk.Label(legend, text=f" Score ≥ {SCORE_HIGH_THRESHOLD}", bootstyle=SECONDARY).pack(side="left", padx=(4, 16))
        ttk.Label(legend, text="  ", background=SCORE_LOW_COLOR, relief="solid", borderwidth=1).pack(side="left")
        ttk.Label(legend, text=f" Score ≤ {SCORE_LOW_THRESHOLD}", bootstyle=SECONDARY).pack(side="left", padx=(4, 0))

        self.table = FiiTable(self)
        self.table.pack(fill="both", expand=True)

    def _build_status_bar(self):
        bar = ttk.Frame(self, padding=(0, 6, 0, 0))
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
        self.status_var.set(f"Buscando {self.asset_noun} no Fundamentus... isso pode levar alguns segundos.")
        self.config(cursor="watch")

        self.result_queue = queue.Queue()
        worker = FetchWorker(self.fetch_callable_factory(), self.result_queue)
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
        self.save_button.configure(state="normal")

        self.raw_df = self.ranking_engine.add_score(df)

        if self.segments_field_attr and self.segments_fn:
            values = [self._widgets[self.segments_field_attr].cget("values")[0]] + self.segments_fn(self.raw_df)
            self._widgets[self.segments_field_attr].configure(values=values)
            self._vars[self.segments_field_attr].set(values[0])

        self._set_filter_features_enabled(True)
        self._show_dataframe(self.raw_df)
        self.status_var.set(f"{len(self.raw_df)} {self.asset_noun} carregados.")

    def _on_fetch_failed(self, message: str):
        self.config(cursor="")
        self.fetch_button.configure(state="normal")
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

        for widget in self.preset_widgets:
            if isinstance(widget, ttk.Combobox):
                widget.configure(state=combo_state)
            else:
                widget.configure(state=widget_state)

    # ------------------------------------------------------------------
    # Filtering
    # ------------------------------------------------------------------
    def criteria_from_vars(self):
        kwargs = {}
        for spec in self.field_specs:
            value = self._vars[spec.attr].get()
            if spec.kind == "entry":
                value = value.strip()
            kwargs[spec.attr] = None if value == spec.no_filter_value else value
        return self.criteria_cls(**kwargs)

    def apply_criteria_to_vars(self, criteria):
        for spec in self.field_specs:
            value = getattr(criteria, spec.attr)
            self._vars[spec.attr].set(spec.no_filter_value if value is None else value)

    def on_apply_filters_clicked(self):
        if self.raw_df is None:
            return

        criteria = self.criteria_from_vars()
        filtered = self.filter_engine.apply(self.raw_df, criteria)
        self._show_dataframe(filtered)
        self.status_var.set(f"{len(filtered)} de {len(self.raw_df)} {self.asset_noun} após aplicar os filtros.")

    def on_clear_filters_clicked(self):
        self.apply_criteria_to_vars(self.criteria_cls())

        if self.raw_df is not None:
            self._show_dataframe(self.raw_df)
            self.status_var.set(f"{len(self.raw_df)} {self.asset_noun} (sem filtros).")

    # ------------------------------------------------------------------
    # Filter presets
    # ------------------------------------------------------------------
    def on_save_preset_clicked(self):
        name = Querybox.get_string(prompt="Nome do preset:", title="Salvar preset de filtros", parent=self)
        name = (name or "").strip()
        if not name:
            return

        self.preset_store.save(name, self.criteria_from_vars())
        self.preset_combo.configure(values=self.preset_store.list_names())
        self.preset_var.set(name)
        self.status_var.set(f'Preset "{name}" salvo.')

    def on_load_preset_clicked(self):
        name = self.preset_var.get()
        if not name:
            Messagebox.show_info("Selecione um preset na lista.", "Nenhum preset selecionado", parent=self)
            return

        criteria = self.preset_store.load(name)
        self.apply_criteria_to_vars(criteria)

        if self.raw_df is not None:
            self.on_apply_filters_clicked()
        self.status_var.set(f'Preset "{name}" carregado.')

    def on_delete_preset_clicked(self):
        name = self.preset_var.get()
        if not name:
            Messagebox.show_info("Selecione um preset na lista.", "Nenhum preset selecionado", parent=self)
            return

        confirmed = Messagebox.yesno(f'Excluir o preset "{name}"?', "Confirmar exclusão", parent=self)
        if confirmed != "Yes":
            return

        self.preset_store.delete(name)
        self.preset_combo.configure(values=self.preset_store.list_names())
        self.preset_var.set("")
        self.status_var.set(f'Preset "{name}" excluído.')

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
            initialfile=self.default_export_filename,
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
        self.row_count_var.set(f"{len(df)} {self.asset_noun}")
