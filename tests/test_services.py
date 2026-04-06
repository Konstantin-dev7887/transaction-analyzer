import pytest
import json
from src.services import analyze_cashback_categories, simple_search


@pytest.fixture
def sample_transactions():
    return [
        {"Дата операции": "2025-04-01 10:00:00", "Категория": "Супермаркеты", "Кешбэк": 10.5},
        {"Дата операции": "2025-04-15 12:00:00", "Категория": "Супермаркеты", "Кешбэк": 5.0},
        {"Дата операции": "2025-03-31 23:59:59", "Категория": "Аптеки", "Кешбэк": 20.0},
        {"Дата операции": "2025-04-20 09:00:00", "Категория": "Кафе", "Кешбэк": 7.5},
        {"Дата операции": "2025-04-01 08:00:00", "Категория": "Супермаркеты", "Кешбэк": None},  # None
    ]


def test_analyze_cashback_categories(sample_transactions):
    result_json = analyze_cashback_categories(sample_transactions, 2025, 4)
    result = json.loads(result_json)

    # Ожидаем: Супермаркеты = 10.5 + 5.0 = 15.5; Кафе = 7.5; None игнорируется
    assert result["Супермаркеты"] == 15.5
    assert result["Кафе"] == 7.5
    assert "Аптеки" not in result  # март не входит


def test_analyze_cashback_categories_empty():
    result = json.loads(analyze_cashback_categories([], 2025, 4))
    assert result == {}


def test_simple_search(sample_transactions):
    result_json = simple_search(sample_transactions, "супер")
    result = json.loads(result_json)
    assert len(result) == 3  # все с категорией "Супермаркеты"
    for t in result:
        assert "супер" in t["Категория"].lower()


def test_simple_search_no_match(sample_transactions):
    result = json.loads(simple_search(sample_transactions, "zzz"))
    assert result == []


def test_simple_search_search_in_description():
    trans = [{"Описание": "Перевод другу", "Категория": "Переводы"}]
    result = json.loads(simple_search(trans, "другу"))
    assert len(result) == 1
