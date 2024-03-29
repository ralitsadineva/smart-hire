from models.user_repo import UserRepository
from models.position_repo import PositionRepository
from models.candidate_repo import CandidateRepository
from exceptions import DatabaseError, UniqueViolationError
from validation import is_valid_username, is_valid_password
from utils import get_greeting, get_name
from constants import LOGIN_TYPE_PASSWORD, LOGIN_TYPE_GOOGLE, DEFAULT_AVATAR
from google_service import get_google_client_id, generate_random_password
from google.oauth2 import id_token
from google.auth.transport import requests
from datetime import datetime
import os
import bcrypt
import logging

logger = logging.getLogger(__name__)

users_db = UserRepository()
positions_db = PositionRepository()
candidates_db = CandidateRepository()

def login(username, password):
    user = users_db.get_by_username(username)
    if user is None or not bcrypt.checkpw(password.encode(), bytes(user['password'])):
        return {'success': False, 'error': {'invalid': True}}
    return {'success': True, 'user': user}

def signup(email, username, password):
    if is_valid_username(username):
        if is_valid_password(password):
            hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
            try:
                users_db.insert(email, username, hashed_password, LOGIN_TYPE_PASSWORD)
                return {'success': True}
            except UniqueViolationError as e:
                logger.error(f"{type(e)}\n{e}")
                return {'success': False, 'error': {'exist': True}} 
            except DatabaseError as error:
                logger.error(f"{type(error)}\n{error}")
                return {'success': False, 'error': {'error': True}}
        else:
            return {'success': False, 'error': {'invalid_password': True}}
    else:
        return {'success': False, 'error': {'invalid_username': True}}

def signin_google(credential):
    try:
        client_id = get_google_client_id()
        idinfo = id_token.verify_oauth2_token(credential, requests.Request(), client_id)
    except ValueError:
        logger.error("Invalid token")
    email = idinfo['email']
    user = users_db.get_by_email(email)
    if user is None:
        password = generate_random_password()
        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        try:
            users_db.insert(email, idinfo['sub'], hashed_password, LOGIN_TYPE_GOOGLE)
            user = users_db.get_by_email(email)
        except DatabaseError as error:
            logger.error(f"{type(error)}\n{error}")
            return {'success': False, 'error': {'error': True}}
    elif user['type'] == LOGIN_TYPE_PASSWORD:
        return {'success': False, 'error': {'exist': True}}
    return {'success': True, 'user': user}

def change_password(id, old_password, new_password):
    user = users_db.get(id)
    if not bcrypt.checkpw(old_password.encode(), bytes(user['password'])):
        return {'success': False, 'error': {'invalid': True}}
    if is_valid_password(new_password):
        hashed_password = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt())
        try:
            users_db.update_password(hashed_password, id)
            return {'success': True}
        except DatabaseError as error:
            logger.error(f"{type(error)}\n{error}")
            return {'success': False, 'error': {'error': True}}
    else:
        return {'success': False, 'error': {'invalid_password': True}}
    
def get_home(id):
    return {
        'greeting': get_greeting(),
        'username': get_name(users_db.get(id)),
        'last_added_pos': positions_db.last_added(),
        'last_updated_pos': positions_db.last_updated(),
        'last_added_cand': candidates_db.last_added(),
        'last_updated_cand': candidates_db.last_updated(),
        'most_applied_pos': positions_db.with_most_candidates(),
        'cand_highest_cv_score': candidates_db.with_highest_cv_score(),
        'cand_highest_motivation_lvl': candidates_db.with_highest_motivation_lvl()
    }

def update_avatar(id, avatar):
    filename = f"{id}/{datetime.now().strftime('%Y%m%d%H%M%S')}{os.path.splitext(avatar.filename)[1]}"
    if avatar.content_type.startswith('image/') and len(avatar.read()) < 2 * 1024 * 1024:
        if not os.path.exists(f"static/images/{id}"):
            os.makedirs(f"static/images/{id}")
        avatar.seek(0)
        avatar.save(f"static/images/{filename}")
        user = users_db.get(id)
        try:
            users_db.update_avatar(filename, id)
        except DatabaseError as error:
            logger.error(f"{type(error)}\n{error}")
            return {'success': False, 'error': {'error': True}}
        if user['avatar'] != DEFAULT_AVATAR:
            if os.path.exists(f"static/images/{user['avatar']}"):
                try:
                    os.remove(f"static/images/{user['avatar']}")
                except OSError as error:
                    logger.error(f"{type(error)}\n{error}")
        return {'success': True, 'avatar': filename}
    else:
        return {'success': False, 'error': {'invalid': True}}

def update_signature(id, signature):
    try:
        users_db.update_signature(signature, id)
        return {'success': True}
    except DatabaseError as error:
        logger.error(f"{type(error)}\n{error}")
        return {'success': False, 'error': {'error': True}}

def update_company(id, company):
    try:
        users_db.update_company(company, id)
        return {'success': True}
    except DatabaseError as error:
        logger.error(f"{type(error)}\n{error}")
        return {'success': False, 'error': {'error': True}}

def get_signature_company(id):
    user = users_db.get(id)
    return user['signature'], user['company']
