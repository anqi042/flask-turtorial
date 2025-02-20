import os

from flask import Flask
from datetime import timedelta

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    db_name   = 'flaskr.sqlite'
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"base_dir: {base_dir}")
    print(f"app.instance_path: {app.instance_path}")
    db_path = os.path.join(app.instance_path, db_name)
    print(f"db_path: {db_path}")
    
    app.config.from_mapping(
        SECRET_KEY = 'dev',

        PERMANENT_SESSION_LIFETIME = timedelta(minutes=5),
        WTF_CRSF_ENABLED = True,
        SQLALCHEMY_DATABASE_URI = f'sqlite:///{db_path}',
        SQLALCHEMY_TRACK_MODIFICATIONS = False
    )

    if test_config is None:
        # load the instance config, it it exists, when not testing
        app.config.from_pyfile('config.py', silent = True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)
    
    #ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'hello, world!'
 
    from .db import db
    db.sqldb.init_app(app)
    db.init_db_app(app)
    with app.app_context():
        db.sqldb.create_all()
    
    from .auth import auth
    app.register_blueprint(auth.bp)
    
    from .blog import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')
    
    return app