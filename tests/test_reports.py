import pytest
import pandas as pd
import json
from datetime import datetime, timedelta
from src.reports import spending_by_category, save_to_file


@pytest.fixture
def sample_df():
    base_date = datetime(2025, 4, 6)
    dates = [base_date - timedelta(days=i) for i in range(0, 120)]  # 120 дней
    categories = ["Супермаркеты"] * 60 + ["Другое"] * 60
    return pd.DataFrame({
        "Дата операции": dates,
        "Категория": categories,
        "Сумма платежа": [100] * 120,
    })


def test_spending_by_category_with_date(sample_df, tmp_path):
    # Временно подменим путь сохранения отчёта, чтобы не засорять
    with patch("src.reports.open", create=True) as mock_open:
        result_df = spending_by_category(sample_df, "Супермаркеты", "2025-04-06 00:00:00")
    # За последние 3 месяца (90 дней) от 2025-04-06
    # В sample_df за 120 дней, должны попасть только те, что в последних 90 днях
    # Дата начала = 2025-04-06 - 90 дней = 2025-01-06
    expected_count = len(sample_df[
        (sample_df["Дата операции"] >= datetime(2025, 1, 6)) &
        (sample_df["Категория"] == "Супермаркеты")
    ])
    assert len(result_df) == expected_count
    assert all(result_df["Категория"] == "Супермаркеты")


def test_spending_by_category_default_date(sample_df):
    with patch("src.reports.datetime") as mock_dt:
        mock_dt.now.return_value = datetime(2025, 4, 6)
        mock_dt.side_effect = lambda *args, **kw: datetime(*args, **kw)
        result_df = spending_by_category(sample_df, "Супермаркеты")
    # Аналогично, но дата now
    assert len(result_df) > 0


def test_spending_by_category_no_category(sample_df):
    result_df = spending_by_category(sample_df, "Несуществующая")
    assert len(result_df) == 0


def test_decorator_saves_file(tmp_path):
    # Проверяем, что декоратор сохраняет результат в файл
    @save_to_file(str(tmp_path / "test_report.json"))
    def dummy_report():
        return [{"a": 1}]

    dummy_report()
    saved_file = tmp_path / "test_report.json"
    assert saved_file.exists()
    with open(saved_file) as f:
        data = json.load(f)
    assert data == [{"a": 1}]


def test_decorator_default_filename():
    with patch("src.reports.open", create=True) as mock_open:
        @save_to_file()
        def dummy_report():
            return {"x": 2}
        dummy_report()
        # Проверяем, что open вызван с именем файла, начинающимся с "report_"
        call_args = mock_open.call_args[0][0]
        assert call_args.startswith("report_")
        assert call_args.endswith(".json")
