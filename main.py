import os

from flask import Flask, redirect, render_template, request, abort
from flask_login import login_required, LoginManager, login_user, logout_user, current_user
from werkzeug.utils import secure_filename

from data import db_session

from data.users import User
from data.cards import Card, Card_Page
from data.news import News

from forms.authorizer_forms import RegisterForm, LoginForm

from forms.card_form import MainCardsForm, SmallCardsForm
from forms.pre_create_form import PreCreateForm
from forms.news import NewsForm
from forms.forum import ForumForm

import requests


def region_coords(name):
    geocoder_request = f"http://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode={name}&format=json"

    # Выполняем запрос.
    response = requests.get(geocoder_request)
    if response:
        # Преобразуем ответ в json-объект
        json_response = response.json()

        # Получаем первый топоним из ответа геокодера.
        # Согласно описанию ответа, он находится по следующему пути:
        toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        # Координаты центра топонима:
        toponym_coodrinates = toponym["Point"]["pos"]

        return ','.join(toponym_coodrinates.split()[::-1])
    else:
        print("Ошибка выполнения запроса:")
        print(geocoder_request)
        print("Http статус:", response.status_code, "(", response.reason, ")")

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
    cards = sorted(db_sess.query(Card).all(), key=lambda x: x.loyality_counter, reverse=True)

    # db_sess.close()

    if len(cards) > 5:
        cards = cards[:5]
    return render_template("index.html", cards=cards)


@app.route('/news',  methods=['GET', 'POST'])
@login_required
def all_news():
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter((News.user == current_user) | (News.is_private != True))
    return render_template("all_news.html", news=news)

@app.route('/add_news',  methods=['GET', 'POST'])
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
        return redirect(f'/news')
    return render_template('news.html', title='Добавление новости',
                           form=form)


@app.route('/edit_news/<int:news_id>', methods=['GET', 'POST'])
@login_required
def edit_news(news_id):
    form = NewsForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == news_id,
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
        news = db_sess.query(News).filter(News.id == news_id,
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
            return redirect(f'/news')
        else:
            abort(404)
    return render_template('news.html',
                           title='Редактирование новости',
                           form=form
                           )


@app.route('/news_delete/<int:news_id>', methods=['GET', 'POST'])
@login_required
def news_delete(news_id):
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.id == news_id,
                                      News.user == current_user
                                      ).first()
    if news:
        db_sess.delete(news)
        db_sess.commit()
    else:
        abort(404)
    return redirect(f'/news')


@app.route('/reading_news/<int:news_id>', methods=['GET', 'POST'])
@login_required
def reading_news(news_id):
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.id == news_id,
                                      News.user == current_user
                                      ).first()
    return render_template('reading_news.html', news=news)


@app.route('/card_<int:card_id>/news',  methods=['GET', 'POST'])
@login_required
def card_news(card_id):
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter((News.card_id == card_id), (News.is_private != True))
    card = db_sess.query(Card).filter(Card.id == card_id).first()
    return render_template("card_news.html", news=news, card=card)


@app.route('/card_<int:card_id>/add_news',  methods=['GET', 'POST'])
@login_required
def add_news_card(card_id):
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
        news.card_id = card_id
        current_user.news.append(news)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect(f'/card_{card_id}/news')
    return render_template('news.html', title='Добавление новости',
                           form=form)


@app.route('/card_<int:card_id>/edit_news/<int:news_id>', methods=['GET', 'POST'])
@login_required
def edit_card_news(card_id, news_id):
    form = NewsForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == news_id,
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
        news = db_sess.query(News).filter(News.id == news_id,
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
            return redirect(f'/card_{card_id}/news')
        else:
            abort(404)
    return render_template('news.html',
                           title='Редактирование новости',
                           form=form
                           )


@app.route('/card_<int:card_id>/news_delete/<int:news_id>', methods=['GET', 'POST'])
@login_required
def card_news_delete(card_id, news_id):
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.id == news_id,
                                      News.user == current_user
                                      ).first()
    if news:
        db_sess.delete(news)
        db_sess.commit()
    else:
        abort(404)
    return redirect(f'/card_{card_id}/news')


@app.route('/card_<int:card_id>/reading_news/<int:news_id>', methods=['GET', 'POST'])
@login_required
def reading_card_news(card_id, news_id):
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.id == news_id,
                                      News.user == current_user
                                      ).first()
    return render_template('reading_news.html', news=news)


@app.route('/card_<int:card_id>/forum', methods=['GET', 'POST'])
@login_required
def forum(card_id):
    global username
    form = ForumForm()
    if form.submit.data:
        with open(f'files/forum{card_id}.txt', "a", encoding="utf8") as file:
            file.write(f"{form.content.data};{current_user.nickname};{current_user.id}\n")
    if username:
        form.content.data = f'@{username}, '
    try:
        with open(f'files/forum{card_id}.txt', "r", encoding="utf8") as file:
            content = file.readlines()
            content = [i.rsplit(';', 2) for i in content]
    except:
        with open(f'files/forum{card_id}.txt', "w", encoding="utf8") as file:
            content = []
    return render_template('forum.html', title='Форум', form=form, content=content, card_id=card_id)


@app.route('/card_<int:card_id>/forum/<nickname>', methods=['GET', 'POST'])
@login_required
def select_name(card_id, nickname):
    global username
    username = nickname
    return redirect(f'/card_{card_id}/forum')


@app.route("/cards")
def show_cards():
    db_sess = db_session.create_session()
    cards = sorted(db_sess.query(Card).all(), key=lambda x: x.loyality_counter, reverse=True)

    # db_sess.close()

    return render_template("cards.html", title='Каталог', cards=cards)


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
        db_sess.close()
        return redirect('/')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        db_sess.close()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


cards = Card()
points = []


@app.route('/new_card_pre', methods=['GET', 'POST'])
@login_required
def start_to_add_cards():
    pre_form = PreCreateForm()
    if pre_form.validate_on_submit():
        global cards, points

        cards.points_count = pre_form.points_count.data
        cards.region = pre_form.region.data

        points = [i for i in range(0, cards.points_count * 2 + 1)]

        return redirect(
        f'''/new_card_pre_map#type=hybrid&center={region_coords(cards.region)}&zoom=9''')

    return render_template('pre_card.html', title='Добавление Маршрута',
                           form=pre_form)

@app.route('/new_card_pre_map', methods=['GET', 'POST'])
def add_map():
    return render_template('pre_map.html', title='Добавление Карты', chng=False)

@app.route('/set_map/<string:arg>')
def set_map(arg):
    global cards
    cards.map = arg
    return redirect(f'''/new_card''')

@app.route('/new_card', methods=['GET', 'POST'])
def add_cards():
    global cards, points
    form = MainCardsForm()
    if form.validate_on_submit():

        db_sess = db_session.create_session()

        last = db_sess.query(Card).all()

        if last:
            cards.id = last[-1].id + 1
        else:
            cards.id = 1

        # need to check
        db_sess.close()

        cards.title = form.title.data
        cards.place = form.place.data
        cards.longest = form.longest.data
        cards.creator = current_user.id

        return redirect('/new_card/page/1')
    return render_template('main_card.html', title='Добавление Маршрута', count=points,
                           form=form, page=0)

@app.route('/start_corrector/<int:id>', methods=['GET', 'POST'])
def starter(id):
    global cards, points
    form = MainCardsForm()

    db_sess = db_session.create_session()
    cards = db_sess.query(Card).filter(Card.id == id,
                                       Card.creator == current_user.id
                                       ).first()

    if cards:
        points = [i for i in range(0, cards.points_count * 2 + 1)]
    else:
        abort(404)

    return redirect(f'/old_card_pre_map#{cards.map}')

@app.route('/old_card_pre_map', methods=['GET', 'POST'])
@login_required
def start_to_chng_map():
    return render_template('pre_map.html', title='Изменение Карты', chng=True)

@app.route('/chng_map/<string:arg>')
def chng_map(arg):
    global cards
    cards.map = arg
    return redirect(f'''/card/{cards.id}''')


@app.route('/card/<int:id>', methods=['GET', 'POST'])
@login_required
def change_cards(id):
    global cards, points

    form = MainCardsForm()

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


def size(el):
    return el.stream.seek(0, os.SEEK_END)


@app.route('/new_card/page/<int:number>', methods=['GET', 'POST'])
def add_page(number):
    global cards, points
    form = SmallCardsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        card = Card_Page()
        card.txt = form.text.data
        card.title = form.title.data

        file = form.picture.data
        if file:
            card.picture = f'static/img/{cards.id}_{number}.{file.filename.split(".")[-1]}'
            file.save(card.picture)

        card.mother = cards.id

        db_sess.add(card)
        db_sess.commit()

        if number != points[-1]:
            return redirect(f'/new_card/page/{number + 1}')
        else:
            db_sess.add(cards)
            db_sess.commit()
            db_sess.close()
            return redirect('/')

    if number % 2:
        return render_template('small_card.html', title=f'шаг {number}', page=number,
                               head=f'Расскажи о точке остановки №{number}',
                               count=points,
                               form=form)
    else:
        if number == points[-1]:
            return render_template('small_card.html', title=f'шаг {number}', page=number,
                                   head=f'Расскажи, как добираться в начало пути',
                                   count=points, delta=True,
                                   form=form)
        return render_template('small_card.html', title=f'шаг {number}', page=number,
                               head=f'Расскажи, как добирался от пункта №{number - 1} до следующей остановки',
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


            file = form.picture.data
            if file:
                card.picture = f'{cards.id}_{number}.{file.filename.split(".")[-1]}'
                file.save(f'static/img/{cards.id}_{number}.{file.filename.split(".")[-1]}')

            db_sess.add(card)
            db_sess.commit()

            if number != points[-1]:
                return redirect(f'/card/page/{number + 1}')
            else:
                db_sess.add(cards)
                db_sess.commit()

                #
                db_sess.close()

                return redirect('/')

    if number % 2:
        return render_template('small_card.html', title=f'шаг {number}', page=number,
                               head=f'Расскажи о точке остановки №{number}',
                               count=points,
                               form=form, delta=True)
    else:
        if number == points[-1]:
            return render_template('small_card.html', title=f'шаг {number}', page=number,
                                   head=f'Расскажи, как добираться в начало пути',
                                   count=points, delta=True,
                                   form=form)
        return render_template('small_card.html', title=f'шаг {number}', page=number,
                               head=f'Расскажи, как добирался от пункта №{number - 1} до следующей остановки',
                               count=points, delta=True,
                               form=form)


# heads_in_card = 0
@app.route("/display_card/<int:id>")
def load_card(id):
    global points, cards

    db_sess = db_session.create_session()
    cards = db_sess.query(Card).filter(Card.id == id).first()

    if cards:
        points = [i for i in range(1, cards.points_count * 2 + 1)]

        return redirect(f'/display_cards#{cards.map}')

    abort(404)



@app.route("/display_cards")
def display_card():
    global points, cards

    db_sess = db_session.create_session()
    cards = db_sess.query(Card).filter(Card.id == cards.id).first()

    if cards:
        return render_template('main_card_display.html', cards=cards, page=0,
                               title=f'{cards.title}', count=points)
    abort(404)


@app.route("/display_card/page/<int:number>")
def display_page(number):
    global points, cards

    db_sess = db_session.create_session()
    card = db_sess.query(Card_Page).filter(Card_Page.mother == cards.id).all()

    if card:
        card = card[number - 1]
        return render_template('small_card_display.html', card=card, cards=cards, page=number,
                               title=f'{card.title}', count=points)
    else:
        return """неполноценная карточка"""


@app.route('/card_delete/<int:id>', methods=['GET', 'POST'])
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


@app.route('/like/<string:arg>', methods=['GET'])
def cards_like(arg):
    id, number = map(int, arg.split('-'))

    db_sess = db_session.create_session()
    card = db_sess.query(Card).filter(Card.id == id).first()

    if card:
        if str(current_user.id) not in str(card.loyality).split():
            card.loyality = str(card.loyality) + ' ' + str(current_user.id)

            card.loyality_counter += 1
            card.creator_obj.loyality += 1

            db_sess.commit()
    else:
        abort(404)

    if number == 0:
        return redirect(f"/display_card/{id}")
    else:
        return redirect(f"/display_card/page/{number}")


def main():
    db_session.global_init("db/blogs.db")
    app.run()


if __name__ == '__main__':
    main()
