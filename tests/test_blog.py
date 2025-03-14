import pytest

from flaskr.blog import blog
from flaskr.db.db import sqldb as db
from flaskr.db.db import User, Post, Like, UnLike

def test_index_with_0_post(client, auth):
    # login before testing
    response = client.get('/')
    assert response.status_code == 200
    assert b"Log In" in response.data
    assert b"Register" in response.data
    assert b"Create" not in response.data
    
    # login and test
    auth.register()
    response = auth.login()
    assert response.status_code == 302
    assert 'Incorrect username.' not in response.data.decode()
    response = client.get('/')
    assert b"Log Out" in response.data
    assert b"test" in response.data
    assert b"New" in response.data
    assert b'href="/create"' in response.data

def test_index_with_1_post(client, auth):
    # login before testing
    response = client.get('/')
    assert response.status_code == 200
    assert b"Log In" in response.data
    assert b"Register" in response.data
    assert b"Create" not in response.data
    
    # login and test
    auth.register()
    response = auth.login()
    assert response.status_code == 302
    assert 'Incorrect username.' not in response.data.decode()
    response = client.get('/')
    assert b"Log Out" in response.data
    assert b"test" in response.data
    assert b"New" in response.data
    assert b'href="/create"' in response.data
    
    # create a post
    response = client.post('/create', data={'title': 'test title', 'body': 'test body'})
    assert response.status_code == 302
    response = client.get('/')
    assert b"test title" in response.data
    assert b"test body" in response.data
    assert b'href="/1/update"' in response.data
    
    # logout and test
    auth.logout()
    response = client.get('/')
    assert b"Log In" in response.data
    assert b"Register" in response.data
    assert b"Create" not in response.data
    assert b"test title" in response.data
    assert b"test body" in response.data
    

# if the user is not logged in, they should be redirected to the login page
@pytest.mark.parametrize('path', (
    '/create',
    '/1/update',
    '/1/delete',
))
def test_login_required(client, path):
    response = client.post(path)
    assert response.status_code == 302
    assert '/auth/login' in response.headers['Location']


def test_auth_require(client, auth):
    auth.register()
    auth.login()
    response = client.post('/create', data={'title': 'test title', 'body': 'test body'})
    assert response.status_code == 302
    
    auth.register('test2', '123@gmail.com', 'test', 'test')
    auth.login('test2', 'test')
    assert client.get('/1/update').status_code == 403
    assert client.post('/1/delete').status_code == 403
    assert b'href="/1/update"' not in client.get('/').data
    

@pytest.mark.parametrize('path', (
    '/2/update',
    '/2/delete',
))
def test_exists_required(client, auth, path):
    auth.register()
    auth.login()
    assert client.post(path).status_code == 404
    

def test_create(client, auth):
    auth.register()
    auth.login()
    assert client.get('/create').status_code == 200
    assert client.post('/create', data={'title': 'test title', 'body': 'test body'}).status_code == 302
    assert b'test title' in client.get('/').data
    assert b'test body' in client.get('/').data
    assert db.session.query(Post).filter_by(title='test title').first() is not None
    
    assert client.post('/create', data={'title': 'another post', 'body': 'test body'}).status_code == 302
    assert b'another post' in client.get('/').data
    assert db.session.query(Post).filter_by(title='another post').first() is not None

def test_update(client, auth):
    auth.register()
    auth.login()
    client.post('/create', data={'title': 'test title', 'body': 'test body'})
    assert client.get('/1/update').status_code == 200
    assert client.post('/1/update', data={'title': 'new title', 'body': 'new body'}).status_code == 302
    assert b'new title' in client.get('/').data
    assert b'new body' in client.get('/').data
    assert db.session.query(Post).filter_by(title='new title').first() is not None
    

@pytest.mark.parametrize('path', (
    '/create',
    '/1/update',
))
def test_update_validate(client, auth, path):
    auth.register()
    auth.login()
    client.post('/create', data={'title': 'test title', 'body': 'test body'})
    response = client.post(path, data={'title': '', 'body': ''})
    assert b'Title is required.' in response.data


def test_delete(client, auth):
    auth.register()
    auth.login()
    client.post('/create', data={'title': 'test title', 'body': 'test body'})
    assert db.session.query(Post).filter_by(title='test title').first() is not None
    assert client.post('/1/delete').status_code == 302
    assert db.session.query(Post).filter_by(title='test title').first() is None
    assert b'test title' not in client.get('/').data