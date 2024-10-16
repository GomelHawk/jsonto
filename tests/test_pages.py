import pytest
from app import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_home_page_redirect(client):
    response = client.get('/')
    assert response.status_code == 302


def test_php_page(client):
    response = client.get('/php')
    assert response.status_code == 200
    assert b'RootModel::class' in response.data


def test_java_page(client):
    response = client.get('/java')
    assert response.status_code == 200
    assert b'RootModel.class' in response.data


def test_python_page(client):
    response = client.get('/python')
    assert response.status_code == 200
    assert b'RootModel.from_dict' in response.data
