import tkinter as tk

import ttkbootstrap as ttk

from app.domain.filters.fii_filter import FiiFilter, FiiFilterCriteria
from app.domain.filters.stock_filter import StockFilter, StockFilterCriteria
from app.domain.ranking.fii_ranking import FiiRanking
from app.domain.ranking.stock_ranking import StockRanking
from app.use_cases.fetch_fiis import FetchFiisUseCase
from app.use_cases.fetch_stocks import FetchStocksUseCase
from infra.storage.filter_preset_store import FilterPresetStore
from ui.asset_panel import AssetPanel, FilterField
from ui.resources import resource_path

TODOS_SEGMENTOS = "Todos"
PVP_MAX_LIMIT = 100.0
VACANCIA_MAX_LIMIT = 100.0
PL_MAX_LIMIT = 500.0
DIVIDA_PATRIMONIO_MAX_LIMIT = 50.0
COTACAO_MAX_LIMIT = 100_000.0
THEME = "flatly"

FII_FIELDS = [
    FilterField("dy_min", "Dividend Yield mínimo (%):", "double", 0.0, dict(from_=0, to=100, increment=0.1, width=10)),
    FilterField("pvp_max", "P/VP máximo:", "double", PVP_MAX_LIMIT, dict(from_=0, to=PVP_MAX_LIMIT, increment=0.01, width=10)),
    FilterField(
        "liquidez_min", "Liquidez diária mínima (R$):", "double", 0.0,
        dict(from_=0, to=1_000_000_000, increment=1000, width=14),
    ),
    FilterField("ffo_yield_min", "FFO Yield mínimo (%):", "double", 0.0, dict(from_=0, to=100, increment=0.1, width=10)),
    FilterField(
        "valor_mercado_min", "Valor de Mercado mínimo (R$):", "double", 0.0,
        dict(from_=0, to=100_000_000_000, increment=1_000_000, width=16),
    ),
    FilterField("qtd_imoveis_min", "Qtd de imóveis mínima:", "int", 0, dict(from_=0, to=1000, increment=1, width=10)),
    FilterField("cap_rate_min", "Cap Rate mínimo (%):", "double", 0.0, dict(from_=0, to=100, increment=0.1, width=10)),
    FilterField(
        "vacancia_max", "Vacância máxima (%):", "double", VACANCIA_MAX_LIMIT,
        dict(from_=0, to=VACANCIA_MAX_LIMIT, increment=0.5, width=10),
    ),
    FilterField(
        "segmento", "Segmento:", "combobox", TODOS_SEGMENTOS,
        dict(state="readonly", values=[TODOS_SEGMENTOS], width=18),
    ),
    FilterField("ticker", "Buscar ticker:", "entry", "", dict(width=14)),
]

STOCK_FIELDS = [
    FilterField("dy_min", "Dividend Yield mínimo (%):", "double", 0.0, dict(from_=0, to=100, increment=0.1, width=9)),
    FilterField(
        "cotacao_max", "Cotação máxima (R$):", "double", COTACAO_MAX_LIMIT,
        dict(from_=0, to=COTACAO_MAX_LIMIT, increment=1, width=9),
    ),
    FilterField("pl_max", "P/L máximo:", "double", PL_MAX_LIMIT, dict(from_=0, to=PL_MAX_LIMIT, increment=0.5, width=9)),
    FilterField("pvp_max", "P/VP máximo:", "double", PVP_MAX_LIMIT, dict(from_=0, to=PVP_MAX_LIMIT, increment=0.01, width=9)),
    FilterField("psr_max", "PSR máximo:", "double", 100.0, dict(from_=0, to=100, increment=0.1, width=9)),
    FilterField("p_ativo_max", "P/Ativo máximo:", "double", 100.0, dict(from_=0, to=100, increment=0.1, width=9)),
    FilterField("p_cap_giro_max", "P/Cap.Giro máximo:", "double", 1000.0, dict(from_=0, to=1000, increment=1, width=9)),
    FilterField("p_ebit_max", "P/EBIT máximo:", "double", 500.0, dict(from_=0, to=500, increment=0.5, width=9)),
    FilterField(
        "p_ativ_circ_liq_max", "P/Ativ Circ.Liq máximo:", "double", 1000.0,
        dict(from_=0, to=1000, increment=1, width=9),
    ),
    FilterField("ev_ebit_max", "EV/EBIT máximo:", "double", 500.0, dict(from_=0, to=500, increment=0.5, width=9)),
    FilterField("ev_ebitda_max", "EV/EBITDA máximo:", "double", 500.0, dict(from_=0, to=500, increment=0.5, width=9)),
    FilterField("margem_bruta_min", "Margem Bruta mínima (%):", "double", 0.0, dict(from_=0, to=100, increment=0.5, width=9)),
    FilterField("margem_ebit_min", "Margem EBIT mínima (%):", "double", 0.0, dict(from_=0, to=100, increment=0.5, width=9)),
    FilterField(
        "margem_liquida_min", "Margem Líquida mínima (%):", "double", 0.0, dict(from_=0, to=100, increment=0.5, width=9)
    ),
    FilterField(
        "liquidez_corrente_min", "Liquidez Corrente mínima:", "double", 0.0, dict(from_=0, to=20, increment=0.1, width=9)
    ),
    FilterField("roic_min", "ROIC mínimo (%):", "double", 0.0, dict(from_=0, to=100, increment=0.5, width=9)),
    FilterField("roe_min", "ROE mínimo (%):", "double", 0.0, dict(from_=0, to=100, increment=0.5, width=9)),
    FilterField(
        "liquidez_min", "Liquidez (2 meses) mínima (R$):", "double", 0.0,
        dict(from_=0, to=1_000_000_000, increment=1000, width=12),
    ),
    FilterField(
        "patrimonio_liquido_min", "Patrimônio Líquido mínimo (R$):", "double", 0.0,
        dict(from_=0, to=100_000_000_000, increment=1_000_000, width=14),
    ),
    FilterField(
        "divida_patrimonio_max", "Dívida/Patrimônio máximo:", "double", DIVIDA_PATRIMONIO_MAX_LIMIT,
        dict(from_=0, to=DIVIDA_PATRIMONIO_MAX_LIMIT, increment=0.1, width=9),
    ),
    FilterField(
        "crescimento_receita_5a_min", "Cresc. Receita 5a mínimo (%):", "double", 0.0,
        dict(from_=0, to=500, increment=1, width=9),
    ),
    FilterField("ticker", "Buscar ticker:", "entry", "", dict(width=12)),
]


class MainWindow(ttk.Window):
    def __init__(self):
        super().__init__(
            title="PyInvest — Ranking de FIIs e Ações", theme=THEME, size=(1450, 900), resizable=(True, True)
        )
        self._set_icon()

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True)

        fii_filter_engine = FiiFilter()
        self.fii_panel = AssetPanel(
            notebook,
            asset_noun="FIIs",
            fetch_callable_factory=lambda: FetchFiisUseCase().execute,
            filter_engine=fii_filter_engine,
            ranking_engine=FiiRanking(),
            criteria_cls=FiiFilterCriteria,
            field_specs=FII_FIELDS,
            preset_store=FilterPresetStore(FiiFilterCriteria),
            default_export_filename="fiis.xlsx",
            columns=3,
            segments_field_attr="segmento",
            segments_fn=fii_filter_engine.segments,
        )
        notebook.add(self.fii_panel, text="FIIs")

        self.stock_panel = AssetPanel(
            notebook,
            asset_noun="Ações",
            fetch_callable_factory=lambda: FetchStocksUseCase().execute,
            filter_engine=StockFilter(),
            ranking_engine=StockRanking(),
            criteria_cls=StockFilterCriteria,
            field_specs=STOCK_FIELDS,
            preset_store=FilterPresetStore(StockFilterCriteria, filename="stock_filter_presets.json"),
            default_export_filename="acoes.xlsx",
            columns=4,
        )
        notebook.add(self.stock_panel, text="Ações")

    def _set_icon(self):
        icon_path = resource_path("assets/icon.ico")
        if icon_path.exists():
            try:
                self.iconbitmap(icon_path)
            except tk.TclError:
                pass
