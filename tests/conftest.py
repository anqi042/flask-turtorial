import os
import tempfile

import pytest
from flaskr import create_app
from flaskr.db.db import sqldb as db
from flaskr.db.db import User, Post, Like, UnLike
from sqlalchemy import Engine

@pytest.fixture
def app():
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///:memory:',
        #'SQLALCHEMY_ECHO': True,
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'WTF_CSRF_ENABLED': False
    })

    with app.app_context():
        @db.event.listens_for(Engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all() 
    
@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def login(self, username='test',  password='test'):
        return self._client.post(
            '/auth/login',
            data={'username': username, 'password': password}
        )
    
    def logout(self):
        return self._client.get('/auth/logout')
    
    def register(self, username='test', email='1234@gmail.com', password='test', confirm='test'):
        return self._client.post(
            '/auth/register',
            data={'username': username, 'email': email, 'password': password, 'confirm': confirm}
        )

@pytest.fixture
def auth(client):
    return AuthActions(client)