from datetime import datetime
from hashlib import md5
from time import time
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

import jwt

from app import db, login
from sqlalchemy import ForeignKey, Column, Integer, DateTime
from sqlalchemy.orm import relationship

USER_ID = 'user.id'

followers = db.Table(
    'followers',
    db.Column('follower_id', db.Integer, db.ForeignKey(USER_ID)),
    db.Column('followed_id', db.Integer, db.ForeignKey(USER_ID))
)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    role = db.Column(db.String(10), default='User')
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    email = db.Column(db.String(120), index=True, unique=True)
    about_me = db.Column(db.String(140))
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
                followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.timestamp.desc())

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'],
            algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            user_id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except Exception:
            return
        return User.query.get(user_id)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey(USER_ID))
    language = db.Column(db.String(5))

    def __repr__(self):
        return '<Post {}>'.format(self.body)


class Photo(db.Model):

    __tablename__ = 'photo'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    folder = db.Column(db.String, default="app\static\images")
    filename = db.Column(db.String, unique=True)
    comment = db.Column(db.String)
    PersonIdFK = db.Column(db.Integer, ForeignKey('person.id'), default=0)

    def __repr__(self):
        return "[Id: {}, filename: {}, comment: {}, personIdFK: {}]".\
            format(self.id, self.filename, self.comment, self.PersonIdFK)


class Person(db.Model):

    __tablename__ = 'person'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    surname = db.Column(db.String)
    given_names = db.Column(db.String)
    gender = db.Column(db.String)
    year_born = db.Column(db.Integer)
    photos = relationship("Photo")

    def __repr__(self):
        return "[Id: {}, surname: {}, given names: {}, gender: {}, year born: {}]".\
            format(self.id, self.surname, self.given_names, self.gender, self.year_born)


class Quiz(db.Model):

    __table__ = 'quiz'

    quiz_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    # user_idFK == 0 means anonymous guest user took the quiz
    user_idFK = db.Column(db.Integer, db.ForeignKey(USER_ID), default=0)

    def __repr__(self):
        return "[Id: {}, date: {}, User: {}]".\
            format(self.quiz_id, self.timestamp, self.user_idFK)
