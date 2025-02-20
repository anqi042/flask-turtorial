import sqlite3
from datetime import datetime

import click
from flask import current_app, g

from flask_sqlalchemy import SQLAlchemy

sqldb = SQLAlchemy()

'''
CREATE TABLE user (
  id       INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  email    TEXT NOT NULL
);

CREATE TABLE post (
  id        INTEGER PRIMARY KEY AUTOINCREMENT,
  author_id INTEGER NOT NULL,
  created   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  title     TEXT NOT NULL,
  body      TEXT NOT NULL,
  FOREIGN KEY (author_id) REFERENCES user (id)
);
'''

class User(sqldb.Model):
    id = sqldb.Column(sqldb.Integer, primary_key=True, autoincrement=True)
    username = sqldb.Column(sqldb.String(80), unique=True, nullable=False)
    password = sqldb.Column(sqldb.String(120), unique=True, nullable=False)
    email    = sqldb.Column(sqldb.String(120), unique = True, nullable=False)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Post(sqldb.Model):
    id = sqldb.Column(sqldb.Integer, primary_key=True, autoincrement=True)
    author_id = sqldb.Column(sqldb.Integer, sqldb.ForeignKey('user.id'), nullable=False) # User.id will cause an error: can't find foreign key
    created   = sqldb.Column(sqldb.DateTime, nullable=False, default=datetime.utcnow)
    title     = sqldb.Column(sqldb.String(120), nullable=False)
    body      = sqldb.Column(sqldb.Text, nullable=False)
    
    def __repr__(self):
        return f'<Post {self.title}>'

'''
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types = sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()
'''

def init_db():
    with current_app.app_context():
        sqldb.create_all()

@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables"""
    init_db()
    click.echo('Initialized the database.')

sqlite3.register_converter(
    "timestamp", lambda v: datetime.fromisoformat(v.decode())
)

def init_db_app(app):
    #app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
