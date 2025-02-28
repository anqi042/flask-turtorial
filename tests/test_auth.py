from flaskr.auth import auth
from flaskr.db.db import sqldb as db
from flaskr.db.db import User, Post, Like, UnLike

from bs4 import BeautifulSoup

def get_csrf_token(html):
    soup = BeautifulSoup(html, 'html.parser')
    csrf_input = soup.find('input', {'name': 'csrf_token'})
    return csrf_input['value'] if csrf_input else None

def test_register(client):
    response = client.get('auth/register')
    assert response.status_code == 200

    html = response.data.decode()
    
    # 解析Token（推荐使用BeautifulSoup）
    csrf_token = get_csrf_token(html)
    assert csrf_token is not None
    
    response = client.post('/auth/register', data={'csrf_token': csrf_token, 
                                                  'username': 'anqi8', 'email': 'fff@gmail.com', 
                                                  'password': '123', 'confirm': '123', 'submit': 'Register'})
    assert '/auth/login' == response.headers['Location']
    assert User.query.filter_by(username='anqi8').first() is not None
    assert User.query.filter_by(email='fff@gmail.com').first() is not None