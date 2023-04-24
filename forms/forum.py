from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField


class ForumForm(FlaskForm):
    content = TextAreaField("")
    submit = SubmitField('Отправить')
