from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, ForeignKey
from flask_login import UserMixin
import os


database_path = os.environ["DATABASE_URL"]
db = SQLAlchemy()


def setup_db(app, database_path=database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config['SECRET_KEY'] = 'laimg ##ggserg%'
    db.app = app
    db.init_app(app)


def rollback():
    db.session.rollback()


class Question(db.Model):
    __tablename__ = "Question"

    id = Column(Integer, primary_key=True)
    title = Column(String())
    question = Column(String())
    answer = Column(String())
    subject = Column(String())
    user_id = Column(Integer, ForeignKey('user.id'))

    def format(self):
        return {
            "id": self.id,
            "title": self.title,
            "question": self.question,
            "img": self.img
        }

    def  insert ( self ):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class User(db.Model, UserMixin):
    id = Column(Integer, primary_key = True)
    email = Column(String(), unique=True)
    password = Column(String())
    first_name = Column(String())
    questions = db.relationship("Question")

