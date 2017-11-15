from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, ValidationError, Email, Regexp

from app.models import User, Role
from flask_login import current_user


class NameForm(FlaskForm):
    name = StringField('What\'s your name?', validators=[DataRequired()])
    submit = SubmitField('Submit')


class EditProfileForm(FlaskForm):
    name = StringField('Name:', validators=[
        Length(1, 60),
        Regexp('^[A-Za-z\u4e00-\u9fa5][A-Za-z0-9_.\u4e00-\u9fa5]*$', 0,
               'UserName must have only letters,numbers,dots or underscores')
    ])
    location = StringField('Location:', validators=[Length(0, 64)])
    about_me = TextAreaField('About Me:')
    submit = SubmitField('Submit')

    def validate_name(self, field):
        if User.query.filter_by(username=field.data).first() is not None \
                and current_user.username != field.data:
            raise ValidationError("This name has been used")


class EditProfileAdminForm(FlaskForm):
    email = StringField('Email:', validators=[DataRequired(), Length(1, 64), Email()])
    username = StringField('UserName', validators=[DataRequired(), Length(1, 64),
                                                   Regexp('^[A-Za-z\u4e00-\u9fa5][A-Za-z0-9_.\u4e00-\u9fa5]*$', 0,
                                                          'UserName must have only letters,numbers,dots or underscores')
                                                   ])

    confirmed = BooleanField('Confirmed')
    role = SelectField('Role', coerce=int)
    location = StringField('Location:', validators=[Length(0, 64)])
    about_me = TextAreaField('About Me:')
    submit = SubmitField('Submit')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and \
                User.query.filter_by(email=field.data).first():
            raise ValidationError("Email has already registered")

    def validate_username(self, field):
        if field.data != self.user.username and \
                User.query.filter_by(username=field.data).first():
            raise ValidationError("User name has already in use")


class PostForm(FlaskForm):
    body = TextAreaField("What's on your mind?", validators=[DataRequired()])
    submit = SubmitField("Submit")
