from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Email, Length, Regexp, EqualTo, ValidationError
from ..models import User


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(), Length(1, 64)])
    password = PasswordField('password', validators=[DataRequired()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log in')


class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(), Length(1, 64)])
    username = StringField('UserName', validators=[DataRequired(), Length(1, 64),
                                                   Regexp('^[A-Za-z\u4e00-\u9fa5][A-Za-z0-9_.\u4e00-\u9fa5]*$', 0,
                                                          'UserName must have only letters,numbers,dots or underscores')
                                                   ])

    password = PasswordField('password', validators=[DataRequired(), EqualTo('password2', 'Passwords must match.')])
    password2 = PasswordField('Confirm password', validators=[DataRequired()])
    submit = SubmitField('Register')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use')


class FindPasswordForm(FlaskForm):
    email = StringField('Input your Email(your account)',
                        validators=[DataRequired(), Email("Your email is invalidate"),
                                    Length(1, 64)])
    submit = SubmitField('Go!')

    def validate_email(self, field):
        if not User.query.filter_by(email=field.data).first():
            raise ValidationError('Email haven\'t registered.')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired(), EqualTo('password2', 'Passwords must match.')])
    password2 = PasswordField('Confirm password', validators=[DataRequired()])
    submit = SubmitField('Reset')
