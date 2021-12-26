from flask import render_template, url_for,redirect, flash, request
from flaskblog.models import User
from flaskblog.forms import LoginForm, RegisterForm
from flaskblog import app, bcrypt, db
from flask_login import login_user, current_user, logout_user, login_required

data = [
    {
        'author' : 'Nithin Sai G M',
        'title' : 'My first post',
        'content' : 'Good Morning ',
        'date' : '22-12-2021'
    },
     {
        'author' : 'Siva kumar',
        'title' : 'Good morning post',
        'content' : 'Morning raises are always beautiful',
        'date' : '22-12-2021'
    }
]

# home page
@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html', data = data)

# about page
@app.route('/about')
def about():
    return render_template('about.html', title = 'about')

# register page
@app.route('/register', methods = ['POST','GET'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form  = RegisterForm()
    
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username = form.username.data, email = form.email.data, password = hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('You have registered Succesfully, Please login!','success')
        return redirect(url_for('login'))
    else:
        return render_template('register.html', title = 'register', form = form)

# login page
@app.route('/login', methods = ['POST', 'GET'])
def login():
    form = LoginForm()
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data) :
            login_user(user, remember = form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title = 'login', form = form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/account')
@login_required
def account():
    return render_template('account.html', title = 'account')