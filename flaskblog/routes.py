import secrets
import os
from PIL import Image
from flask import render_template, url_for,redirect, flash, request, abort
from flaskblog.models import User, Post
from flaskblog.forms import AccountForm, LoginForm, PostForm, RegisterForm
from flaskblog import app, bcrypt, db
from flask_login import login_user, current_user, logout_user, login_required


# home page
@app.route('/')
@app.route('/home')
def home():
    posts = Post.query.all()
    print(posts)
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


