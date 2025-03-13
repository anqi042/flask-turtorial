import pytest

from flaskr.auth import auth
from flaskr.db.db import sqldb as db
from flaskr.db.db import User, Post, Like, UnLike
from flask import g

from bs4 import BeautifulSoup
from werkzeug.security import generate_password_hash, check_password_hash

def get_csrf_token(html):
    soup = BeautifulSoup(html, 'html.parser')
    csrf_input = soup.find('input', {'name': 'csrf_token'})
    return csrf_input['value'] if csrf_input else None

def test_register(client, auth):
    response = client.get('auth/register')
    assert response.status_code == 200

    #html = response.data.decode()
    
    # 解析Token（推荐使用BeautifulSoup）
    #csrf_token = get_csrf_token(html)
    #assert csrf_token is not None

    response = auth.register('anqi8', 'fff@gmail.com', '123', '123')
    assert response.status_code == 302
    assert '/auth/login' == response.headers['Location']
    assert User.query.filter_by(username='anqi8').first() is not None
    assert User.query.filter_by(email='fff@gmail.com').first() is not None
    
    response = client.post('/auth/register', data={'username': 'anqi8', 'email': 'fff@gmail.com', 
                                                   'password': '123', 'confirm': '123', 'submit': 'Register'})
    auth.register('anqi8', 'fff@gmail.com', '123', '123')
    message = b'User anqi8 is already registered.'
    assert message in response.data

def test_login(client, auth):
    auth.register()
    
    response = client.get('/auth/login')
    assert response.status_code == 200

    # wrong username
    response = client.post('/auth/login', data={'username': 'xxxxx', 'password': 'test'})
    assert response.status_code == 200
    assert 'Incorrect username.' in response.data.decode()
    
    # wrong password
    response = client.post('/auth/login', data={
        'username': 'test', 'password': 'xxxx'
    })
    assert response.status_code == 200
    assert 'Incorrect password.' in response.data.decode()

    # test success login
    response = client.post('/auth/login', data={
        'username': 'test', 'password': 'test'
    })
    assert response.status_code == 302
    assert response.headers['Location'] == '/'
    
    with client.session_transaction() as session:
       assert session['user_id'] is not None

@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('a', 'test', b'Incorrect username.'),
    ('test', 'a', b'Incorrect password.'),
))
def test_login_validate_input(auth, username, password, message):
    response = auth.register()
    assert response.status_code == 302

    response = auth.login(username, password)
    assert message in response.data
    
def test_logout(client, auth):
    auth.register()
    auth.login()
    
    response = auth.logout()
    assert response.status_code == 302
    assert response.headers['Location'] == '/'
    
    with client.session_transaction() as session:
        assert 'user_id' not in session