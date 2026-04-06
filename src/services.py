import json
import logging
from datetime import datetime
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


def analyze_cashback_categories(transactions: List[Dict[str, Any]], year: int, month: int) -> str:
    """
    Анализирует выгодные категории для повышенного кешбэка.

    Параметры:
    transactions (list): список словарей с транзакциями
    year (int): год
    month (int): месяц

    Возвращает:
    str: JSON-строка с начисленным кешбэком по категориям
    """
    # Фильтрация транзакций за указанный месяц
    filtered = []
    for t in transactions:
        # Предполагаем, что дата операции в формате, который можно распарсить
        try:
            t_date = datetime.strptime(t["Дата операции"], "%Y-%m-%d %H:%M:%S")
        except:
            continue
        if t_date.year == year and t_date.month == month:
            filtered.append(t)

    # Подсчёт кешбэка по категориям (предполагаем, что кешбэк хранится в поле "Кешбэк")
    cashback_by_category = {}
    for t in filtered:
        category = t.get("Категория", "Без категории")
        cashback = t.get("Кешбэк", 0.0)
        if isinstance(cashback, (int, float)):
            cashback_by_category[category] = cashback_by_category.get(category, 0.0) + cashback

    return json.dumps(cashback_by_category, ensure_ascii=False, indent=2)


def simple_search(transactions: List[Dict[str, Any]], query: str) -> str:
    """
    Простой поиск транзакций по описанию или категории.

    Параметры:
    transactions (list): список словарей с транзакциями
    query (str): поисковый запрос

    Возвращает:
    str: JSON-строка с найденными транзакциями
    """
    query_lower = query.lower()
    result = []
    for t in transactions:
        description = t.get("Описание", "").lower()
        category = t.get("Категория", "").lower()
        if query_lower in description or query_lower in category:
            result.append(t)

    return json.dumps(result, ensure_ascii=False, indent=2)
