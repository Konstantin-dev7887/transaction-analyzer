import pytest
import json
from unittest.mock import patch, MagicMock
from src.views import generate_main_page_response


def test_invalid_date_format():
    with pytest.raises(ValueError):
        generate_main_page_response("2025-04-06")  # не хватает времени


@patch("src.views.load_transactions")
@patch("src.views.load_user_settings")
@patch("src.views.filter_transactions_by_date")
@patch("src.views.get_currency_rates")
@patch("src.views.get_stock_prices")
def test_generate_main_page_response_structure(
    mock_stocks, mock_currency, mock_filter, mock_settings, mock_load
):
    # Мокаем DataFrame
    mock_df = MagicMock()
    mock_load.return_value = mock_df
    mock_filter.return_value = mock_df

    # Мокаем группировку по картам
    mock_group = MagicMock()
    mock_df.groupby.return_value = mock_group
    mock_group.__iter__ = lambda self: iter([("1234", MagicMock(**{"__getitem__.return_value.sum.return_value": 1000}))])
    # Альтернативно:
    mock_df.groupby.return_value = {"1234": MagicMock(**{"sum.return_value": 1000})}
    # Для top_transactions:
    mock_sorted = MagicMock()
    mock_df.sort_values.return_value = mock_sorted
    mock_sorted.head.return_value.iterrows.return_value = [
        (0, {"Дата операции": MagicMock(strftime=lambda x: "01.01.2025"),
             "Сумма платежа": 500,
             "Категория": "Еда",
             "Описание": "Магнит"})
    ]

    mock_settings.return_value = {"user_currencies": ["USD"], "user_stocks": ["AAPL"]}
    mock_currency.return_value = [{"currency": "USD", "rate": 75.0}]
    mock_stocks.return_value = [{"stock": "AAPL", "price": 150.0}]

    response_str = generate_main_page_response("2025-04-06 14:30:00")
    response = json.loads(response_str)

    assert "greeting" in response
    assert response["greeting"] == "Добрый день"
    assert "cards" in response
    assert "top_transactions" in response
    assert isinstance(response["top_transactions"], list)
    assert "currency_rates" in response
    assert "stock_prices" in response


@patch("src.views.load_transactions")
def test_generate_main_page_response_no_cards(mock_load):
    mock_df = MagicMock()
    mock_load.return_value = mock_df
    # Нет колонки "Номер карты"
    mock_df.__contains__.return_value = False
    # Мокаем остальное минимально
    with patch("src.views.filter_transactions_by_date", return_value=mock_df):
        with patch("src.views.load_user_settings", return_value={"user_currencies": [], "user_stocks": []}):
            with patch("src.views.get_currency_rates", return_value=[]):
                with patch("src.views.get_stock_prices", return_value=[]):
                    response_str = generate_main_page_response("2025-04-06 14:30:00")
                    response = json.loads(response_str)
                    assert response["cards"] == []
