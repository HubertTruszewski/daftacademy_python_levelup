from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_customers():
    response = client.get('/customers')
    results = response.json()
    results = results['customers']
    for result in results:
        assert(bool(result) is True)


def test_categories():
    response = client.get('/categories')
    results = response.json()
    results = results['categories']
    for result in results:
        assert(bool(result) is True)
