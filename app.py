from flask import Flask, render_template, request, redirect
import re

app = Flask(__name__)

def is_valid_password(input_str):
    # Check if the input matches the pattern
    pattern = r"^(?=.*[0-9])(?=.*[\W_])(?!.*\s)[A-Za-z0-9\W_]{6,}$"
    
    return bool(re.match(pattern, input_str))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        #check if in database
        return 'Got it!' #redirect('/home.html')
    else:
        return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        #check if valid according to rules
        invalid = False
        if is_valid_password(password):
            pass #try to add to database
        else:
            invalid = True
            return render_template('signup.html', invalid=invalid)
        #add to database
        return 'Got it!' #redirect('/home.html')
    else:
        return render_template('signup.html')

if __name__ == '__main__':
    app.run(debug=True)
