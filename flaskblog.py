from flask import Flask, render_template, url_for

app = Flask(__name__)
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

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html', data = data, title = 'about')




if __name__ == '__main__':
    app.run(debug=True)