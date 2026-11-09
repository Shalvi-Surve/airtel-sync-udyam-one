from streamlit.testing.v1 import AppTest

from src.database import connection


def test_first_run_creates_storage_directory_and_application_schema(tmp_path, monkeypatch):
    db_path = tmp_path / "new" / "storage" / "demo.sqlite"
    monkeypatch.setattr(connection, "DB_PATH", db_path)

    connection.initialize()

    assert db_path.is_file()
    with connection.session() as db:
        tables = {row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert {"businesses", "quotes", "quote_revisions", "orders", "order_events", "consents", "kyc_results"} <= tables


def test_app_explains_sqlite_initialization_failure(tmp_path, monkeypatch):
    parent_file = tmp_path / "not-a-directory"
    parent_file.write_text("synthetic test obstruction", encoding="utf-8")
    monkeypatch.setattr(connection, "DB_PATH", parent_file / "demo.sqlite")

    app = AppTest.from_file("app.py").run(timeout=30)

    assert not app.exception
    assert any("Demo storage could not be initialized" in item.value for item in app.error)


def test_missing_required_catalogue_has_actionable_loader_error(tmp_path, monkeypatch):
    import pytest
    import src.data.loaders as loaders
    monkeypatch.setattr(loaders, "CATALOGUE_PATH", tmp_path / "missing-catalogue.csv")
    loaders.load_catalogue.clear()

    with pytest.raises(FileNotFoundError, match="Required product catalogue dataset is missing"):
        loaders.load_catalogue()


def test_all_navigation_destinations_load_without_exceptions(tmp_path, monkeypatch):
    monkeypatch.setattr(connection, "DB_PATH", tmp_path / "navigation.sqlite")
    app = AppTest.from_file("app.py").run(timeout=30)
    pages = [
        "Overview", "AI Business Advisor", "Product Catalogue", "Bundle Builder",
        "Quotes & Orders", "Smart KYC", "Order Tracker", "Operations Dashboard", "Settings",
    ]

    for page in pages:
        app.radio[0].set_value(page)
        app.run(timeout=30)
        assert not app.exception, f"{page} raised an exception"
