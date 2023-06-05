from flask import Flask, render_template, request, redirect
from database import create_tables, UniqueViolationError, DatabaseError, insert_user, get_user, update_password
from validation import is_valid_username, is_valid_password
import bcrypt
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(name)s] %(levelname)s: %(message)s',
    # datefmt='%Y-%m-%d %H:%M:%S',
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        #check if in database
        user = get_user(username)
        if user is None or not bcrypt.checkpw(password.encode(), bytes(user[3])):
            return render_template('login.html', invalid=True)
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
        if is_valid_username(username):
            if is_valid_password(password):
                hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
                try:
                    insert_user(email, username, hashed_password)
                    return 'You registered succesfully!' #redirect('/home.html')
                except UniqueViolationError as e:
                    logger.error(f"{type(e)}\n{e}")
                    return render_template('signup.html', exist=True) 
                except DatabaseError as error:
                    logger.error(f"{type(error)}\n{error}")
                    return render_template('signup.html', error=True)
            else:
                return render_template('signup.html', invalid_password=True)
        else:
            return render_template('signup.html', invalid_username=True)
    else:
        return render_template('signup.html')

@app.route('/logout')
def logout():
    #session.pop('username', None)
    return redirect('/')

@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    # if 'username' not in session:
    #     return redirect('/')
    if request.method == 'POST':
        old_password = request.form['old_password']
        new_password = request.form['new_password']
        user = get_user(username) #session['username']
        if not bcrypt.checkpw(old_password.encode(), bytes(user[3])):
            return render_template('change_password.html', invalid=True)
        if is_valid_password(new_password):
            hashed_password = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt())
            try:
                update_password(hashed_password, username) #session['username']
                return 'You changed your password succesfully!' #redirect('/home.html')
            except DatabaseError as error:
                logger.error(f"{type(error)}\n{error}")
                return render_template('change_password.html', error=True)
        else:
            return render_template('change_password.html', invalid_password=True)
    else:
        return render_template('change_password.html')

@app.route('/home')
def home():
    # if 'username' not in session:
    #     return redirect('/')
    return render_template('home.html')

if __name__ == '__main__':
    create_tables()
    app.run(debug=True, host='0.0.0.0')
