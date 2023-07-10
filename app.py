from flask import Flask, render_template, request, redirect, session, send_from_directory
import services.users as user_service
import services.positions as position_service
import services.candidates as candidate_service
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

EXCLUDED_ROUTES = ['/', '/login', '/signup', '/signin-google', '/logout']

@app.before_request
def check_session():
    if request.path not in EXCLUDED_ROUTES and 'username' not in session and not request.path.startswith('/static'):
        return redirect('/')

@app.route('/')
def index():
    return render_template('index.html', landing_page=True)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        #check if in database
        result = user_service.login(username, password)
        if result['success']:
            session['username'] = username
            session['user_id'] = result['user'][0]
            session['email'] = result['user'][1]
            session['avatar'] = result['user'][4]
            return redirect('/home')
        else:
            return render_template('login.html', client_id=user_service.client_id(), **result['error'])
    else:
        return render_template('login.html', client_id=user_service.client_id())

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        #check if valid according to rules
        result = user_service.signup(email, username, password)
        if result['success']:
            return redirect('/login')
        else:
            return render_template('signup.html', client_id=user_service.client_id(), **result['error'])
    else:
        return render_template('signup.html', client_id=user_service.client_id())

@app.route('/signin-google', methods=['POST'])
def googleCallback():
    # Get authorization code Google sent back to you
    credential = request.form.get('credential')
    result = user_service.signin_google(credential)
    if result['success']:
        session['username'] = result['user'][2]
        session['user_id'] = result['user'][0]
        session['email'] = result['user'][1]
        session['avatar'] = result['user'][4]
        return redirect('/home')
    else:
        return render_template('signup.html', client_id=user_service.client_id(), **result['error'])

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')

@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if request.method == 'POST':
        old_password = request.form['old_password']
        new_password = request.form['new_password']
        result = user_service.change_password(session['user_id'], old_password, new_password)
        if result['success']:
            session.pop('username', None)
            return redirect('/login')
        else:
            return render_template('change_password.html', **result['error'], avatar=session['avatar'])
    else:
        return render_template('change_password.html', avatar=session['avatar'])

@app.route('/home')
def home():
    parameters = user_service.get_home(session['user_id'])
    return render_template('home.html', **parameters, avatar=session['avatar'])

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if request.method == 'POST':
        avatar = request.files['avatar']
        result = user_service.update_avatar(session['user_id'], avatar)
        if result['success']:
            session['avatar'] = result['avatar']
            return redirect('/profile')
        else:
            return render_template('profile.html', **result['error'], username=session['username'], email=session['email'], avatar=session['avatar'])
        
    else:
        return render_template('profile.html', username=session['username'], email=session['email'], avatar=session['avatar'])

@app.route('/positions')
def positions():
    positions = position_service.get_all()
    return render_template('positions.html', positions=positions, avatar=session['avatar'])

@app.route('/positions/add', methods=['GET', 'POST'])
def add_position():
    if request.method == 'POST':
        result = position_service.add(session['user_id'], request.form['title'], request.form['description'])
        if result['success']:
            return redirect('/positions')
        else:
            return render_template('add_position.html', **result['error'], avatar=session['avatar'])
    else:
        return render_template('add_position.html', avatar=session['avatar'])

@app.route('/positions/add/<string:position_id>', methods=['GET', 'POST'])
def duplicate_position(position_id):
    if request.method == 'POST':
        result = position_service.add(session['user_id'], request.form['title'], request.form['description'])
        if result['success']:
            return redirect('/positions')
        else:
            position = position_service.duplicate(position_id)
            return render_template('add_position.html', position=position, **result['error'], avatar=session['avatar'])
    else:
        position = position_service.duplicate(position_id)
        return render_template('add_position.html', position=position, avatar=session['avatar'])

@app.route('/positions/history')
def positions_history():
    positions = position_service.history()
    return render_template('positions_history.html', positions=positions, avatar=session['avatar'])

@app.route('/positions/<string:position_id>')
def position(position_id):
    result = position_service.get(position_id)
    return render_template('position.html', **result, avatar=session['avatar'])

@app.route('/positions/<string:position_id>/edit', methods=['GET', 'POST'])
def edit_position(position_id):
    if request.method == 'POST':
        result = position_service.edit(position_id, request.form['title'], request.form['description'])
        if result['success']:
            return redirect('/positions')
        else:
            return render_template('edit_position.html', **result['error'], position=result['position'], avatar=session['avatar'])
    else:
        position = position_service.get(position_id)['position']
        return render_template('edit_position.html', position=position, avatar=session['avatar'])

@app.route('/positions/<string:position_id>/archive')
def archive_position(position_id):
    position_service.archive(position_id)
    return redirect('/positions')

@app.route('/positions/<string:position_id>/activate')
def activate_position(position_id):
    position_service.activate(position_id)
    return redirect('/positions')

@app.route('/positions/<string:position_id>/add_candidate', methods=['GET', 'POST'])
def add_candidate(position_id):
    if request.method == 'POST':
        result = candidate_service.add(position_id, request.form['first_name'], request.form['last_name'], request.form['email'])
        if result['success']:
            return redirect(f'/positions/{position_id}')
        else:
            return render_template('add_candidate.html', **result['error'], avatar=session['avatar'])
    else:
        return render_template('add_candidate.html', avatar=session['avatar'])

@app.route('/positions/<string:position_id>/<string:candidate_id>')
def candidate(position_id, candidate_id):
    result = candidate_service.get(candidate_id)
    return render_template('candidate.html', **result, avatar=session['avatar'])

@app.route('/add_cv', methods=['GET', 'POST'])
def add_cv():
    if request.method == 'POST':
        cand_id = request.form['candidate']
        if 'cv' in request.files:
            result = candidate_service.add_cv(cand_id, request.files['cv'])
            if result['success']:
                return render_template('add_cv.html', **result['arguments'], avatar=session['avatar'])
            # else:
            #     candidates = candidate_service.get_all()
            #     return render_template('add_cv.html', **result['error'], candidates=candidates, avatar=session['avatar'])
        else:
            result = candidate_service.update(cand_id, request.form['email'], request.form['phone'], request.form['address'], request.form['postal_code'], request.form['city'], request.form['country'], request.form['birthdate'])
            if result['success']:
                return redirect(f'/positions/{result["pos_id"]}/{cand_id}')
            # else:
        candidates = candidate_service.get_all()
        return render_template('add_cv.html', **result['error'], candidates=candidates, avatar=session['avatar'])
    else:
        candidates = candidate_service.get_all()
        return render_template('add_cv.html', candidates=candidates, avatar=session['avatar'])

@app.route('/add_ml', methods=['GET', 'POST'])
def add_ml():
    if request.method == 'POST':
        cand_id = request.form['candidate']
        result = candidate_service.add_ml(cand_id, request.files['ml'])
        if result['success']:
            return redirect(f'/positions/{result["pos_id"]}/{cand_id}')
        else:
            candidates = candidate_service.get_all()
            return render_template('add_ml.html', **result['error'], candidates=candidates, avatar=session['avatar'])
    else:
        candidates = candidate_service.get_all()
        return render_template('add_ml.html', candidates=candidates, avatar=session['avatar'])

@app.route('/positions/<string:position_id>/<string:candidate_id>/view_cv')
def view_cv(position_id, candidate_id):
    result = candidate_service.view_cv(position_id, candidate_id)
    if result['success']:
        return send_from_directory(f"uploads/{position_id}/{candidate_id}", result['filename'])
    else:
        return redirect(f'/positions/{position_id}/{candidate_id}')

@app.route('/positions/<string:position_id>/<string:candidate_id>/view_ml')
def view_ml(position_id, candidate_id):
    result = candidate_service.view_ml(position_id, candidate_id)
    if result['success']:
        return send_from_directory(f"uploads/{position_id}/{candidate_id}", result['filename'])
    else:
        return redirect(f'/positions/{position_id}/{candidate_id}')

@app.route('/positions/<string:position_id>/<string:candidate_id>/del_cv')
def delete_cv(position_id, candidate_id):
    candidate_service.delete_cv(position_id, candidate_id)
    return redirect(f'/positions/{position_id}/{candidate_id}')

@app.route('/positions/<string:position_id>/<string:candidate_id>/del_ml')
def delete_ml(position_id, candidate_id):
    candidate_service.delete_ml(position_id, candidate_id)
    return redirect(f'/positions/{position_id}/{candidate_id}')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
