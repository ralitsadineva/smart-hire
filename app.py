from flask import Flask, render_template, request, redirect, session
from database import create_tables, UniqueViolationError, DatabaseError, insert_user, insert_google_user, get_user, get_user_by_email, update_password,update_avatar, get_positions, insert_position, get_position, update_position, last_added_positions, last_updated_positions, positions_with_most_candidates, insert_candidate, get_candidate, get_candidates, get_all_candidates, update_candidate, last_added_candidates, last_updated_candidates, candidates_with_highest_cv_score, candidates_with_highest_motivation_lvl, insert_cv, get_cv, del_cv, insert_ml, get_ml, del_ml
from validation import is_valid_username, is_valid_password
import bcrypt
import logging
import secrets
import os
from datetime import datetime
from google.oauth2 import id_token
from google.auth.transport import requests
from get_google_client_id import get_google_client_id
from generate_random_password import generate_random_password
from read_pdf import read_pdf, page_count
from openai_eval import extract_cv, evaluate_cv, evaluate_ml
from convert_to_dict import convert_to_dict, convert_to_dict_extracted
from check_empty import check_empty
from get_greeting import get_greeting

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(name)s] %(levelname)s: %(message)s',
    # datefmt='%Y-%m-%d %H:%M:%S',
)
logger = logging.getLogger(__name__)

client_id = get_google_client_id()

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

@app.route('/')
def index():
    return render_template('index.html', landing_page=True)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        #check if in database
        user = get_user(username)
        if user is None or not bcrypt.checkpw(password.encode(), bytes(user[3])):
            return render_template('login.html', invalid=True)
        session['username'] = username
        session['user_id'] = user[0]
        session['email'] = user[1]
        session['avatar'] = user[4]
        return redirect('/home')
    else:
        return render_template('login.html', client_id=client_id)

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
                    return redirect('/login')
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
        return render_template('signup.html', client_id=client_id)

@app.route('/signin-google', methods=['POST'])
def googleCallback():
    # Get authorization code Google sent back to you
    credential = request.form.get('credential')
    logger.info(f"{credential}")
    try:
        idinfo = id_token.verify_oauth2_token(credential, requests.Request(), client_id)
        logger.info(f"{idinfo}")
    except ValueError:
        logger.error("Invalid token")
    email = idinfo['email']
    logger.info(f"{email}")
    user = get_user_by_email(email)
    if user is None:
        password = generate_random_password()
        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        try:
            insert_google_user(email, idinfo['sub'], hashed_password)
            user = get_user_by_email(email)
        except DatabaseError as error:
            logger.error(f"{type(error)}\n{error}")
            return render_template('signup.html', error=True)
    elif user[5] == '0': # check if google user, if not ...
        return render_template('login.html', exist=True)
    session['username'] = user[2]
    session['user_id'] = user[0]
    session['email'] = email
    session['avatar'] = user[4]
    return redirect('/home')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')

@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if 'username' not in session:
        return redirect('/')
    if request.method == 'POST':
        old_password = request.form['old_password']
        new_password = request.form['new_password']
        user = get_user(session['username'])
        if not bcrypt.checkpw(old_password.encode(), bytes(user[3])):
            return render_template('change_password.html', invalid=True, avatar=session['avatar'])
        if is_valid_password(new_password):
            hashed_password = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt())
            try:
                update_password(hashed_password, session['username'])
                return redirect('/login')
            except DatabaseError as error:
                logger.error(f"{type(error)}\n{error}")
                return render_template('change_password.html', error=True, avatar=session['avatar'])
        else:
            return render_template('change_password.html', invalid_password=True, avatar=session['avatar'])
    else:
        return render_template('change_password.html', avatar=session['avatar'])

@app.route('/home')
def home():
    if 'username' not in session:
        return redirect('/')
    parameters = {
        'greeting': get_greeting(),
        'last_added_pos': last_added_positions(),
        'last_updated_pos': last_updated_positions(),
        'last_added_cand': last_added_candidates(),
        'last_updated_cand': last_updated_candidates(),
        'most_applied_pos': positions_with_most_candidates(),
        'cand_highest_cv_score': candidates_with_highest_cv_score(),
        'cand_highest_motivation_lvl': candidates_with_highest_motivation_lvl()
    }
    return render_template('home.html', **parameters, avatar=session['avatar'])

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'username' not in session:
        return redirect('/')
    if request.method == 'POST':
        avatar = request.files['avatar']
        filename = f"{session['user_id']}/{datetime.now().strftime('%Y%m%d%H%M%S')}{os.path.splitext(avatar.filename)[1]}"
        if avatar.content_type.startswith('image/') and len(avatar.read()) < 2 * 1024 * 1024:
            if not os.path.exists(f"static/images/{session['user_id']}"):
                os.makedirs(f"static/images/{session['user_id']}")
            avatar.seek(0)
            avatar.save(f"static/images/{filename}")
            update_avatar(filename, session['username'])
            if session['avatar'] != 'user.png':
                if os.path.exists(f"static/images/{session['avatar']}"):
                    try:
                        os.remove(f"static/images/{session['avatar']}")
                    except OSError as error:
                        logger.error(f"{type(error)}\n{error}")
            session['avatar'] = filename
        else:
            return render_template('profile.html', invalid=True, username=session['username'], email=session['email'], avatar=session['avatar'])
        return redirect('/profile')
    else:
        return render_template('profile.html', username=session['username'], email=session['email'], avatar=session['avatar'])

@app.route('/positions')
def positions():
    if 'username' not in session:
        return redirect('/')
    positions = get_positions(session['user_id'])
    return render_template('positions.html', positions=positions, avatar=session['avatar'])

@app.route('/positions/add', methods=['GET', 'POST'])
def add_position():
    if 'username' not in session:
        return redirect('/')
    if request.method == 'POST':
        try:
            insert_position(session['user_id'], request.form['title'], request.form['description'])
            return redirect('/positions')
        except DatabaseError as error:
            logger.error(f"{type(error)}\n{error}")
            return render_template('add_position.html', error=True, avatar=session['avatar'])
    else:
        return render_template('add_position.html', avatar=session['avatar'])

@app.route('/positions/<string:position_id>')
def position(position_id):
    if 'username' not in session:
        return redirect('/')
    position = get_position(position_id)
    candidates = get_candidates(position_id)
    return render_template('position.html', position=position, candidates=candidates, avatar=session['avatar'])

@app.route('/positions/<string:position_id>/edit', methods=['GET', 'POST'])
def edit_position(position_id):
    if 'username' not in session:
        return redirect('/')
    if request.method == 'POST':
        try:
            update_position(position_id, request.form['title'], request.form['description'])
            return redirect('/positions')
        except DatabaseError as error:
            logger.error(f"{type(error)}\n{error}")
            return render_template('edit_position.html', error=True, position=position, avatar=session['avatar'])
    else:
        position = get_position(position_id)
        return render_template('edit_position.html', position=position, avatar=session['avatar'])

@app.route('/positions/<string:position_id>/add_candidate', methods=['GET', 'POST'])
def add_candidate(position_id):
    if 'username' not in session:
        return redirect('/')
    if request.method == 'POST':
        try:
            insert_candidate(position_id, request.form['first_name'], request.form['last_name'], request.form['email'])
            return redirect(f'/positions/{position_id}')
        except DatabaseError as error:
            logger.error(f"{type(error)}\n{error}")
            return render_template('add_candidate.html', error=True, position_id=position_id, avatar=session['avatar'])
    else:
        return render_template('add_candidate.html', position_id=position_id, avatar=session['avatar'])

@app.route('/positions/<string:position_id>/<string:candidate_id>')
def candidate(position_id, candidate_id):
    if 'username' not in session:
        return redirect('/')
    candidate = get_candidate(candidate_id)
    cv = get_cv(candidate_id)
    ml = get_ml(candidate_id)
    return render_template('candidate.html', candidate=candidate, cv=cv, ml=ml, avatar=session['avatar'])

@app.route('/add_cv', methods=['GET', 'POST'])
def add_cv():
    if 'username' not in session:
        return redirect('/')
    if request.method == 'POST':
        if 'cv' in request.files:
            cand_id = request.form['candidate']
            if get_cv(cand_id) is not None:
                candidates = get_all_candidates()
                return render_template('add_cv.html', exist=True, candidates=candidates, avatar=session['avatar'])
            cv = request.files['cv']
            if cv.content_type == 'application/pdf' and len(cv.read()) < 2 * 1024 * 1024:
                cv.seek(0)
                contents = read_pdf(cv)
                length = page_count(cv)
                candidate_info = extract_cv(contents)
                logger.info(candidate_info)
                try:
                    cand_info = convert_to_dict_extracted(candidate_info)
                except Exception as error:
                    logger.error(f"{type(error)}\n{error}")
                    candidates = get_all_candidates()
                    return render_template('add_cv.html', error=True, candidates=candidates, avatar=session['avatar'])
                # logger.info(cand_info)
                if get_candidate(cand_id)[2] != cand_info['First name'] or get_candidate(cand_id)[3] != cand_info['Last name']:
                    different_names = True
                else:
                    different_names = False
                response = evaluate_cv(contents)
                logger.info(response)
                try:
                    response_dict = convert_to_dict(response)
                except Exception as error:
                    logger.error(f"{type(error)}\n{error}")
                    candidates = get_all_candidates()
                    return render_template('add_cv.html', error=True, candidates=candidates, avatar=session['avatar'])
                score = sum(response_dict.values())
                try:
                    insert_cv(cand_id, score, response_dict['Structure and organization'], response_dict['Contact information'], response_dict['Work experience'], response_dict['Education'], response_dict['Skills'], response_dict['Languages'], length)
                except (DatabaseError, Exception) as error:
                    logger.error(f"{type(error)}\n{error}")
                    candidates = get_all_candidates()
                    return render_template('add_cv.html', error=True, candidates=candidates, avatar=session['avatar'])
            else:
                candidates = get_all_candidates()
                return render_template('add_cv.html', invalid=True, candidates=candidates, avatar=session['avatar'])
            candidate = get_candidate(cand_id)
            return render_template('add_cv.html', cand_info=cand_info, candidate=candidate, different_names=different_names, avatar=session['avatar'])
        else:
            cand_id = request.form['candidate']
            email = request.form['email']
            if email == '':
                email = get_candidate(cand_id)[4]
            phone = check_empty(request.form['phone'])
            address = check_empty(request.form['address'])
            postal_code = check_empty(request.form['postal_code'])
            city = check_empty(request.form['city'])
            country = check_empty(request.form['country'])
            birthdate = check_empty(request.form['birthdate'])
            try:
                update_candidate(cand_id, email, phone, address, postal_code, city, country, birthdate)
            except DatabaseError as error:
                logger.error(f"{type(error)}\n{error}")
                del_cv(cand_id)
                candidates = get_all_candidates()
                return render_template('add_cv.html', error=True, candidates=candidates, avatar=session['avatar'])
            return redirect(f'/positions/{get_candidate(cand_id)[1]}/{cand_id}')
    else:
        candidates = get_all_candidates()
        return render_template('add_cv.html', candidates=candidates, avatar=session['avatar'])

@app.route('/add_ml', methods=['GET', 'POST'])
def add_ml():
    if 'username' not in session:
        return redirect('/')
    if request.method == 'POST':
        cand_id = request.form['candidate']
        if get_ml(cand_id) is not None:
            candidates = get_all_candidates()
            return render_template('add_ml.html', exist=True, candidates=candidates, avatar=session['avatar'])
        ml = request.files['ml']
        if ml.content_type == 'application/pdf' and len(ml.read()) < 2 * 1024 * 1024:
            ml.seek(0)
            contents = read_pdf(ml)
            word_count = len(contents.split())
            # logger.info(word_count)
            response = evaluate_ml(contents)
            logger.info(response)
            try:
                response_dict = convert_to_dict(response)
            except:
                logger.error(f"{type(error)}\n{error}")
                candidates = get_all_candidates()
                return render_template('add_ml.html', error=True, candidates=candidates, avatar=session['avatar'])
            logger.info(response_dict)
            try:
                insert_ml(cand_id, response_dict['Motivation level'], response_dict['Overall sentiment'], response_dict['Tone'], word_count, response_dict['Grammar and language usage'])
            except DatabaseError as error:
                logger.error(f"{type(error)}\n{error}")
                candidates = get_all_candidates()
                return render_template('add_ml.html', error=True, candidates=candidates, avatar=session['avatar'])
        else:
            candidates = get_all_candidates()
            return render_template('add_ml.html', invalid=True, candidates=candidates, avatar=session['avatar'])
        return redirect(f'/positions/{get_candidate(cand_id)[1]}/{cand_id}')
    else:
        candidates = get_all_candidates()
        return render_template('add_ml.html', candidates=candidates, avatar=session['avatar'])

@app.route('/positions/<string:position_id>/<string:candidate_id>/del_cv')
def delete_cv(position_id, candidate_id):
    if 'username' not in session:
        return redirect('/')
    del_cv(candidate_id)
    return redirect(f'/positions/{position_id}/{candidate_id}')

@app.route('/positions/<string:position_id>/<string:candidate_id>/del_ml')
def delete_ml(position_id, candidate_id):
    if 'username' not in session:
        return redirect('/')
    del_ml(candidate_id)
    return redirect(f'/positions/{position_id}/{candidate_id}')

if __name__ == '__main__':
    create_tables()
    app.run(debug=True, host='0.0.0.0')
