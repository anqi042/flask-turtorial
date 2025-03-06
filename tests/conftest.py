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
        'SQLALCHEMY_TRACK_MODIFICATIONS': False
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