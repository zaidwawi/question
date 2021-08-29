from logging import debug
from operator import sub
from re import U
from flask import Flask, request, abort, jsonify,render_template
from flask.helpers import flash, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy.engine import url
from sqlalchemy.sql.functions import user
from werkzeug.utils import redirect
from models import Question, User, setup_db, rollback
from flask_login import (
    UserMixin,
    current_user,
    login_user,
    logout_user,
    login_required,
    login_manager,
    LoginManager,
)
from werkzeug.security import check_password_hash, generate_password_hash
from flask_sqlalchemy import SQLAlchemy

def create_app(test_config=None):
    app = Flask(__name__)
    setup_db(app)
    CORS ( app )
    db = SQLAlchemy(app)


    login_manager = LoginManager()
    login_manager.login_view = "login"
    login_manager.init_app(app)


    @login_manager.user_loader
    def load_user(id):
        return User.query.get(id)




    @app.route('/')
    @login_required
    def home():   
        return  render_template('home.html', user = current_user)


    @app.route('/add', methods = ['GET', 'POST'])
    @login_required
    def add():
        if request.method == 'POST':
            title = request.form.get('title')
            question = request.form.get('question')
            answer = request.form.get('answer')
            subject = request.form.get('subjects')
            if subject == 'Choose Subject':
                flash('You must choose subject', category='error')
            else:
                add_question = Question(
                title = title,
                question = question,
                answer = answer,
                subject = subject,
                user_id = current_user.id
                )
                db.session.add(add_question)
                db.session.commit()
                flash(f'You have added question successfuly', category='true')
                return redirect(url_for('home'))
        return render_template('add.html' , user = current_user)

    @app.route('/delete/<int:id>', methods = ['GET', 'POST', 'DELETE'])
    @login_required
    def delete(id):
        delete = Question.query.get(id).delete()
        db.session.commit()
        flash('You have delete the question successfully')
        return redirect(url_for('home'))
    @app.route('/login', methods = ['GET', 'POST'])
    def login(): 
        if request.method == 'POST':
            email = request.form.get('email')
            password = request.form.get('password')
            
            user = User.query.filter_by(email = email ).first()
            if user:
                if check_password_hash(user.password, password):
                    login_user(user, remember=True)
                    flash(f"Welcome back {user.first_name}")
                    return redirect(url_for('home'))
                else:
                    flash('Your password is wrong !!', category='error')
            else:
                flash('Your email is Wrong !', category='error')
        return render_template('login.html' , user = current_user)
    
    @app.route('/logout')
    @login_required
    def logout():
        flash('You have logout successfully')
        logout_user()
        return redirect(url_for('login'))


    @app.route('/signup', methods=['GET', 'POST'])
    def sign():
        if request.method == 'POST':
            email = request.form.get('email', '')
            firstname = request.form.get('first_name')
            password = request.form.get('password')
            check_password = request.form.get('password_check')

            if len(email) < 6 :
                flash('Your Email is too Short !', category='error')
            elif len(firstname) < 2 :
                flash('Your firstname is too Short !', category='error')
            elif len(password) < 6 :
                flash('Your password is too Short !', category='error')
            elif password != check_password :
                flash('Your passwords does not match', category='error')
            else:
                add_user = User(
                    email = email,
                    first_name = firstname,
                    password = generate_password_hash(password, method="sha256")
                )
                db.session.add(add_user)
                db.session.commit()

                login_user(add_user, remember = True)
                flash('You have loged in successfully '+firstname)
                return redirect(url_for('home'))
        return render_template('signup.html', user = current_user)

    @app.route('/question/<user_id>/<int:id>', methods = ['GET', 'POST'])
    @login_required
    def get_question(user_id, id):
        try:
            question = Question.query.get(id)
            title = question.title
            questions = question.question
            answer = question.answer
            subject = question.subject
        except:
            return redirect(url_for('home'))
        return render_template('page.html', qq = question ,user=current_user, title = title, question = questions, answer = answer, subject = subject, uuu = current_user.questions)


    @app.route('/edit/<int:id>', methods = ['POST',"PATCH", 'GET'] )
    @login_required
    def edit(id):
        questions = Question.query.get(id)
        questions.question = request.form.get('questions')
        questions.title = request.form.get('titles')
        questions.answer = request.form.get('answers')
        questions.subject = request.form.get('subjects')
        questions.user_id = current_user.id
        questions.id = questions.id
        questions.update()
        db.session.commit()
        flash(f'you have update {questions.title} successfuly,  you will find your question at the end of the page')
        return redirect(url_for('home'))

    @app.route('/search')
    def search():
        return render_template('search.html', user = current_user)

    @app.route('/search', methods = ['GET', 'POST'])
    @login_required
    def searchs():
        if request.method == 'POST':
            search_term = request.form.get('search', None)

        # Return 422 status code if empty search term is sent
            if search_term == '':
                return render_template('search.html')

            try:
                # get all questions that has the search term substring
                if search_term:
                    questions = Question.query.filter(
                    Question.title.ilike(f'%{search_term}%')).all()

                # if there are no questions for search term return 404
                if len(questions) == 0:
                    abort(404)

                # paginate questions
        
            except Exception as e:
                print(e)

        if request.method == 'GET':
            pass

        return render_template('search.html', user = current_user, data = questions)
    return app 




APP = create_app()
if __name__ == '__main__':
    APP.run(debug=True)
