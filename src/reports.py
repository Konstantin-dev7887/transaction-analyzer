import json
import logging
from datetime import datetime, timedelta
from functools import wraps
from typing import Optional, Callable, Any

import pandas as pd

logger = logging.getLogger(__name__)


def save_to_file(filename: Optional[str] = None) -> Callable:
    """
    Декоратор для сохранения результата отчёта в JSON-файл.
    Если filename не указан, используется имя "report_{дата_время}.json".

    Параметры:
    filename (str, optional): имя файла для сохранения

    Возвращает:
    Callable: декоратор
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            result = func(*args, **kwargs)
            # Преобразуем результат в JSON-совместимый формат
            if isinstance(result, pd.DataFrame):
                data = result.to_dict(orient="records")
            else:
                data = result

            output_filename = filename or f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(output_filename, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            logger.info(f"Отчёт сохранён в {output_filename}")
            return result
        return wrapper
    return decorator


@save_to_file()
def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> pd.DataFrame:
    """
    Возвращает траты по заданной категории за последние 3 месяца от указанной даты.

    Параметры:
    transactions (pd.DataFrame): DataFrame с транзакциями
    category (str): категория для анализа
    date (str, optional): дата отсчёта в формате "YYYY-MM-DD HH:MM:SS". Если не указана — текущая дата.

    Возвращает:
    pd.DataFrame: отфильтрованные транзакции
    """
    if date is None:
        end_date = datetime.now()
    else:
        end_date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")

    start_date = end_date - timedelta(days=90)  # примерно 3 месяца

    # Приводим столбец даты к datetime
    transactions["Дата операции"] = pd.to_datetime(transactions["Дата операции"])
    mask = (transactions["Дата операции"] >= start_date) & (transactions["Дата операции"] <= end_date)
    mask_category = transactions["Категория"] == category
    filtered = transactions.loc[mask & mask_category]

    logger.info(f"Найдено {len(filtered)} транзакций по категории '{category}' за последние 3 месяца")
    return filtered
