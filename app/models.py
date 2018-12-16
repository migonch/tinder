from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), unique=True)
    password_hash = db.Column(db.String(128))
    extension = db.Column(db.String(10))
    description = db.Column(db.String(500))
    confirmed = db.Column(db.Boolean, default=False)

    likes_from_me = db.relationship('Like',
                                    foreign_keys='Like.user_id',
                                    backref='user', lazy='dynamic')
    likes_to_me = db.relationship('Like',
                                  foreign_keys='Like.recipient_id',
                                  backref='recipient', lazy='dynamic')

    dislikes_from_me = db.relationship('Dislike',
                                       foreign_keys='Dislike.user_id',
                                       backref='user', lazy='dynamic')
    dislikes_to_me = db.relationship('Dislike',
                                     foreign_keys='Dislike.recipient_id',
                                     backref='recipient', lazy='dynamic')

    messages_sent = db.relationship('Message',
                                    foreign_keys='Message.sender_id',
                                    backref='author', lazy='dynamic')
    messages_received = db.relationship('Message',
                                        foreign_keys='Message.recipient_id',
                                        backref='recipient', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_ranked_candidates(self):
        candidates = set([user.id for user in db.session.query(User).all()])
        candidates -= {self.id}
        candidates -= set([like.recipient_id for like in self.likes_from_me])
        candidates -= set([like.recipient_id for like in self.dislikes_from_me])
        candidates -= set([like.recipient_id for like in self.dislikes_to_me])
        candidates = list(candidates)
        candidates.sort()
        return candidates


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Like(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)


class Dislike(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return '<Message {}>'.format(self.body)


def private_messages(user_id1, user_id2):
    return db.session.query(User, Message).filter(
        (User.id == Message.sender_id) & (
            ((Message.sender_id == user_id1) & (Message.recipient_id == user_id2)) |
            ((Message.sender_id == user_id2) & (Message.recipient_id == user_id1))
        )
    ).order_by(Message.timestamp).all()


def check_match(user_id1, user_id2):
    db.session.query(Like).filter_by(user_id=user_id1, recipient_id=user_id2).first_or_404()
    db.session.query(Like).filter_by(user_id=user_id2, recipient_id=user_id1).first_or_404()


def get_matches_usernames(user_id):
    return list(set([like.recipient.username for like in User.query.get(user_id).likes_from_me]) & \
                set([like.user.username for like in User.query.get(user_id).likes_to_me]))

