from flask import Flask, redirect, render_template, request, abort
from flask_login import login_required, LoginManager, login_user, logout_user, current_user

from data import db_session
from data.users import User
from data.cards import Card
from data.news import News

from forms.authorizer_forms import RegisterForm, LoginForm
from forms.card_form import CardsForm
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


@app.route("/")
def index():
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        news = db_sess.query(News).filter(
            (News.user == current_user) | (News.is_private != True))
    else:
        news = db_sess.query(News).filter(News.is_private != True)
    return render_template("index.html", news=news)


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


@app.route('/cards',  methods=['GET', 'POST'])
@login_required
def add_cards():
    pass
    form = CardsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        cards = Card()
        cards.title = form.title.data
        cards.region = form.region.data
        cards.place = form.place.data
        cards.longest = form.longest.data
        db_sess.add(cards)
        db_sess.commit()
        return redirect('/')
    return render_template('card.html', title='Добавление Маршрут',
                           form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


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


def main():
    db_session.global_init("db/blogs.db")
    app.run()


if __name__ == '__main__':
    main()
