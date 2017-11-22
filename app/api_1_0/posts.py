from flask import jsonify, request, g, url_for

from app import db
from app.api_1_0.decorators import permission_required
from app.api_1_0.errors import forbidden
from app.exceptions import ValidationError
from app.models import Post, User, Permission, PostType
from . import api
from .authentication import auth


@api.route("/posts/")
@auth.login_required
def get_posts():
    page = request.args.get("page", 1, type=int)
    size = request.args.get('size', 10, type=int)
    pagination = Post.query. \
        filter_by(post_type=PostType.POST). \
        order_by(Post.timestamp.desc()).paginate(page, size, error_out=False)
    posts = pagination.items
    next = url_for('.get_posts', page=page + 1, _external=True) if pagination.has_next else None
    prev = url_for('.get_posts', page=page - 1, _external=True) if pagination.has_prev else None
    count = pagination.total

    return jsonify(posts=[post.to_json() for post in posts], next=next, prev=prev, count=count)


@api.route('/posts/<int:id>')
@auth.login_required
def get_post(id):
    post = Post.query.get_or_404(id)
    return jsonify(post.to_json())


@api.route('/posts/<int:id>', methods=['PUT'])
@auth.login_required
@permission_required(Permission.MODERATE_COMMENTS | Permission.POST_ARTICLES)
def modify_post(id):
    if request.json and request.json.get('body'):
        post = Post.query.get_or_404(id)
        if g.current_user.can(Permission.MODERATE_COMMENTS) or post.author == g.current_user:
            post.body = request.json.get('body')
            db.session.add(post)
            db.session.commit()
        else:
            return forbidden("您不具备操作权限")
        return jsonify(post.to_json())
    else:
        raise ValidationError('body 是空的')


@api.route('/users/<int:id>/posts/')
def get_user_posts(id):
    user = User.query.get_or_404(id)
    return jsonify(posts=[post.to_json() for post in user.posts])


@api.route('/users/<int:id>/timeline/')
def get_user_follows_posts(id):
    user = User.query.get_or_404(id)
    return jsonify(posts=[post.to_json() for post in user.followed_posts])


@api.route('/posts/', methods=['POST'])
@auth.login_required
@permission_required(Permission.POST_ARTICLES)
def new_post():
    if request.json:
        post = Post.from_json(request.json)
        post.author = g.current_user
        db.session.add(post)
        db.session.commit()
        return jsonify(post.to_json()), 201
    else:
        raise ValidationError("body is Empty")


@api.route('/posts/<int:id>/comments/', methods=['POST'])
@auth.login_required
@permission_required(Permission.COMMENT)
def new_comment(id):
    if request.json:
        post = Post.from_json(request.json, True)
        post.author = g.current_user
        post.parent_post_id = id
        post.disabled = not g.current_user.confirmed
        db.session.add(post)
        db.session.commit()
        return jsonify(post.to_json()), 201
    else:
        raise ValidationError("body is Empty")


@api.route('/posts/<int:id>/comments/')
def get_post_comments(id):
    post = Post.query.get_or_404(id)
    return jsonify(comments=[comment.to_json() for comment in post.comments])


@api.route('/posts/<int:parent_id>/comments/<int:id>')
def get_post_comment(parent_id, id):
    return jsonify(comment=Post.query.get_or_404(id))
