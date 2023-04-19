from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, FileField, SelectField
from wtforms import BooleanField, SubmitField
from wtforms.validators import DataRequired


class MainCardsForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired()])

    place = StringField('Место')

    longest = IntegerField('продолжительность')

    submit = SubmitField('Применить')


class SmallCardsForm(FlaskForm):
    title = StringField('Заглавие', validators=[DataRequired()])

    text = TextAreaField('Описание', validators=[DataRequired()])

    picture = FileField('Картинка')

    submit = SubmitField('Применить')
