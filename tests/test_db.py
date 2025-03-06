from flaskr.db.db import sqldb as db
from flaskr.db.db import User, Post, Like, UnLike

def test_init_db_command(runner, monkeypatch):
    class Recorder:
        called = False

    def fake_init_db():
        Recorder.called = True

    monkeypatch.setattr('flaskr.db.db.init_db', fake_init_db)
    result = runner.invoke(args=['init-db'])
    assert 'Initialized' in result.output
    assert Recorder.called

def test_user_model(app):
    user = User(username='test', password='test',
                email = '123@gmail.com')
    db.session.add(user)
    db.session.commit()

    assert user in db.session
    assert user.username == 'test'
    assert user.password == 'test'
    assert user.email    == '123@gmail.com'

def test_post_model(app):
    user = User(username='test', password='test', email='123@gmail.com')
    db.session.add(user)
    db.session.commit()
    
    post = Post(title='test', body='test', author_id=user.id)
    db.session.add(post)
    db.session.commit()

    assert post in db.session
    assert post.title == 'test'
    assert post.body == 'test'
    assert post.author_id == user.id

def test_like_model(app):
    user = User(username='test', password='test', email='123@gmail.com')
    db.session.add(user)
    db.session.commit()
    
    post = Post(title='test', body='test', author_id=user.id)
    db.session.add(post)
    db.session.commit()
    
    like = Like(user_id=user.id, post_id=post.id)
    db.session.add(like)
    db.session.commit()
    
    assert like in db.session
    assert like.user_id == user.id
    assert like.post_id == post.id

def test_unlike_model(app):
    user = User(username='test', password='test', email='123@gmail.com')
    db.session.add(user)
    db.session.commit()
    
    post = Post(title='test', body='test', author_id=user.id)
    db.session.add(post)
    db.session.commit()
    
    unlike = UnLike(user_id=user.id, post_id=post.id)
    db.session.add(unlike)
    db.session.commit()
    
    assert unlike in db.session
    assert unlike.user_id == user.id
    assert unlike.post_id == post.id
    
def test_post_and_like_cascade_delete(app):
    user1 = User(username='user1', password='test',
                email = '111@qq.com')
    db.session.add(user1)
    user2 = User(username='user2', password='test',
                email = '222@qq.com')
    db.session.add(user2)
    user3 = User(username='user3', password='test',
                email = '333@qq.com')
    db.session.add(user3)
    db.session.commit()
    
    post = Post(title='test', body='test', author_id=user1.id)
    db.session.add(post)
    db.session.commit()
    
    assert post in db.session
    assert post.title == 'test'
    assert post.body  == 'test'
    assert post.author_id == user1.id
    
    like1 = Like(user_id=user1.id, post_id=post.id)
    like2 = Like(user_id=user2.id, post_id=post.id)
    like3 = Like(user_id=user3.id, post_id=post.id)
    db.session.add_all([like1, like2, like3])
    db.session.commit()
    
    like_num = Like.query.filter_by(post_id = post.id).count()
    assert like_num == 3
    
    db.session.delete(post)
    db.session.commit()
    
    assert post not in db.session

    like_num = db.session.query(Like).filter_by(post_id = post.id).count()
    assert like_num == 0
