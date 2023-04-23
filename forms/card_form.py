from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, FileField, SelectField
from wtforms import BooleanField, SubmitField
from wtforms.validators import DataRequired, NumberRange


class MainCardsForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired()])

    place = StringField('Место', validators=[DataRequired()])

    longest = IntegerField('продолжительность',
                           validators=[DataRequired(), NumberRange(min=0, max=8760)])

    submit = SubmitField('Применить')


class SmallCardsForm(FlaskForm):
    title = StringField('Заглавие', validators=[DataRequired()])

    text = TextAreaField('Описание', validators=[DataRequired()])

    picture = FileField('Картинка')

    submit = SubmitField('Применить')
