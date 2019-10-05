import hashlib
from datetime import datetime

import bleach
from flask import current_app, request, url_for
from flask_login import UserMixin, AnonymousUserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadTimeSignature
from markdown import markdown
from werkzeug.security import generate_password_hash, check_password_hash

from app.exceptions import ValidationError
from . import db
from . import login_manager


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.FOLLOW | Permission.COMMENT | Permission.POST_ARTICLES, True),
            'Moderator': (Permission.FOLLOW | Permission.COMMENT | Permission.POST_ARTICLES |
                          Permission.MODERATE_COMMENTS, False),
            'Administrator': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()


class Follow(db.Model):
    __tablename__ = 'follow'
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    avatar = db.Column(db.String(128))

    followed = db.relationship('Follow', foreign_keys=[Follow.follower_id],
                               backref=db.backref('follower', lazy='joined'),
                               lazy='dynamic', cascade='all, delete-orphan')
    followers = db.relationship('Follow', foreign_keys=[Follow.followed_id],
                                backref=db.backref('followed', lazy='joined'),
                                lazy='dynamic', cascade='all, delete-orphan')

    def follow(self, user):
        if not self.is_following(user):
            f = Follow(followed=user, follower=self)
            db.session.add(f)
            db.session.commit()

    def unfollow(self, user):
        followed = self.find_following(user)
        if followed is not None:
            db.session.delete(followed)
            db.session.commit()

    def find_following(self, user):
        return self.followed.filter_by(followed_id=user.id).first()

    def is_following(self, user):
        return self.find_following(user) is not None

    def __init__(self, **kwargs):
        print("User init")
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
            if self.email is not None and self.avatar is None:
                self.avatar = hashlib.md5(self.email.encode('utf-8')).hexdigest()
        self.follow(self)

    def __repr__(self):
        return '<User %r>' % self.username

    @staticmethod
    def generate_fake(count=100):
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py
        seed()
        for i in range(count):
            u = User(email=forgery_py.internet.email_address(),
                     username=forgery_py.internet.user_name(True),
                     password=forgery_py.lorem_ipsum.word(),
                     confirmed=True,
                     location=forgery_py.address.city(),
                     about_me=forgery_py.lorem_ipsum.sentence(),
                     member_since=forgery_py.date.date(True))
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    @staticmethod
    def follow_them_self():
        users = User.query.all()
        for user in users:
            if not user.is_following(user):
                f = Follow(follower=user, followed=user)
                db.session.add(f)
        db.session.commit()

    @property
    def followed_posts(self):
        return Post.query.join(Follow, Follow.followed_id == Post.author_id) \
            .filter(Follow.follower_id == self.id)

    @property
    def comments(self):
        return self.posts.filter_by(post_type=PostType.COMMENT)

    @staticmethod
    def on_change_email(target, value, old_value, initiator):
        target.avatar = hashlib.md5(value.encode('utf-8')).hexdigest()

    def getAvatar(self, size=100, default='identicon', rating='g'):
        if request.is_secure:
            url = "https://secure.gravatar.com/avatar"
        else:
            url = 'http://www.gravatar.com/avatar'
        hash = self.avatar or hashlib.md5(self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash, default=default, rating=rating, size=size)

    def can(self, permissions):
        return self.role is not None and \
               (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    @property
    def password(self):
        raise AttributeError('password is not readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def generate_auth_token(self, uuid=None, expiration=3600 * 24):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        rs = s.dumps({'id': self.id, "uuid": uuid})
        if isinstance(rs, bytes):
            rs = rs.decode('utf-8')
        return rs

    @staticmethod
    def verify_auth_token(token, uuid):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
            if data.get('uuid') != uuid:
                raise ValueError("uuid exception")
        except Exception as e:
            print(e)
            return None
        return User.query.get(data['id'])

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
            if data.get('confirm') != self.id:
                return False, "token 不匹配"
            self.confirmed = True
            db.session.add(self)
            db.session.commit()
            return True, "success"
        except BadTimeSignature:
            return False, 'token已经失效，清重新认证'
        except Exception as e:
            return False, 'token 无法识别(%s)' % str(e)

    def ping(self):
        print("save last pin date")
        self.last_seen = datetime.utcnow()
        db.session.add(self)
        db.session.commit()

    def     to_json(self):
        json_post = {'url': url_for('api.get_user', id=self.id, _external=True),
                     'username': self.username,
                     'member_since': self.member_since,
                     'last_seen': self.last_seen,
                     'posts': url_for('api.get_user_posts', id=self.id, _external=True),
                     'followed_posts': url_for('api.get_user_follows_posts', id=self.id, _external=True),
                     'posts_count': self.posts.count()
                     }
        return json_post


class PostType:
    POST = 0x01
    COMMENT = 0x02


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    post_type = db.Column(db.Integer, default=PostType.POST)
    parent_post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    disabled = db.Column(db.Boolean, default=True)

    comments = db.relationship('Post', foreign_keys=[parent_post_id],
                               backref=db.backref('parent_post',
                                                  lazy='joined', remote_side=[id]),
                               cascade='all,delete-orphan',
                               lazy='dynamic'
                               )

    @staticmethod
    def generate_fake(count=100):
        from random import seed, randint
        import forgery_py
        seed()
        user_count = User.query.count()
        for i in range(count):
            u = User.query.offset(randint(0, user_count - 1)).first()
            p = Post(body=forgery_py.lorem_ipsum.sentences(randint(1, 3)), timestamp=forgery_py.date.date(True)
                     , author=u)
            db.session.add(p)
        db.session.commit()

    @staticmethod
    def on_change_body(target, value, old_value, initiator):
        allowed_tags = ['a', 'b', 'code',
                        'i', 'li', 'ol', 'pre', 'strong',
                        'h1', 'h2', 'h3', 'p', 'img', 'br', 'span', 'hr', ]
        allowed_attrs = {'img': ['alt', 'src'], '*': ['class'], 'a': ['href', 'rel']}
        target.body_html = bleach.clean(markdown(value, output_format='html'),
                                        tags=allowed_tags, attributes=allowed_attrs, strip=True)

    def to_json(self):
        if self.post_type == PostType.POST:
            json_post = {'url': url_for('api.get_post', id=self.id, _external=True),
                         'body': self.body,
                         'body_html': self.body_html,
                         'timestamp': str(self.timestamp),
                         'author': url_for('api.get_user', id=self.author_id, _external=True),
                         'comments': url_for('api.get_post_comments', id=self.id, _external=True),
                         'comments_count': self.comments.count()
                         }
        else:
            json_post = {'url': url_for('api.get_post_comment', parent_id=self.parent_post_id,
                                        id=self.id, _external=True),
                         'body': self.body,
                         'body_html': self.body_html,
                         'timestamp': str(self.timestamp),
                         'parent_post': url_for('api.get_post', id=self.parent_post_id, _external=True) \
                             if self.parent_post.post_type == PostType.POST else \
                             url_for('api.get_post_comment', parent_id=self.parent_post_id, id=self.id),
                         'author': url_for('api.get_user', id=self.author_id, _external=True),
                         'comments': url_for('api.get_post_comments', id=self.id, _external=True),
                         'comments_count': self.comments.count()
                         }

        return json_post

    @staticmethod
    def from_json(json_post, is_comment=False):
        body = json_post.get('body')
        if not body:
            raise ValidationError('post dosen\'s have body')
        return Post(body=body, post_type=PostType.COMMENT if is_comment else PostType.POST)


db.event.listen(Post.body, 'set', Post.on_change_body)
db.event.listen(User.email, 'set', User.on_change_email)


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False


login_manager.anonymous_user = AnonymousUser


class Permission:
    FOLLOW = 0x01
    COMMENT = 0x02
    POST_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x80


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
