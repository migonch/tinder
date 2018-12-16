from app import app, db
from flask import render_template, redirect, request, url_for, flash
from app.forms import RegisterForm, LoginForm, LikeForm, MessageForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Like, Dislike, Message, private_messages, check_match, get_matches_usernames
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
import os
from app.token import generate_confirmation_token, confirm_token
from app.email import send_email
from app.decorators import check_confirmed


os.makedirs(os.path.join(app.static_folder, app.config['PHOTO_FOLDER']), exist_ok=True)


@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
@login_required
@check_confirmed
def home():
    candidates = current_user.get_ranked_candidates()
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
        photo = os.path.join(app.config['PHOTO_FOLDER'], secure_filename(user.username + user.extension))
    else:
        photo, form = None, None
    return render_template('home.html', title='Home', photo=photo, form=form)


@app.route('/about')
def about():
    return render_template('about.html', title='About')


@app.route('/matches')
@login_required
@check_confirmed
def matches():
    return render_template('matches.html', title='Matches', matches=get_matches_usernames(current_user.id))


@app.route('/private_chat/<recipient>', methods=['GET', 'POST'])
@login_required
@check_confirmed
def private_chat(recipient):
    user = User.query.filter_by(username=recipient).first_or_404()
    check_match(current_user.id, user.id)
    form = MessageForm()
    if form.validate_on_submit():
        msg = Message(author=current_user, recipient=user, body=form.message.data)
        db.session.add(msg)
        db.session.commit()
        flash('Your message has been sent')
        return redirect(url_for('private_chat', recipient=recipient))
    return render_template('private_chat.html', title='Private Chat', form=form, recipient=recipient)


@app.route('/private_chat/<recipient>/history', methods=['GET'])
@login_required
@check_confirmed
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
        user = User(username=form.username.data, email=form.email.data,
                    description=form.description.data, extension=extension)
        user.set_password(form.password.data)
        photo = request.files[form.photo.name]
        photo.save(os.path.join(app.static_folder,
                                app.config['PHOTO_FOLDER'],
                                secure_filename(form.username.data + extension)))
        db.session.add(user)
        db.session.commit()
        token = generate_confirmation_token(user.email)
        confirm_url = url_for('confirm_email', token=token, _external=True)
        send_email(subject="Please confirm your email",
                   sender=app.config['MAIL_DEFAULT_SENDER'],
                   recipients=[user.email],
                   html_body=render_template('activate.html', confirm_url=confirm_url))
        flash('A confirmation email has been sent via email.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/confirm/<token>')
def confirm_email(token):
    try:
        email = confirm_token(token)
    except:
        flash('The confirmation link is invalid or has expired.', 'danger')
    user = User.query.filter_by(email=email).first_or_404()
    if user.confirmed:
        flash('Account already confirmed. Please login.', 'success')
    else:
        user.confirmed = True
        db.session.add(user)
        db.session.commit()
        flash('You have confirmed your account. Thanks!', 'success')
    return redirect(url_for('login'))


@app.route('/unconfirmed')
@login_required
def unconfirmed():
    if current_user.confirmed:
        return redirect('main.home')
    return render_template('unconfirmed.html', title='Unconfirmed')


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
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))
