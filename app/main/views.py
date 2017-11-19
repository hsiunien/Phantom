from flask import render_template, request, make_response, flash, abort, url_for, redirect, current_app
from flask_login import login_required, current_user

from app.decorator import admin_required, permission_required
from app.main.forms import EditProfileForm, EditProfileAdminForm, PostForm
from app.models import Permission, User, Role, Post, Follow
from . import main
from .. import db


@main.route('/', methods=['POST', 'GET'])
def home():
    form = PostForm()
    if current_user.can(Permission.POST_ARTICLES) and form.validate_on_submit():
        post = Post(body=form.body.data, author=current_user._get_current_object())
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('.home'))
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()) \
        .paginate(page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)

    posts = pagination.items
    return render_template("index.html", form=form, posts=posts, pagination=pagination)


@main.route('/post/<int:id>')
def post(id):
    post = Post.query.get_or_404(id)
    return render_template('post.html', posts=[post])


@main.route('/edit_post/<int:id>', methods=['GET', 'POST'])
def edit_post(id):
    post = Post.query.get_or_404(id)
    form = PostForm()
    if current_user != post.author and \
            not current_user.can(Permission.MODERATE_COMMENTS):
        abort(403)

    if form.validate_on_submit():
        post.body = form.body.data
        db.session.add(post)
        db.session.commit()
        flash("The post has ben updated.", "success")
        return redirect(url_for('.post', id=post.id))

    form.body.data = post.body
    return render_template('edit_post.html', post=post, form=form)


@main.route('/delete_post/<int:id>', methods=['GET', 'POST'])
def delete_post(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and \
            not current_user.can(Permission.MODERATE_COMMENTS):
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash("The post has been deleted.", "success")
    return redirect(url_for('.home'))


@main.route('/user/<id>')
def user(id):
    user = User.query.filter_by(id=id).first()
    if user is None:
        abort(404)
    page = request.args.get('page', 1, type=int)
    pagination = user.posts.order_by(Post.timestamp.desc()) \
        .paginate(page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    total = pagination.total
    posts = pagination.items
    return render_template("user/user.html", user=user, posts=posts, pagination=pagination, total=total)


@main.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    edit_success = False
    if form.validate_on_submit():
        current_user.username = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        db.session.commit()
        flash("Your profile has benn updated.", "success")
        edit_success = True
    form.name.data = current_user.username
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('user/edit_profile.html', form=form, user=current_user, edit_success=edit_success)


@main.route('/edit_profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    edit_success = False
    if form.validate_on_submit():
        user.confirmed = form.confirmed.data
        user.cemail = form.email.data
        user.role = Role.query.get(form.role.data)
        user.username = form.username.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        db.session.commit()
        flash("User's profile has benn updated.", "success")
        edit_success = True
    form.username.data = user.username
    form.location.data = user.location
    form.about_me.data = user.about_me
    form.role.data = user.role_id
    form.email.data = user.cemail
    form.confirmed.data = user.confirmed
    return render_template('user/edit_profile.html', form=form, edit_success=edit_success, user=user)


@main.route('/moderate')
@permission_required(Permission.MODERATE_COMMENTS)
def for_moderators():
    return "FOr moderator"


@main.route('/follow/<int:id>')
@permission_required(Permission.FOLLOW)
@login_required
def follow(id):
    user = User.query.get(id)
    if user is not None:
        current_user.follow(user)
        flash("您已关注%s." % user.username, "success")
        return redirect(url_for('.user', id=id))


@main.route('/unfollow/<int:id>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(id):
    user = User.query.get(id)
    if user is not None:
        flash("您已取消关注%s." % user.username, "success")
        current_user.unfollow(user)
        return redirect(url_for('.user', id=id))


@main.route('/followers/<int:id>')
def followers(id):
    user = User.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.order_by(Follow.timestamp.desc()) \
        .paginate(page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)

    follows = [{'user': item.follower, 'timestamp': item.timestamp} for item in pagination.items]  # 蜜汁写法

    return render_template('user/followers.html', user=user, title="跟随者", endpoint='.followers', pagination=pagination,
                           follows=follows)


@main.route('/followed_post')
@login_required
def followed_posts():
    user = current_user
    page = request.args.get('page', 1, type=int)
    pagination = user.followed_posts.order_by(Post.timestamp.desc()) \
        .paginate(page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    posts = pagination.items
    return render_template('followed_posts.html', endpoint='.followed_posts', user=user, pagination=pagination,
                           posts=posts)


@main.route('/followed/<int:id>')
def followed(id):
    user = User.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    pagination = user.followed.order_by(Follow.timestamp.desc()) \
        .paginate(page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)

    follows = [{'user': item.followed, 'timestamp': item.timestamp} for item in pagination.items]  # 蜜汁写法
    return render_template('user/followers.html', user=user, title="关注", endpoint='.followers', pagination=pagination,
                           follows=follows)


@main.route('/user/<id>')
def find_user(id):
    user = load_user(id)
    if not user:
        abort(404)
    return make_response("login success")


@main.route('/secret')
def secret():
    return 'Only authenticated users are allowed'


def load_user(id):
    return None
