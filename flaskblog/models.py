from datetime import datetime
from flaskblog import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    pais = db.Column(db.String(3), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)
    lol = db.Column(db.Boolean, default=False, nullable=False)
    rango_lol = db.Column(db.String(40), default="No juega")
    name_lol = db.Column(db.String(20), unique=True, default="")
    csgo = db.Column(db.Boolean, default=False, nullable=False)
    rango_csgo = db.Column(db.String(40), default="No juega")
    name_csgo = db.Column(db.String(20), unique=True, default="")
    connected_lol = db.Column(db.Boolean, default=False, nullable=False)
    connected_csgo = db.Column(db.Boolean, default=False, nullable=False)
    entrenador = db.Column(db.String, default="No es entrenador", nullable=False)
    

    def __repr__(self):
        return f"User('{self.username}'', '{self.email}'', '{self.image_file}'')"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    link_video = db.Column(db.String(100), default="")
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"