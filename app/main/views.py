from flask import render_template, request, make_response, flash, abort, url_for, redirect, current_app
from flask_login import login_required, current_user

from app.decorator import admin_required, permission_required
from app.main.forms import EditProfileForm, EditProfileAdminForm, PostForm
from app.models import Permission, User, Role, Post
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


@main.route('/make_request')
def req():
    cookie = request.headers.get('Cookie')
    response = make_response('<h1> current Cookie is %s<h1>' % cookie)
    response.set_cookie('sessionId', 'wxn')
    return response


@main.route('/user/<id>')
def user(id):
    user = User.query.filter_by(id=id).first()
    if user is None:
        abort(404)
    posts = user.posts.order_by(Post.timestamp.desc()).all()
    return render_template("user/user.html", user=user, posts=posts)


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


@main.route('/admin')
@login_required
@admin_required
def for_admins_only():
    return "For admin only"


@main.route('/moderate')
@permission_required(Permission.MODERATE_COMMENTS)
def for_moderators():
    return "FOr moderator"


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
