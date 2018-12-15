from app import app, db
from flask import render_template, redirect, request, url_for, flash
from app.forms import RegisterForm, LoginForm, LikeForm, MessageForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Like, Dislike, Message, private_messages
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
import os


os.makedirs(os.path.join(app.static_folder, app.config['PHOTO_FOLDER']), exist_ok=True)


@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    candidates = current_user.get_ranked_candidates()
    print(candidates)
    if len(candidates):
        user = db.session.query(User).get(candidates[0])
        form = LikeForm()
        if form.validate_on_submit():
            if form.like_or_dislike.data == 'Like':
                like = Like(user_id=current_user.id, recipient_id=user.id)
                db.session.add(like)
                if db.session.query(Like).filter_by(user_id=user.id, recipient_id=current_user.id).scalar():
                    flash('You have a new pair!')
            else:
                dislike = Dislike(user_id=current_user.id, recipient_id=user.id)
                db.session.add(dislike)
            db.session.commit()
            return redirect('home')
        print(user.username)
        photo = os.path.join(app.config['PHOTO_FOLDER'], secure_filename(user.username + user.extension))
        print(photo)
    else:
        photo, form = None, None
    return render_template('home.html', title='Home', photo=photo, form=form)


@app.route('/private_chat/<recipient>', methods=['GET', 'POST'])
@login_required
def private_chat(recipient):
    user = User.query.filter_by(username=recipient).first_or_404()
    form = MessageForm()
    if form.validate_on_submit():
        msg = Message(author=current_user, recipient=user, body=form.message.data)
        db.session.add(msg)
        db.session.commit()
        flash('Your message has been sent')
        return redirect(url_for('private_chat', recipient=recipient))
    return render_template('private_chat.html', title='Private Chat', form=form, recipient=recipient)


@app.route('/private_chat/<recipient>/history', methods=['GET'])
def history(recipient):
    user = User.query.filter_by(username=recipient).first_or_404()
    messages = private_messages(current_user.id, user.id)
    return render_template('_history.html', messages=messages)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegisterForm()
    if form.validate_on_submit():
        extension = '.' + form.photo.data.filename.rsplit('.', 1)[1]
        user = User(username=form.username.data, name=form.name.data,
                    description=form.description.data, extension=extension)
        user.set_password(form.password.data)
        photo = request.files[form.photo.name]
        photo.save(os.path.join(app.static_folder,
                                app.config['PHOTO_FOLDER'],
                                secure_filename(form.username.data + extension)))
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('home')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))
