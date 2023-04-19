from flask import Flask, redirect, render_template
from flask_login import login_required, LoginManager

from data import db_session

from data.users import User
from data.cards import Card, Card_Page

from forms.authorizer_forms import RegisterForm

from forms.card_form import MainCardsForm, SmallCardsForm
from forms.pre_create_form import PreCreateForm

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
    cards = db_sess.query(Card).all()
    if len(cards) > 5:
        cards = cards[:5]
    return render_template("index.html", title='indexpage', cards=cards)


@app.route("/news")
def show_news():
    return """Тут пока пусто, но мы уже почти это исправили"""


@app.route("/cards")
def show_cards():
    db_sess = db_session.create_session()
    cards = db_sess.query(Card).all()
    return render_template("cards.html", title='catalogue', cards=cards)


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


cards = None
points = 0


@app.route('/new_card_pre', methods=['GET', 'POST'])
def start_to_add_cards():
    pre_form = PreCreateForm()
    if pre_form.validate_on_submit():
        global cards, points
        cards = Card()
        cards.points_count = pre_form.points_count.data
        cards.region = pre_form.region.data

        points = [i for i in range(1, cards.points_count * 2 + 1)]

        return redirect('/new_card')
    return render_template('pre_card.html', title='Добавление Маршрута',
                           form=pre_form)


@app.route('/new_card', methods=['GET', 'POST'])
def add_cards():
    global cards, points
    form = MainCardsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()

        cards.title = form.title.data
        cards.place = form.place.data
        cards.longest = form.longest.data
        #####
        cards.creator = 1

        db_sess.add(cards)
        db_sess.commit()
        return redirect('/create_card/1')
    return render_template('main_card.html', title='Добавление Маршрута', count=points,
                           form=form)


@app.route('/create_card/<int:number>', methods=['GET', 'POST'])
def add_page(number):
    global cards, points
    form = SmallCardsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        card = Card_Page()
        card.txt = form.text.data
        card.title = form.title.data
        card.picture = form.picture.data

        #####
        card.mother = 2

        db_sess.add(card)
        db_sess.commit()

        if number != points[-1]:
            return redirect(f'/create_card/{number + 1}')
        else:
            return redirect('/')

    if number % 2:
        return render_template('small_card.html', title=f'Расскажи о точке остановки{number}',
                               count=points,
                               form=form)
    else:
        return render_template('small_card.html',
                               title=f'Расскажи, как добирался от пункта {number - 1} до следующей остановки',
                               count=points,
                               form=form)


heads_in_card = 0

@app.route("/display_card/<int:number>")
def display_card(number):
    global heads_in_card, cards

    db_sess = db_session.create_session()
    cards = db_sess.query(Card).filter(Card.id == number).first()
    if cards:

        heads_in_card = [i for i in range(1, cards.points_count * 2 + 1)]
        return render_template('main_card_display.html', card = cards,
                               title=f'{cards.title}', count=heads_in_card)

@app.route("/display_card/page/<int:number>")
def display_page(number):

    global heads_in_card, cards

    db_sess = db_session.create_session()
    card = db_sess.query(Card_Page).filter(Card_Page.mother == cards.id).all()
    if len(card) == cards.points_count * 2:
        card = card[number - 1]
        return render_template('small_card_display.html',
                               title=f'{card.title}', count=heads_in_card)
    else:
        return """неполноценная карточка"""



def main():
    db_session.global_init("db/blogs.db")
    app.run()


if __name__ == '__main__':
    main()
