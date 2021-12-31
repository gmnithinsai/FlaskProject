from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from flaskblog import db, bcrypt
from flaskblog.models import User, Post
from flaskblog.users.forms import RegisterForm, LoginForm, AccountForm, RequestResetForm, ResetPasswordForm
from flaskblog.users.utils import save_picture, send_reset_email

users = Blueprint('users', __name__)

# register page
@users.route('/register', methods = ['POST','GET'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form  = RegisterForm()
    
    if form.validate_on_submit():
        # password encryption
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username = form.username.data, email = form.email.data, password = hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('You have registered Succesfully, Please login!','success')
        return redirect(url_for('users.login'))
    else:
        return render_template('register.html', title = 'register', form = form)

# login page
@users.route('/login', methods = ['POST', 'GET'])
def login():
    form = LoginForm()
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        # checks encrypted password and entered password matches
        if user and bcrypt.check_password_hash(user.password, form.password.data) : 
            login_user(user, remember = form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title = 'login', form = form)

@users.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.home'))

@users.route('/account', methods = ['POST','GET'])
@login_required
def account():
    form = AccountForm()
    if form.validate_on_submit(): # when update updates db and current user
        if form.picture.data :
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('users.account'))
    elif request.method == 'GET': # fills the user account details
        form.username.data = current_user.username
        form.email.data = current_user.email

    image_file = url_for('static', filename = 'images/'+ current_user.image_file) # path for images
    return render_template('account.html', title = 'Account', image_file = image_file, form = form)

@users.route('/user/<string:username>')
def user_posts(username):
    user = User.query.filter_by(username = username).first_or_404()
    page = request.args.get('page', 1, type = int)
    posts = Post.query.filter_by(author = user).order_by(Post.date_posted.desc()).paginate(page, per_page = 3)
    return render_template('user_posts.html', posts = posts, user = user)


@users.route('/reset_password', methods = ['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('users.login'))
    return render_template('reset_request.html', title = 'Reset Password', form = form)


@users.route('/reset_password/<token>', methods = ['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is invalid or expired token.','warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.add(user)
        db.session.commit()
        flash('Your password has been updated! you are now able to login','success')
        return redirect(url_for('users.login'))
    return render_template('reset_token.html', title = 'Reset Password', form = form)