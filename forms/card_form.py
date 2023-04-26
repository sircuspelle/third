import os

from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import StringField, IntegerField, TextAreaField, SelectField, validators
from wtforms import BooleanField, SubmitField
from wtforms.validators import DataRequired, NumberRange, ValidationError

def extension_validate(form, field):
    try:
        if field.data.filename.split('.')[-1] not in ['png', 'jpg', 'jpeg']:
            raise ValidationError('image must be png, jpg or jpeg')
    except AttributeError:
        pass

def size_validate(form, field):
    try:
        if field.data.stream.seek(0, os.SEEK_END) > 3 * 1024 * 1024:
            raise ValidationError('image size must be 3MB or smaller')
    except AttributeError:
        pass

class MainCardsForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired()])

    place = StringField('Место', validators=[DataRequired()])

    longest = IntegerField('продолжительность',
                           validators=[DataRequired(), NumberRange(min=0, max=8760)])

    submit = SubmitField('Применить')


class SmallCardsForm(FlaskForm):
    title = StringField('Заглавие', validators=[DataRequired()])

    text = TextAreaField('Описание', validators=[DataRequired()])

    picture = FileField('Image File', validators=[extension_validate])

    submit = SubmitField('Применить')
