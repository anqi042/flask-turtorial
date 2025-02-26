from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, jsonify
)
from werkzeug.exceptions import abort

from ..auth.auth import login_required
from ..db.db import sqldb as db
from ..db.db import User, Post, Like,  UnLike
from sqlalchemy import desc, func

bp = Blueprint('blog', __name__,
               template_folder='templates',
               static_folder='static')

@bp.route('/')
def index():
    try:
        query = (
            Post.query
            .outerjoin(Like, Post.id == Like.post_id)  # 改为外连接
            .join(User, Post.author_id == User.id)
            .add_columns(
                Post.id,
                Post.title,
                Post.body,
                Post.created,
                Post.author_id,
                User.username,
                func.coalesce(func.count(Like.post_id), 0).label('likes')  # 处理空值
            )
            .group_by(Post.id)
            .order_by(desc(Post.created))
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

@bp.route('/blog/<int:post_id>/<int:user_id>/like', methods=['POST'])
@login_required
def like(post_id, user_id):
    print(f"like view {post_id}")
    # check if the user has already liked the post
    like = Like.query.filter_by(post_id=post_id, user_id=user_id).first()
    if like:
        # if the user has already liked the post, delete the like
        db.session.delete(like)
        db.session.commit()
        number =  Like.query.filter_by(post_id=post_id).count()
        return jsonify({'likes': number})

    like = Like(post_id=post_id, user_id=user_id)
    db.session.add(like)
    db.session.commit()

    # count the like number in the like table with post_id
    number =  Like.query.filter_by(post_id=post_id).count()

    return jsonify({'likes': number})