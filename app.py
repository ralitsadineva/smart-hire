from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    #return render_template('login.html')
    pass

@app.route('/signup')
def signup():
    #return render_template('signup.html')
    pass

if __name__ == '__main__':
    app.run(debug=True)
