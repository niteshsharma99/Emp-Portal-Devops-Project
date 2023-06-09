import pytest
from models import models
from app import app, db


@pytest.fixture
def client():
    app_context = app.app_context()
    app_context.push()
    initDB()
    yield app.test_client()
    truncateDB()
    app_context.pop()


def initDB():
    DATABASE = 'test_emp_db.db'
    app.config.update(
        SQLALCHEMY_DATABASE_URI='sqlite:///'+DATABASE
    )


def truncateDB():
    with app.app_context():
        models.Employee.query.delete()
        db.session.commit()


def test_index():
    client = app.test_client()
    response = client.get('/')
    assert response.status_code == 200



def test_add(client):
    test_data = {'name': 'Mickey Test',
                 'gender': 'male',
                 'address': 'IN',
                 'phone': '0123456789',
                 'salary': '2000',
                 'department': 'Sales'}
    client.post('/add', data=test_data)
    with app.app_context():
        assert models.Employee.query.count() == 1


def test_edit():
    client = app.test_client()
    response = client.post('/edit/0')
    assert response.status_code == 200
    assert b"Sorry, the employee does not exist." in response.data


def test_delete(client):
    test_data = {'emp_id': 0}
    response = client.post('/delete', data=test_data)
    assert response.status_code == 200
    assert b"Sorry, the employee does not exist." in response.data
