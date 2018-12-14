from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, BooleanField, RadioField
from wtforms.validators import DataRequired, EqualTo, ValidationError, Length
from app.models import User

ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg', 'gif']


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(message='Fill this field')])
    name = StringField('Name', validators=[DataRequired(message='Fill this field')])
    password = PasswordField('Password', validators=[DataRequired(message='Fill this field')])
    password2 = PasswordField(
        'Confirm Password',
        validators=[DataRequired(message='Fill this field'), EqualTo('password')]
    )
    photo = FileField('Your best photo', validators=[FileRequired(message='Upload a photo')])
    description = TextAreaField('Description', validators=[Length(min=0, max=500)])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username')

    def validate_photo(self, photo):
        if photo.data.filename.rsplit('.', 1)[1].lower() not in ALLOWED_EXTENSIONS:
            raise ValidationError('Please upload file with one of the following extensions: '
                                  + ', '.join(ALLOWED_EXTENSIONS))


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(message='Fill this field')])
    password = PasswordField('Password', validators=[DataRequired(message='Fill this field')])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Sign in')


class LikeForm(FlaskForm):
    like_or_dislike = RadioField('Like or dislike?', choices=[('Like', 'Like'), ('Dislike', 'Dislike')])
    submit = SubmitField('Confirm')


class MessageForm(FlaskForm):
    message = TextAreaField('Message', validators=[DataRequired(), Length(min=0, max=140)])
    submit = SubmitField('Send')
