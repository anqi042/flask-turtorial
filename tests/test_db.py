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
    post = Post(title='test', body='test', author_id=1)
    db.session.add(post)
    db.session.commit()

    assert post in db.session
    assert post.title == 'test'
    assert post.body == 'test'
    assert post.author_id == 1

def test_like_model(app):
    like = Like(user_id=1, post_id=1)
    db.session.add(like)
    db.session.commit()
    
    assert like in db.session
    assert like.user_id == 1
    assert like.post_id == 1

def test_unlike_model(app):
    unlike = UnLike(user_id=1, post_id=1)
    db.session.add(unlike)
    db.session.commit()
    
    assert unlike in db.session
    assert unlike.user_id == 1
    assert unlike.post_id == 1