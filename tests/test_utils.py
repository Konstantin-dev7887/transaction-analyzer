import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock
import pandas as pd
from src.utils import (
    load_transactions,
    load_user_settings,
    get_greeting,
    get_currency_rates,
    get_stock_prices,
    filter_transactions_by_date,
)


def test_load_transactions_success(tmp_path):
    # Создаём временный Excel-файл
    df_test = pd.DataFrame({"Сумма платежа": [100, 200]})
    test_file = tmp_path / "test.xlsx"
    df_test.to_excel(test_file, index=False)

    result = load_transactions(str(test_file))
    assert len(result) == 2
    assert result["Сумма платежа"].sum() == 300


def test_load_transactions_file_not_found():
    with pytest.raises(Exception):
        load_transactions("nonexistent.xlsx")


def test_load_user_settings_success(tmp_path, monkeypatch):
    # Создаём временный user_settings.json
    settings_data = {"user_currencies": ["USD"], "user_stocks": ["AAPL"]}
    settings_file = tmp_path / "user_settings.json"
    import json
    json.dump(settings_data, open(settings_file, "w"))

    # Подменяем путь к файлу настроек
    monkeypatch.setattr("src.utils.Path", lambda *args: settings_file if "user_settings.json" in str(args) else None)
    # Проще: переопределим открытие файла
    with patch("builtins.open", return_value=open(settings_file, "r")):
        result = load_user_settings()
        assert result["user_currencies"] == ["USD"]


def test_load_user_settings_missing_file():
    with patch("builtins.open", side_effect=FileNotFoundError):
        result = load_user_settings()
        assert result == {"user_currencies": [], "user_stocks": []}


@pytest.mark.parametrize("hour, expected", [
    (5, "Доброй ночи"),
    (6, "Доброе утро"),
    (11, "Доброе утро"),
    (12, "Добрый день"),
    (17, "Добрый день"),
    (18, "Добрый вечер"),
    (22, "Добрый вечер"),
    (23, "Доброй ночи"),
    (0, "Доброй ночи"),
])
def test_get_greeting(hour, expected):
    dt = datetime(2025, 1, 1, hour, 0, 0)
    assert get_greeting(dt) == expected


@patch("src.utils.requests.get")
def test_get_currency_rates_real_api(mock_get):
    # Тестируем заглушку? Но функция пока заглушка, поэтому просто проверим формат
    rates = get_currency_rates(["USD", "EUR"])
    assert isinstance(rates, list)
    assert len(rates) == 2
    assert "currency" in rates[0]
    assert "rate" in rates[0]


def test_get_stock_prices_format():
    prices = get_stock_prices(["AAPL", "GOOGL"])
    assert len(prices) == 2
    assert prices[0]["stock"] == "AAPL"


def test_filter_transactions_by_date():
    df = pd.DataFrame({
        "Дата операции": ["2025-04-01", "2025-04-10", "2025-03-31"],
        "Сумма": [1, 2, 3]
    })
    df["Дата операции"] = pd.to_datetime(df["Дата операции"])
    end_date = datetime(2025, 4, 10)
    filtered = filter_transactions_by_date(df, end_date)
    assert len(filtered) == 2  # 01.04 и 10.04
    assert filtered["Сумма"].sum() == 3
