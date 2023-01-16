from flask import Flask, render_template, url_for, redirect, flash, request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from form import RegisterUser, Login, CreateTask
from flask_bootstrap import Bootstrap

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
Bootstrap(app)


login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    user = db.relationship('BlogPost', backref='user')


class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=False)
    done = db.Column(db.Boolean, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



@app.route('/')
def home():
    print(current_user)
    return render_template('index.html', logged_in=current_user.is_authenticated)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterUser()
    if form.validate_on_submit():
        email = form.email.data
        if User.query.filter_by(email=email).first():
            flash('You are already registered with this email. Come in.')
            return redirect(url_for('register'))
        new_user = User(
            name=form.name.data,
            email=form.email.data,
            password=generate_password_hash(form.password.data, salt_length=8))
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('register.html', form=form, logged_in=current_user.is_authenticated)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = Login()
    user = User.query.filter_by(email=form.email.data).first()
    if form.validate_on_submit():
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('Incorrect password or email')
            return redirect(url_for('login'))
    return render_template('login.html', form=form, logged_in=current_user.is_authenticated)

@app.route('/tasks')
def tasks():
    task = BlogPost.query.filter_by(user_id=current_user.id)
    return render_template('tasks.html', task=task, logged_in=current_user.is_authenticated)

@app.route('/add_task', methods=['POST', 'GET'])
def add_task():
    form = CreateTask()
    if form.validate_on_submit():
        new_task = BlogPost(
            body=form.title.data,
            done=False,
            user_id=current_user.id)
        db.session.add(new_task)
        db.session.commit()
        return redirect('tasks')
    return render_template('add_task.html', form=form, logged_in=current_user.is_authenticated)

@app.route('/logout')
def logout():
    logout_user()
    print(current_user)
    return redirect(url_for('home'))


@app.route('/delete/<int:task_id>')
def delete(task_id):
    task = BlogPost.query.get(task_id)
    db.session.delete(task)
    db.session.commit()
    return redirect('/tasks')

@app.route('/toggle/<int:task_id>', methods=['POST', "GET"])
def toggle(task_id):
    if request.method == 'GET':
        task = BlogPost.query.get(task_id)
        task.done = not task.done
        db.session.commit()
        return redirect('/tasks')

app.run(debug=True)
