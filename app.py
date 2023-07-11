from flask import Flask, render_template, request, redirect, session
from controllers.users import login, signup, googleCallback, logout, change_password, home, profile
from controllers.positions import positions, add_position, duplicate_position, positions_history, position, edit_position, archive_position, activate_position
from controllers.candidates import add_candidate, candidate, add_cv, add_ml, view_cv, view_ml, delete_cv, delete_ml
import secrets
import logging

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(name)s] %(levelname)s: %(message)s',
    # datefmt='%Y-%m-%d %H:%M:%S',
)

EXCLUDED_ROUTES = ['/', '/login', '/signup', '/signin-google', '/logout']

@app.before_request
def check_session():
    if request.path not in EXCLUDED_ROUTES and 'username' not in session and not request.path.startswith('/static'):
        return redirect('/')

@app.route('/')
def index():
    return render_template('index.html', landing_page=True)

app.add_url_rule('/login', 'login', login, methods=['GET', 'POST'])
app.add_url_rule('/signup', 'signup', signup, methods=['GET', 'POST'])
app.add_url_rule('/signin-google', 'googleCallback', googleCallback, methods=['POST'])
app.add_url_rule('/logout', 'logout', logout)
app.add_url_rule('/change_password', 'change_password', change_password, methods=['GET', 'POST'])
app.add_url_rule('/home', 'home', home)
app.add_url_rule('/profile', 'profile', profile, methods=['GET', 'POST'])

app.add_url_rule('/positions', 'positions', positions)
app.add_url_rule('/positions/add', 'add_position', add_position, methods=['GET', 'POST'])
app.add_url_rule('/positions/add/<string:position_id>', 'duplicate_position', duplicate_position, methods=['GET', 'POST'])
app.add_url_rule('/positions/history', 'positions_history', positions_history)
app.add_url_rule('/positions/<string:position_id>', 'position', position)
app.add_url_rule('/positions/<string:position_id>/edit', 'edit_position', edit_position, methods=['GET', 'POST'])
app.add_url_rule('/positions/<string:position_id>/archive', 'archive_position', archive_position)
app.add_url_rule('/positions/<string:position_id>/activate', 'activate_position', activate_position)

app.add_url_rule('/positions/<string:position_id>/add_candidate', 'add_candidate', add_candidate, methods=['GET', 'POST'])
app.add_url_rule('/positions/<string:position_id>/<string:candidate_id>', 'candidate', candidate)
app.add_url_rule('/add_cv', 'add_cv', add_cv, methods=['GET', 'POST'])
app.add_url_rule('/add_ml', 'add_ml', add_ml, methods=['GET', 'POST'])
app.add_url_rule('/positions/<string:position_id>/<string:candidate_id>/view_cv', 'view_cv', view_cv)
app.add_url_rule('/positions/<string:position_id>/<string:candidate_id>/view_ml', 'view_ml', view_ml)
app.add_url_rule('/positions/<string:position_id>/<string:candidate_id>/del_cv', 'delete_cv', delete_cv)
app.add_url_rule('/positions/<string:position_id>/<string:candidate_id>/del_ml', 'delete_ml', delete_ml)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
