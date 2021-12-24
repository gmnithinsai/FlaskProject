from flask import Flask, render_template, url_for,redirect, flash

from forms import LoginForm, RegisterForm

app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
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
def home():
    return render_template('home.html', data = data)

# about page
@app.route('/about')
def about():
    return render_template('about.html', title = 'about')

# register page
@app.route('/register', methods = ['POST','GET'])
def register():
    form  = RegisterForm()
    if form.validate_on_submit():
        flash('You have registered Succesfully!','success')
        return redirect(url_for('home'))
    else:
        return render_template('register.html', title = 'register', form = form)

# login page
@app.route('/login', methods = ['POST', 'GET'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == 'gmnithinsai2599@gmail.com' and form.password.data == '1234':
            flash('You have succesfully logged in!','success')
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title = 'login', form = form)




if __name__ == '__main__':
    app.run(debug=True)