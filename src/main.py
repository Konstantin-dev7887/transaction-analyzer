import logging
from src.utils import load_transactions
from src.views import generate_main_page_response
from src.services import analyze_cashback_categories, simple_search
from src.reports import spending_by_category

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def main():
    # Демонстрация работы главной страницы
    response = generate_main_page_response("2025-04-06 14:30:00")
    print("=== Главная страница ===")
    print(response)

    # Загрузка транзакций в виде списка словарей для сервисов
    df = load_transactions("data/operations.xlsx")
    transactions_list = df.to_dict(orient="records")

    # Сервис: выгодные категории кешбэка
    cashback_json = analyze_cashback_categories(transactions_list, 2025, 4)
    print("\n=== Выгодные категории кешбэка ===")
    print(cashback_json)

    # Сервис: простой поиск
    search_result = simple_search(transactions_list, "перевод")
    print("\n=== Простой поиск ===")
    print(search_result)

    # Отчёт: траты по категории
    report_df = spending_by_category(df, "Супермаркеты")
    print("\n=== Траты по категории 'Супермаркеты' ===")
    print(report_df.head())


if __name__ == "__main__":
    main()
