from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from ..auth.auth import login_required
from ..db.db import sqldb as db
from ..db.db import User, Post
from sqlalchemy import desc

bp = Blueprint('blog', __name__,
               template_folder='templates',
               static_folder='static')

@bp.route('/')
def index():
    try:
        # 使用 Flask-SQLAlchemy 的查询构造器
        query = (
            Post.query
            .join(User, Post.author_id == User.id)
            .add_columns(
                Post.id,
                Post.title,  # 假设 Post 模型中有一个名为 title 的字段
                Post.body,   # 假设 Post 模型中有一个名为 body 的字段（注意：原 SQL 中是 'body'，但常见字段名可能是 'content'）
                Post.created,  # 假设 Post 模型中有一个名为 created 的字段
                Post.author_id,
                User.username  # 从 User 模型中加入 username 字段
            )
            .order_by(desc(Post.created))  # 按照 created 字段降序排列
        )
 
        # 执行查询并获取结果
        results = query.all()
    except AttributeError as e:
        print(f"An error occurred: {e}")
        posts = []
    return render_template('./index.html', posts=results)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            new_post = Post(title = title, body = body, author_id = g.user.id)
            db.session.add(new_post)
            db.session.commit()
            return redirect(url_for('blog.index'))

    return render_template('./create.html')

def get_post(id, check_author=True):
    post = db.session.query(Post).filter_by(id = id).first()

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    #if check_author and post.author_id != g.user.id:
    #    abort(403)

    return post


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body  = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            new_post = db.session.query(Post).filter_by(id = id).first()
            new_post.title = title
            new_post.body  = body
            db.session.commit()
            return redirect(url_for('blog.index'))

    return render_template('./update.html', post=post)

@bp.route('/<int:id>/read', methods=('GET', 'POST'))
#@login_required
def read(id):
    post = get_post(id)

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    return render_template('./read.html', post=post)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db.session.delete(Post.query.filter_by(id = id).first())
    db.session.commit()
    return redirect(url_for('blog.index'))