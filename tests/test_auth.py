from flaskr.auth import auth
from flaskr.db.db import sqldb as db
from flaskr.db.db import User, Post, Like, UnLike

from bs4 import BeautifulSoup
from werkzeug.security import generate_password_hash, check_password_hash

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
    
def test_login(client):
    user = User(username='test', password=generate_password_hash('test'),
                email = '123@gmail.com')
    db.session.add(user)
    db.session.commit()
    assert user in db.session
    assert user.username == 'test'
    assert check_password_hash(user.password, 'test')
    assert user.email    == '123@gmail.com'
    
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
    