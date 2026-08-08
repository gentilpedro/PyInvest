from app.domain.filters.fii_filter import FiiFilter, FiiFilterCriteria


def test_apply_with_no_criteria_returns_everything(sample_fii_df):
    result = FiiFilter().apply(sample_fii_df, FiiFilterCriteria())
    assert len(result) == len(sample_fii_df)


def test_dy_min_filters_below_threshold(sample_fii_df):
    result = FiiFilter().apply(sample_fii_df, FiiFilterCriteria(dy_min=8))
    assert set(result["Papel"]) == {"AAAA11", "BBBB11"}


def test_pvp_max_filters_above_threshold(sample_fii_df):
    result = FiiFilter().apply(sample_fii_df, FiiFilterCriteria(pvp_max=1.0))
    assert set(result["Papel"]) == {"AAAA11", "CCCC11"}


def test_liquidez_min_filters_below_threshold(sample_fii_df):
    result = FiiFilter().apply(sample_fii_df, FiiFilterCriteria(liquidez_min=50_000))
    assert set(result["Papel"]) == {"AAAA11", "CCCC11"}


def test_segmento_filters_exact_match(sample_fii_df):
    result = FiiFilter().apply(sample_fii_df, FiiFilterCriteria(segmento="Shoppings"))
    assert set(result["Papel"]) == {"AAAA11", "CCCC11"}


def test_segmento_todos_means_no_filter(sample_fii_df):
    result = FiiFilter().apply(sample_fii_df, FiiFilterCriteria(segmento="Todos"))
    assert len(result) == len(sample_fii_df)


def test_ffo_yield_min(sample_fii_df):
    result = FiiFilter().apply(sample_fii_df, FiiFilterCriteria(ffo_yield_min=8))
    assert set(result["Papel"]) == {"AAAA11", "BBBB11"}


def test_valor_mercado_min(sample_fii_df):
    result = FiiFilter().apply(sample_fii_df, FiiFilterCriteria(valor_mercado_min=1_000_000))
    assert set(result["Papel"]) == {"AAAA11", "CCCC11"}


def test_qtd_imoveis_min(sample_fii_df):
    result = FiiFilter().apply(sample_fii_df, FiiFilterCriteria(qtd_imoveis_min=5))
    assert set(result["Papel"]) == {"AAAA11", "CCCC11"}


def test_cap_rate_min(sample_fii_df):
    result = FiiFilter().apply(sample_fii_df, FiiFilterCriteria(cap_rate_min=8))
    assert set(result["Papel"]) == {"AAAA11", "CCCC11"}


def test_vacancia_max(sample_fii_df):
    result = FiiFilter().apply(sample_fii_df, FiiFilterCriteria(vacancia_max=5))
    assert set(result["Papel"]) == {"AAAA11", "BBBB11", "CCCC11"}


def test_ticker_filter_is_case_insensitive_substring(sample_fii_df):
    result = FiiFilter().apply(sample_fii_df, FiiFilterCriteria(ticker="bbbb"))
    assert set(result["Papel"]) == {"BBBB11"}


def test_combined_criteria(sample_fii_df):
    criteria = FiiFilterCriteria(dy_min=6, pvp_max=1.0, segmento="Shoppings")
    result = FiiFilter().apply(sample_fii_df, criteria)
    assert set(result["Papel"]) == {"AAAA11", "CCCC11"}


def test_apply_returns_reset_index(sample_fii_df):
    result = FiiFilter().apply(sample_fii_df, FiiFilterCriteria(dy_min=8))
    assert list(result.index) == list(range(len(result)))


def test_segments_returns_sorted_unique_values(sample_fii_df):
    assert FiiFilter().segments(sample_fii_df) == ["Logística", "Outros", "Shoppings"]


def test_segments_without_segmento_column_returns_empty():
    import pandas as pd

    assert FiiFilter().segments(pd.DataFrame({"Papel": ["AAAA11"]})) == []
