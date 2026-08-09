from app.domain.filters.stock_filter import StockFilter, StockFilterCriteria


def test_apply_with_no_criteria_returns_everything(sample_stock_df):
    result = StockFilter().apply(sample_stock_df, StockFilterCriteria())
    assert len(result) == len(sample_stock_df)


def test_dy_min_filters_below_threshold(sample_stock_df):
    result = StockFilter().apply(sample_stock_df, StockFilterCriteria(dy_min=5))
    assert set(result["Papel"]) == {"AAAA3", "DDDD3"}


def test_pl_max_filters_above_threshold(sample_stock_df):
    result = StockFilter().apply(sample_stock_df, StockFilterCriteria(pl_max=15))
    assert set(result["Papel"]) == {"AAAA3", "BBBB4", "CCCC3"}


def test_pvp_max_filters_above_threshold(sample_stock_df):
    result = StockFilter().apply(sample_stock_df, StockFilterCriteria(pvp_max=1.5))
    assert set(result["Papel"]) == {"AAAA3", "CCCC3"}


def test_roe_min_filters_below_threshold(sample_stock_df):
    result = StockFilter().apply(sample_stock_df, StockFilterCriteria(roe_min=15))
    assert set(result["Papel"]) == {"AAAA3", "DDDD3"}


def test_roic_min_filters_below_threshold(sample_stock_df):
    result = StockFilter().apply(sample_stock_df, StockFilterCriteria(roic_min=15))
    assert set(result["Papel"]) == {"AAAA3", "DDDD3"}


def test_margem_liquida_min_filters_below_threshold(sample_stock_df):
    result = StockFilter().apply(sample_stock_df, StockFilterCriteria(margem_liquida_min=10))
    assert set(result["Papel"]) == {"AAAA3", "DDDD3"}


def test_divida_patrimonio_max_filters_above_threshold(sample_stock_df):
    result = StockFilter().apply(sample_stock_df, StockFilterCriteria(divida_patrimonio_max=1.0))
    assert set(result["Papel"]) == {"AAAA3", "DDDD3"}


def test_liquidez_min_filters_below_threshold(sample_stock_df):
    result = StockFilter().apply(sample_stock_df, StockFilterCriteria(liquidez_min=200_000))
    assert set(result["Papel"]) == {"AAAA3", "BBBB4", "DDDD3"}


def test_patrimonio_liquido_min_filters_below_threshold(sample_stock_df):
    result = StockFilter().apply(sample_stock_df, StockFilterCriteria(patrimonio_liquido_min=500_000_000))
    assert set(result["Papel"]) == {"AAAA3", "DDDD3"}


def test_ticker_filter_is_case_insensitive_substring(sample_stock_df):
    result = StockFilter().apply(sample_stock_df, StockFilterCriteria(ticker="bbbb"))
    assert set(result["Papel"]) == {"BBBB4"}


def test_combined_criteria(sample_stock_df):
    criteria = StockFilterCriteria(roe_min=15, pl_max=15, dy_min=5)
    result = StockFilter().apply(sample_stock_df, criteria)
    assert set(result["Papel"]) == {"AAAA3"}


def test_apply_returns_reset_index(sample_stock_df):
    result = StockFilter().apply(sample_stock_df, StockFilterCriteria(dy_min=5))
    assert list(result.index) == list(range(len(result)))
