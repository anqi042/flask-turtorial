import sqlite3
from datetime import datetime

import click
from flask import current_app, g

from .. import sqldb

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
    password = sqldb.Column(sqldb.String(120), nullable=False)
    email    = sqldb.Column(sqldb.String(120), nullable=False)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Post(sqldb.Model):
    id = sqldb.Column(sqldb.Integer, primary_key=True, autoincrement=True)
    author_id    = sqldb.Column(sqldb.Integer, sqldb.ForeignKey('user.id'), nullable=False) # User.id will cause an error: can't find foreign key
    created      = sqldb.Column(sqldb.DateTime, nullable=False, default=datetime.utcnow)
    title        = sqldb.Column(sqldb.String(120), nullable=False)
    body         = sqldb.Column(sqldb.Text, nullable=False)
    likes        = sqldb.relationship('Like'  , backref='post', cascade='all, delete-orphan', passive_deletes=True)
    unlikes      = sqldb.relationship('UnLike', backref='post', cascade='all, delete-orphan', passive_deletes=True)
    
    def __repr__(self):
        return f'<Post {self.title}>'

class Like(sqldb.Model):
    id = sqldb.Column(sqldb.Integer, primary_key=True, autoincrement=True)
    user_id    = sqldb.Column(sqldb.Integer, sqldb.ForeignKey('user.id'), nullable=False) # User.id will cause an error: can't find foreign key
    post_id    = sqldb.Column(sqldb.Integer, sqldb.ForeignKey('post.id', ondelete='CASCADE'), nullable=False) # Post.id will cause an error: can't find foreign key

class UnLike(sqldb.Model):
    id = sqldb.Column(sqldb.Integer, primary_key=True, autoincrement=True)
    user_id    = sqldb.Column(sqldb.Integer, sqldb.ForeignKey('user.id'), nullable=False) # User.id will cause an error: can't find foreign key
    post_id    = sqldb.Column(sqldb.Integer, sqldb.ForeignKey('post.id', ondelete='CASCADE'), nullable=False) # Post.id will cause an error: can't find foreign key

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

def add_init_command(app):
    #app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
