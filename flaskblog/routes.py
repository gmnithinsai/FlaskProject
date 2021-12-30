import secrets
import os
from PIL import Image
from flask import render_template, url_for,redirect, flash, request, abort
from flaskblog.models import User, Post
from flaskblog.forms import AccountForm, LoginForm, PostForm, RegisterForm, RequestResetForm, ResetPasswordForm
from flaskblog import app, bcrypt, db, mail
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message

# home page
@app.route('/')
@app.route('/home')
def home():
    page = request.args.get('page', 1, type = int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page, per_page = 3)
    return render_template('home.html', posts = posts)
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
        # password encryption
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
        # checks encrypted password and entered password matches
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

def save_picture(form_picture):
    random_hex = secrets.token_hex(8) # hexadecimal value of 8bits
    _, f_ext = os.path.splitext(form_picture.filename) # splits file name and extension
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/images', picture_fn)
    # converting image size to 125 pixels
    image_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(image_size)
    i.save(picture_path)
    return picture_fn


@app.route('/account', methods = ['POST','GET'])
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
        return redirect(url_for('account'))
    elif request.method == 'GET': # fills the user account details
        form.username.data = current_user.username
        form.email.data = current_user.email

    image_file = url_for('static', filename = 'images/'+ current_user.image_file) # path for images
    return render_template('account.html', title = 'Account', image_file = image_file, form = form)

@app.route('/post/new', methods = ['POST', 'GET'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
         post = Post(title = form.title.data, content = form.content.data, author = current_user)
         db.session.add(post)
         db.session.commit()
         flash('Your post have been updated!', 'success')
         return redirect(url_for('home'))
    return render_template('create_post.html', title = 'New Post', form = form)

@app.route('/post/int:<post_id>', methods = ['POST', 'GET'])
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title = post.title, post = post)

@app.route('/post/int:<post_id>/update', methods = ['POST', 'GET'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('post', post_id = post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content

    return render_template('create_post.html', title = 'Update', form = form)

@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('home'))

@app.route('/user/<string:username>')
def user_posts(username):
    user = User.query.filter_by(username = username).first_or_404()
    page = request.args.get('page', 1, type = int)
    posts = Post.query.filter_by(author = user).order_by(Post.date_posted.desc()).paginate(page, per_page = 3)
    return render_template('user_posts.html', posts = posts, user = user)


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender = 'gmnithinsai@gmail.com', recipients = [user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token = token, _external = True)}

If you did not make this request please ignore this email and no changes will be made.
    '''
    pass

@app.route('/reset_password', methods = ['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title = 'Reset Password', form = form)


@app.route('/reset_password/<token>', methods = ['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is invalid or expired token.','warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.add(user)
        db.session.commit()
        flash('Your password has been updated! you are now able to login','success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title = 'Reset Password', form = form)