import os
import sys
import pytest
from types import SimpleNamespace

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from app import app, openai


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_login_redirects_when_not_authorized(client, monkeypatch):
    monkeypatch.setattr('app.google', SimpleNamespace(authorized=False))
    response = client.get('/login')
    assert response.status_code == 302


def test_logout_clears_session(client):
    with client.session_transaction() as sess:
        sess['user'] = {'id': 1}
    response = client.get('/logout')
    assert response.status_code == 302
    with client.session_transaction() as sess:
        assert 'user' not in sess


def test_chat_requires_login(client):
    response = client.post('/chat', json={'message': 'hola'})
    assert response.status_code == 401


def test_chat_returns_reply(client, monkeypatch):
    with client.session_transaction() as sess:
        sess['user'] = {'id': 1}

    class DummyCompletion:
        choices = [SimpleNamespace(message=SimpleNamespace(content='respuesta'))]

    monkeypatch.setattr(openai.ChatCompletion, 'create', lambda **kwargs: DummyCompletion())
    response = client.post('/chat', json={'message': 'hola'})
    assert response.status_code == 200
    assert response.get_json()['reply'] == 'respuesta'
