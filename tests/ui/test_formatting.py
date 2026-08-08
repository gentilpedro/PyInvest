import math

from ui.formatting import format_value, sort_key


def test_format_percent_column_uses_comma_decimal():
    assert format_value("Dividend Yield", 8.79) == "8,79%"


def test_format_integer_column_uses_dot_thousands_separator():
    assert format_value("Liquidez", 1_234_567) == "1.234.567"


def test_format_decimal_column_uses_brazilian_notation():
    assert format_value("Cotação", 1234.5) == "1.234,50"


def test_format_nan_returns_dash():
    assert format_value("Cotação", float("nan")) == "-"


def test_format_none_returns_dash():
    assert format_value("Cotação", None) == "-"


def test_format_text_column_passthrough():
    assert format_value("Papel", "HGLG11") == "HGLG11"


def test_format_stock_percent_column():
    assert format_value("ROE", -1.05) == "-1,05%"


def test_format_stock_integer_column():
    assert format_value("Patrim. Líq", 1_012_240_000) == "1.012.240.000"


def test_sort_key_numeric_column_returns_float():
    assert sort_key("Cotação", 12.3) == 12.3


def test_sort_key_nan_sorts_as_negative_infinity():
    assert sort_key("Cotação", float("nan")) == float("-inf")
    assert not math.isnan(sort_key("Cotação", float("nan")))


def test_sort_key_text_column_returns_string():
    assert sort_key("Papel", "HGLG11") == "HGLG11"


def test_sort_key_none_text_column_returns_empty_string():
    assert sort_key("Papel", None) == ""
