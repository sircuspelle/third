from flask import Flask, redirect, render_template, request, abort
from flask_login import login_required, LoginManager, login_user, logout_user, current_user

from data import db_session

from data.users import User
from data.cards import Card, Card_Page
from data.news import News

from forms.authorizer_forms import RegisterForm, LoginForm

from forms.card_form import MainCardsForm, SmallCardsForm
from forms.pre_create_form import PreCreateForm
from forms.news import NewsForm
from forms.forum import ForumForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)


username = ''


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route("/")
def index():
    db_sess = db_session.create_session()
    cards = db_sess.query(Card).all()
    if len(cards) > 5:
        cards = cards[:5]
    if current_user.is_authenticated:
        news = db_sess.query(News).filter(
            (News.user == current_user) | (News.is_private != True))
    else:
        news = db_sess.query(News).filter(News.is_private != True)
    return render_template("index.html", cards=cards, news=news)


@app.route('/news',  methods=['GET', 'POST'])
@login_required
def add_news():
    form = NewsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = News()
        news.title = form.title.data
        if len(form.content.data) > 120:
            news.preview = form.content.data[:120:] + "..."
            news.content = form.content.data
        else:
            news.content = form.content.data
        news.is_private = form.is_private.data
        current_user.news.append(news)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('news.html', title='Добавление новости',
                           form=form)


@app.route('/news/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_news(id):
    form = NewsForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id,
                                          News.user == current_user
                                          ).first()
        if news:
            form.title.data = news.title
            form.content.data = news.content
            form.is_private.data = news.is_private
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id,
                                          News.user == current_user
                                          ).first()
        if news:
            news.title = form.title.data
            if len(form.content.data) > 120:
                news.preview = form.content.data[:120:] + "..."
                news.content = form.content.data
            else:
                news.preview = ''
                news.content = form.content.data
            news.is_private = form.is_private.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('news.html',
                           title='Редактирование новости',
                           form=form
                           )


@app.route('/news_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def news_delete(id):
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.id == id,
                                      News.user == current_user
                                      ).first()
    if news:
        db_sess.delete(news)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/reading_news/<int:id>', methods=['GET', 'POST'])
@login_required
def reading_news(id):
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.id == id,
                                      News.user == current_user
                                      ).first()
    return render_template('reading_news.html', news=news)


@app.route('/forum', methods=['GET', 'POST'])
@login_required
def forum():
    global username
    form = ForumForm()
    if username:
        form.content.data = f'@{username}, '
    if form.submit.data:
        with open('files/forum0.txt', "a", encoding="utf8") as file:
            file.write(f"{form.content.data};{current_user.nickname};{current_user.id}\n")
    with open('files/forum0.txt', "r", encoding="utf8") as file:
        content = file.readlines()
        content = [i.rsplit(';', 2) for i in content]
    return render_template('forum.html', title='Форум', form=form, content=content)


@app.route('/forum/<nickname>', methods=['GET', 'POST'])
@login_required
def select_name(nickname):
    global username
    username = nickname
    return redirect('/forum')


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
        return redirect('/')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


cards = Card()
points = 0


@app.route('/new_card_pre', methods=['GET', 'POST'])
@login_required
def start_to_add_cards():
    pre_form = PreCreateForm()
    if pre_form.validate_on_submit():
        global cards, points

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

        cards.id = db_sess.query(Card).all()[-1].id + 1

        cards.title = form.title.data
        cards.place = form.place.data
        cards.longest = form.longest.data
        cards.creator = current_user.id

        return redirect('/new_card/page/1')
    return render_template('main_card.html', title='Добавление Маршрута', count=points,
                           form=form, page=0)


@app.route('/card/<int:id>', methods=['GET', 'POST'])
@login_required
def change_cards(id):
    global cards, points
    form = MainCardsForm()

    db_sess = db_session.create_session()
    cards = db_sess.query(Card).filter(Card.id == id,
                                       Card.creator == current_user.id
                                       ).first()

    points = [i for i in range(1, cards.points_count * 2 + 1)]

    if request.method == "GET":
        if cards:
            form.title.data = cards.title
            form.place.data = cards.place
            form.longest.data = cards.longest
        else:
            abort(404)
    if form.validate_on_submit():
        if cards:
            cards.title = form.title.data
            cards.place = form.place.data
            cards.longest = form.longest.data
        return redirect('/card/page/1')
    return render_template('main_card.html', title='Изменение Маршрута', count=points,
                           form=form, delta=True, page=0)


@app.route('/new_card/page/<int:number>', methods=['GET', 'POST'])
def add_page(number):
    global cards, points
    form = SmallCardsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        card = Card_Page()
        card.txt = form.text.data
        card.title = form.title.data
        card.picture = form.picture.data
        card.mother = cards.id

        db_sess.add(card)
        db_sess.commit()

        if number != points[-1]:
            return redirect(f'/new_card/page/{number + 1}')
        else:
            db_sess.add(cards)
            db_sess.commit()
            return redirect('/')

    if number % 2:
        return render_template('small_card.html', title=f'шаг {number}', page=number,
                               head=f'Расскажи о точке остановки {number}',
                               count=points,
                               form=form)
    else:
        return render_template('small_card.html', title=f'шаг {number}', page=number,
                               head=f'Расскажи, как добирался от пункта {number - 1} до следующей остановки',
                               count=points,
                               form=form)


@app.route('/card/page/<int:number>', methods=['GET', 'POST'])
def change_page(number):
    global cards, points
    form = SmallCardsForm()

    db_sess = db_session.create_session()
    card = db_sess.query(Card_Page).filter(Card_Page.mother == cards.id).all()[number - 1]
    if request.method == "GET":
        if card:
            form.title.data = card.title
            form.text.data = card.txt
            form.picture.data = card.picture
        else:
            abort(404)
    if form.validate_on_submit():
        if card:
            card.txt = form.text.data
            card.title = form.title.data
            card.picture = form.picture.data

            db_sess.add(card)
            db_sess.commit()

            if number != points[-1]:
                return redirect(f'/card/page/{number + 1}')
            else:
                db_sess.add(cards)
                db_sess.commit()
                return redirect('/')

    if number % 2:
        return render_template('small_card.html', title=f'шаг {number}', page=number,
                               head=f'Расскажи о точке остановки {number}',
                               count=points,
                               form=form, delta=True)
    else:
        return render_template('small_card.html', title=f'шаг {number}', page=number,
                               head=f'Расскажи, как добирался от пункта {number - 1} до следующей остановки',
                               count=points, delta=True,
                               form=form)


heads_in_card = 0


@app.route("/display_card/<int:number>")
def display_card(number):
    global heads_in_card, cards

    db_sess = db_session.create_session()
    cards = db_sess.query(Card).filter(Card.id == number).first()
    if cards:
        heads_in_card = [i for i in range(1, cards.points_count * 2 + 1)]
        return render_template('main_card_display.html', cards=cards,
                               title=f'{cards.title}', count=heads_in_card)


@app.route("/display_card/page/<int:number>")
def display_page(number):
    global heads_in_card, cards

    db_sess = db_session.create_session()
    card = db_sess.query(Card_Page).filter(Card_Page.mother == cards.id).all()
    if card:
        card = card[number - 1]
        return render_template('small_card_display.html', card=card, cards=cards, page=number,
                               title=f'{card.title}', count=heads_in_card)
    else:
        return """неполноценная карточка"""


@app.route('/card_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def cards_delete(id):
    db_sess = db_session.create_session()
    cards = db_sess.query(Card).filter(Card.id == id,
                                       Card.creator == current_user.id
                                       ).first()
    if cards:
        db_sess.delete(cards)

        cards = db_sess.query(Card_Page).filter(Card_Page.mother == id,
                                                Card.creator == current_user.id
                                                ).all()
        for card in cards:
            db_sess.delete(card)

        db_sess.commit()
    else:
        abort(404)
    return redirect('/cards')


def main():
    db_session.global_init("db/blogs.db")
    app.run()


if __name__ == '__main__':
    main()
