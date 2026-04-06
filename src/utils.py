import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

import pandas as pd
import requests
from dotenv import load_dotenv
import os

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

load_dotenv()


def load_transactions(file_path: str) -> pd.DataFrame:
    """
    Загружает транзакции из Excel-файла.

    Параметры:
    file_path (str): путь к файлу operations.xlsx

    Возвращает:
    pd.DataFrame: DataFrame с транзакциями
    """
    try:
        df = pd.read_excel(file_path, engine="openpyxl")
        logger.info(f"Загружено {len(df)} транзакций из {file_path}")
        return df
    except Exception as e:
        logger.error(f"Ошибка загрузки файла {file_path}: {e}")
        raise


def load_user_settings() -> Dict[str, Any]:
    """
    Загружает настройки пользователя из user_settings.json.

    Возвращает:
    dict: словарь с настройками
    """
    settings_path = Path(__file__).parent.parent / "user_settings.json"
    try:
        with open(settings_path, "r", encoding="utf-8") as f:
            settings = json.load(f)
        logger.info("Настройки пользователя загружены")
        return settings
    except Exception as e:
        logger.error(f"Ошибка загрузки настроек: {e}")
        return {"user_currencies": [], "user_stocks": []}


def get_greeting(current_time: datetime) -> str:
    """
    Определяет приветствие по времени суток.

    Параметры:
    current_time (datetime): текущее время

    Возвращает:
    str: приветствие
    """
    hour = current_time.hour
    if 6 <= hour < 12:
        return "Доброе утро"
    elif 12 <= hour < 18:
        return "Добрый день"
    elif 18 <= hour < 23:
        return "Добрый вечер"
    else:
        return "Доброй ночи"


def get_currency_rates(currencies: List[str]) -> List[Dict[str, float]]:
    """
    Получает курсы валют через API.

    Параметры:
    currencies (list): список кодов валют

    Возвращает:
    list: список словарей [{"currency": "USD", "rate": 73.21}, ...]
    """
    # Здесь нужен реальный API-ключ. Для примера используем заглушку.
    # В реальном проекте сделай запрос к API, например:
    # api_key = os.getenv("CURRENCY_API_KEY")
    # url = f"https://api.currencyapi.com/v3/latest?apikey={api_key}&base_currency=RUB&currencies={','.join(currencies)}"
    # response = requests.get(url)
    # data = response.json()
    # rates = [{"currency": cur, "rate": data["data"][cur]["value"]} for cur in currencies]

    # Заглушка для демонстрации
    logger.info("Получение курсов валют (заглушка)")
    return [{"currency": cur, "rate": 100.0} for cur in currencies]


def get_stock_prices(stocks: List[str]) -> List[Dict[str, float]]:
    """
    Получает цены акций через API.

    Параметры:
    stocks (list): список тикеров акций

    Возвращает:
    list: список словарей [{"stock": "AAPL", "price": 150.12}, ...]
    """
    # Аналогично, нужен реальный API (например, Alpha Vantage)
    # Заглушка
    logger.info("Получение цен акций (заглушка)")
    return [{"stock": stock, "price": 500.0} for stock in stocks]


def filter_transactions_by_date(df: pd.DataFrame, end_date: datetime) -> pd.DataFrame:
    """
    Фильтрует транзакции с начала месяца по указанную дату.

    Параметры:
    df (pd.DataFrame): DataFrame с транзакциями
    end_date (datetime): конечная дата

    Возвращает:
    pd.DataFrame: отфильтрованный DataFrame
    """
    start_date = end_date.replace(day=1)
    df["Дата операции"] = pd.to_datetime(df["Дата операции"])
    mask = (df["Дата операции"] >= start_date) & (df["Дата операции"] <= end_date)
    filtered = df.loc[mask]
    logger.info(f"Отфильтровано {len(filtered)} транзакций с {start_date.date()} по {end_date.date()}")
    return filtered
