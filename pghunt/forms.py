from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, validators, IntegerField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from pghunt.models import User
from flask_login import current_user
# from flask_babel import _, lazy_gettext as _l
# from flask import request


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    account_type = SelectField('Register As', choices = [('pg_owner', 'PG Owner'), 
      ('customer', 'Customer')], validators=[DataRequired()])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please use another one')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please use another one')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class UpdateAcountForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg','png'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if username.data != current_user.username:
            if user:
                raise ValidationError('That username is taken. Please use another one')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if email.data != current_user.email:
            if user:
                raise ValidationError('That email is taken. Please use another one')


class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    details = TextAreaField('Details', validators=[DataRequired()])
    price = IntegerField('Price(Rs.)', [validators.NumberRange(min=1000, max=100000)])
    contact = StringField('Contact No', validators=[DataRequired(), Length(min=10, max=10)])
    address = TextAreaField('Address', validators=[DataRequired()])
    pg_picture = FileField('PG picture', validators=[FileAllowed(['jpg','png'])])
    submit = SubmitField('Post')


class BookForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=20)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=20)])
    contact = StringField('Contact No', validators=[DataRequired(), Length(min=10, max=10)])
    submit = SubmitField('Book')


class SearchForm(FlaskForm):
    search = StringField('Search', validators=[DataRequired()])
    submit = SubmitField('Search')

