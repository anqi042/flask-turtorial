from flaskr.blog import blog
from flaskr.db.db import sqldb as db
from flaskr.db.db import User, Post, Like, UnLike

def test_index(client):
    response = client.get('/')
    assert response.status_code == 200
