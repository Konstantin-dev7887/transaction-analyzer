import json
import logging
from datetime import datetime
from typing import Dict, Any

import pandas as pd

from src.utils import (
    load_transactions,
    load_user_settings,
    get_greeting,
    get_currency_rates,
    get_stock_prices,
    filter_transactions_by_date,
)

logger = logging.getLogger(__name__)


def generate_main_page_response(date_time_str: str) -> str:
    """
    Генерирует JSON-ответ для главной страницы.

    Параметры:
    date_time_str (str): дата и время в формате "YYYY-MM-DD HH:MM:SS"

    Возвращает:
    str: JSON-строка с данными для главной страницы
    """
    try:
        current_time = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        logger.error("Неверный формат даты")
        raise ValueError("Формат даты должен быть YYYY-MM-DD HH:MM:SS")

    # Загрузка данных
    df = load_transactions("data/operations.xlsx")
    settings = load_user_settings()
    currencies = settings.get("user_currencies", [])
    stocks = settings.get("user_stocks", [])

    # Фильтрация по дате
    df_filtered = filter_transactions_by_date(df, current_time)

    # 1. Приветствие
    greeting = get_greeting(current_time)

    # 2. Данные по картам
    cards_data = []
    # Группировка по номеру карты (столбец "Номер карты")
    if "Номер карты" in df_filtered.columns:
        for card, group in df_filtered.groupby("Номер карты"):
            # Сумма расходов: сумма платежа (столбец "Сумма платежа")
            total_spent = group["Сумма платежа"].sum()
            cashback = total_spent / 100  # 1 рубль на каждые 100 рублей
            cards_data.append({
                "last_digits": str(card)[-4:],
                "total_spent": round(total_spent, 2),
                "cashback": round(cashback, 2)
            })

    # 3. Топ-5 транзакций по сумме платежа
    top_transactions = []
    if "Сумма платежа" in df_filtered.columns:
        sorted_df = df_filtered.sort_values("Сумма платежа", ascending=False).head(5)
        for _, row in sorted_df.iterrows():
            top_transactions.append({
                "date": row["Дата операции"].strftime("%d.%m.%Y") if pd.notna(row["Дата операции"]) else "",
                "amount": round(row["Сумма платежа"], 2),
                "category": row.get("Категория", ""),
                "description": row.get("Описание", "")
            })

    # 4. Курсы валют
    currency_rates = get_currency_rates(currencies)

    # 5. Цены акций
    stock_prices = get_stock_prices(stocks)

    result = {
        "greeting": greeting,
        "cards": cards_data,
        "top_transactions": top_transactions,
        "currency_rates": currency_rates,
        "stock_prices": stock_prices
    }

    return json.dumps(result, ensure_ascii=False, indent=2)
