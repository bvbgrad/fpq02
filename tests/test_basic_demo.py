import pytest

from app import app


@pytest.fixture
def my_app():
    return app.test_client()

def test_my_basic_test(my_app):
    response = my_app.get("/")
    assert response.data.decode("utf-8") == "<h1>Flask demo!</h1>"
    assert response.status_code == 200