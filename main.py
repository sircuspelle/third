from flask import Flask, redirect, render_template
from flask_login import login_required, LoginManager

from data import db_session

from data.users import User
from data.cards import Card

from forms.authorizer_forms import RegisterForm
from forms.card_form import CardsForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/")
def index():
    db_sess = db_session.create_session()

    return render_template("index.html", title='indexpage', cards=)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            nickname=form.nickname.data,
            region=form.region.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/index')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/new_card',  methods=['GET', 'POST'])
def add_cards():
    form = CardsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        cards = Card()
        cards.title = form.title.data
        cards.region = form.region.data
        cards.place = form.place.data
        cards.longest = form.longest.data
        #####
        cards.creator = 1

        db_sess.add(cards)
        db_sess.commit()
        return redirect('/')
    return render_template('card.html', title='Добавление Маршрут',
                           form=form)

def main():
    db_session.global_init("db/blogs.db")
    app.run()

if __name__ == '__main__':
    main()
