import os
import sys
import pytest

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from app import app, get_db, init_db


@pytest.fixture
def client():
    app.config['TESTING'] = True
    try:
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute('DROP TABLE IF EXISTS users')
            conn.commit()
    except Exception:
        pass
    init_db()
    with app.test_client() as client:
        yield client


def register(client, username='user', password='pass'):
    return client.post('/register', json={'username': username, 'password': password})


def login(client, username='user', password='pass'):
    return client.post('/login', json={'username': username, 'password': password})


def test_registration_and_login(client):
    rv = register(client)
    assert rv.status_code in (200, 201)
    rv = login(client)
    assert rv.status_code == 200
    rv = client.get('/user')
    assert rv.status_code == 200
    assert rv.get_json()['username'] == 'user'


def test_chat_requires_login(client):
    rv = client.post('/chat', json={'message': 'hola'})
    assert rv.status_code == 401


def test_chat_returns_reply_when_logged_in(client):
    register(client)
    login(client)
    rv = client.post('/chat', json={'message': 'hola'})
    assert rv.status_code == 200
    assert 'Hola' in rv.get_json()['reply']


def test_logout(client):
    register(client)
    login(client)
    rv = client.post('/logout')
    assert rv.status_code == 200
    rv = client.get('/user')
    assert rv.status_code == 401
