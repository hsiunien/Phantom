from flask import render_template, redirect, request, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadTimeSignature

from app.main.views import redirect_url
from . import auth
from .forms import LoginForm, RegistrationForm, FindPasswordForm, ResetPasswordForm
from .. import db
from ..email import send_email
from ..models import User


@auth.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):

            login_user(user, form.remember_me.data)
            if request.args.get('activate') == '1':
                token = request.args.get('token')
                email = request.args.get('email')
                # print("token:" + token)
                return redirect(url_for('.confirm', token=token, email=email))
            elif not user.confirmed:
                return redirect(url_for('.unconfirmed'))
            else:
                return redirect(redirect_url())
        else:
            flash('invalid username or password')
    form.email.data = request.args.get('email') or form.email.data
    return render_template('auth/login.html', form=form, hide_login=True)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out')
    return redirect(redirect_url())


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data, username=form.username.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('注册邮件已经发往您的邮箱：%s ,请注意查看邮件，Tips：若长时间没有收到邮件，有可能在邮箱垃圾箱中' % user.email, 'success')
        send_email(user.email, '注册成功', 'mail/new_user', user=user)
        return redirect(url_for('.login'))
    return render_template('auth/register.html', form=form)


@auth.route('/profile')
@login_required
def profile():
    return render_template('auth/profile.html')


@auth.route('/confirm/<token>/<email>')
def confirm(token, email):
    if not current_user.is_authenticated:
        return redirect(url_for('.login', token=token, email=email, activate=1))
    if current_user.confirmed:
        return redirect(url_for('main.home'))
    result, msg = current_user.confirm(token)
    if result:
        flash('您已经成功激活了您的账号, 欢迎加入我们', 'success')
    else:
        flash(msg)
        logout_user()
    return redirect(url_for('main.home'))


@auth.route('/confirmed')
@login_required
def confirmed():
    if current_user.confirmed:
        return redirect(url_for('main.home'))
    send_email(current_user.email, 'Re Confirm Your Account', 'mail/new_user', user=current_user)
    flash("we have sent your an email,please check your email first!", "success")
    return render_template('auth/unconfirm.html')


@auth.route('/unconformed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.home'))
    return render_template('auth/unconfirm.html')


@auth.before_request
def befor_request():
    # print(request.endpoint)
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.confirmed \
                and request.endpoint[:5] != 'auth.' \
                and request.endpoint != 'static':
            return redirect(url_for('auth.unconfirmed'))


@auth.route('/findpassword', methods=['POST', 'GET'])
def find_password():
    form = FindPasswordForm()
    if form.validate_on_submit():
        email = form.email.data
        user = User.query.filter_by(email=email).first()
        if user:
            send_email(email, "Reset password", 'mail/find_password', user=user, reset_key=generate_reset_key(user))
            flash("we send email successfully", "success")
        else:
            flash("couldn't load user")
    else:
        print("passed")

    return render_template('auth/find_password.html', form=form)


@auth.route('/reset_password/<reset_key>/<email>')
def reset_password(reset_key, email):
    print(reset_key, email)
    result, decode = decode_reset_key(reset_key)
    if result:
        print(decode)
        id = decode.get(email)
        u = User.query.filter_by(id=id).first()
        if u.email == email:
            login_user(u)
        else:
            return "error"
    else:
        return decode
    return render_template('auth/reset_password.html', form=ResetPasswordForm())


@auth.route('/reset_new_password', methods=["POST"])
def reset_new_password():
    form = ResetPasswordForm()
    reset_result = False
    if form.validate_on_submit():
        pwd = form.password.data
        current_user.password = pwd
        db.session.add(current_user)
        db.session.commit()
        flash("modify success", "success")
        reset_result = True
        logout_user()
    else:
        flash("modify failed", "warning")

    return render_template('auth/reset_password.html', form=form, reset_result=reset_result)


def generate_reset_key(user, expiration=3600):
    s = Serializer(current_app.config['SECRET_KEY'], expiration)
    return s.dumps({user.email: user.id})


def decode_reset_key(reset_key):
    s = Serializer(current_app.config['SECRET_KEY'])
    try:
        data = s.loads(reset_key)
        return True, data
    except BadTimeSignature:
        return False, 'token已经失效，清重新认证'
    except Exception as e:
        return False, 'token 无法识别(%s)' % str(e)
