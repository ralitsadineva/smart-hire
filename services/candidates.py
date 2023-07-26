from models.candidate_repo import CandidateRepository
from models.cv_repo import CVRepository
from models.ml_repo import MLRepository
from models.pros_cons_repo import ProsConsRepository
from models.interview_repo import InterviewRepository
from models.position_repo import PositionRepository
from models.user_repo import UserRepository
from exceptions import DatabaseError
from read_pdf import read_pdf, page_count
from openai_eval import extract_cv, evaluate_cv, evaluate_ml, pros_cons, response_positive, response_negative
from utils import check_empty, convert_to_dict, convert_to_dict_extracted, convert_pros_cons
from constants import RESPONSE_EMAIL_SUBJECT, RESPONSE_EMAIL_SUBJECT_WITH_COMPANY
import logging
import os

logger = logging.getLogger(__name__)

candidates_db = CandidateRepository()
cvs_db = CVRepository()
mls_db = MLRepository()
pros_cons_db = ProsConsRepository()
interviews_db = InterviewRepository()
positions_db = PositionRepository()
users_db = UserRepository()

def add(id, first_name, last_name, email):
    try:
        candidates_db.insert(id, first_name, last_name, email)
        return {'success': True}
    except DatabaseError as error:
        logger.error(f"{type(error)}\n{error}")
        return {'success': False, 'error': {'error': True}}

def get(id):
    candidate = candidates_db.get(id)
    cv = cvs_db.get(id)
    ml = mls_db.get(id)
    plus_minus = pros_cons_db.get(id)
    if plus_minus is not None:
        pros, cons = plus_minus[2:4]
    else:
        pros, cons = None, None
    interview = interviews_db.get(id)
    return {'candidate': candidate, 'cv': cv, 'ml': ml, 'pros': pros, 'cons': cons, 'interview': interview}

def get_all():
    return candidates_db.get_all()

def update(cand_id, email, phone, address, postal_code, city, country, birthdate):
    if email == '':
        email = candidates_db.get(cand_id)[4]
    phone = check_empty(phone)
    address = check_empty(address)
    postal_code = check_empty(postal_code)
    city = check_empty(city)
    country = check_empty(country)
    birthdate = check_empty(birthdate)
    try:
        candidates_db.update(cand_id, email, phone, address, postal_code, city, country, birthdate)
        return {'success': True, 'pos_id': candidates_db.get(cand_id)[1]}
    except DatabaseError as error:
        logger.error(f"{type(error)}\n{error}")
        if os.path.exists(f"uploads/{candidates_db.get(cand_id)[1]}/{cand_id}/{candidates_db.get(cand_id)[3]}-letter.pdf"):
            try:
                os.remove(f"uploads/{candidates_db.get(cand_id)[1]}/{cand_id}/{candidates_db.get(cand_id)[3]}-letter.pdf")
            except OSError as error:
                logger.error(f"{type(error)}\n{error}")
        cvs_db.delete(cand_id)
        pros_cons_db.delete(cand_id)
        return {'success': False, 'error': {'error': True}}

def add_cv(cand_id, cv):
    if cvs_db.get(cand_id) is not None:
        return {'success': False, 'error': {'exist': True}}
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
            return {'success': False, 'error': {'error': True}}
        candidate = candidates_db.get(cand_id)
        if candidate[2] != cand_info['First name'] or candidate[3] != cand_info['Last name']:
            different_names = True
        else:
            different_names = False
        response = evaluate_cv(contents)
        logger.info(response)
        try:
            response_dict = convert_to_dict(response)
        except Exception as error:
            logger.error(f"{type(error)}\n{error}")
            return {'success': False, 'error': {'error': True}}
        score = sum(response_dict.values())
        try:
            cvs_db.insert(cand_id, score, response_dict['Structure and organization'], response_dict['Contact information'], response_dict['Work experience'], response_dict['Education'], response_dict['Skills'], response_dict['Languages'], length)
        except (DatabaseError, Exception) as error:
            logger.error(f"{type(error)}\n{error}")
            return {'success': False, 'error': {'error': True}}
        position = positions_db.get(candidate[1])
        plus_minus = pros_cons(contents, position)
        logger.info(plus_minus)
        pros, cons = convert_pros_cons(plus_minus)
        logger.info(f'Pros:\n{pros}\nCons:\n{cons}')
        try:
            pros_cons_db.insert(cand_id, pros, cons)
        except (DatabaseError, Exception) as error:
            logger.error(f"{type(error)}\n{error}")
            cvs_db.delete(cand_id)
            return {'success': False, 'error': {'error': True}}
        filename = f"{candidate[3]}-cv.pdf"
        if not os.path.exists(f"uploads/{candidate[1]}/{cand_id}"):
            os.makedirs(f"uploads/{candidate[1]}/{cand_id}")
        cv.seek(0)
        cv.save(f"uploads/{candidate[1]}/{cand_id}/{filename}")
        return {'success': True, 'arguments': {'cand_info': cand_info, 'candidate': candidate, 'different_names': different_names}}
    else:
        return {'success': False, 'error': {'invalid': True}}

def add_ml(cand_id, ml):
    if mls_db.get(cand_id) is not None:
        return {'success': False, 'error': {'exist': True}}
    if ml.content_type == 'application/pdf' and len(ml.read()) < 2 * 1024 * 1024:
        ml.seek(0)
        contents = read_pdf(ml)
        word_count = len(contents.split())
        response = evaluate_ml(contents)
        logger.info(response)
        try:
            response_dict = convert_to_dict(response)
        except:
            logger.error(f"{type(error)}\n{error}")
            return {'success': False, 'error': {'error': True}}
        logger.info(response_dict)
        try:
            mls_db.insert(cand_id, response_dict['Motivation level'], response_dict['Overall sentiment'], response_dict['Tone'], word_count, response_dict['Grammar and language usage'])
        except DatabaseError as error:
            logger.error(f"{type(error)}\n{error}")
            return {'success': False, 'error': {'error': True}}
        filename = f"{candidates_db.get(cand_id)[3]}-letter.pdf"
        if not os.path.exists(f"uploads/{candidates_db.get(cand_id)[1]}/{cand_id}"):
            os.makedirs(f"uploads/{candidates_db.get(cand_id)[1]}/{cand_id}")
        ml.seek(0)
        ml.save(f"uploads/{candidates_db.get(cand_id)[1]}/{cand_id}/{filename}")
        return {'success': True, 'pos_id': candidates_db.get(cand_id)[1]}
    else:
        return {'success': False, 'error': {'invalid': True}}

def view_cv(pos_id, cand_id):
    if os.path.exists(f"uploads/{pos_id}/{cand_id}/{candidates_db.get(cand_id)[3]}-cv.pdf"):
        return {'success': True, 'filename': f"{candidates_db.get(cand_id)[3]}-cv.pdf"}
    else:
        return {'success': False}

def view_ml(pos_id, cand_id):
    if os.path.exists(f"uploads/{pos_id}/{cand_id}/{candidates_db.get(cand_id)[3]}-letter.pdf"):
        return {'success': True, 'filename': f"{candidates_db.get(cand_id)[3]}-letter.pdf"}
    else:
        return {'success': False}

def delete_cv(pos_id, cand_id):
    if os.path.exists(f"uploads/{pos_id}/{cand_id}/{candidates_db.get(cand_id)[3]}-cv.pdf"):
        try:
            os.remove(f"uploads/{pos_id}/{cand_id}/{candidates_db.get(cand_id)[3]}-cv.pdf")
        except OSError as error:
            logger.error(f"{type(error)}\n{error}")
    cvs_db.delete(cand_id)
    pros_cons_db.delete(cand_id)

def delete_ml(pos_id, cand_id):
    if os.path.exists(f"uploads/{pos_id}/{cand_id}/{candidates_db.get(cand_id)[3]}-letter.pdf"):
        try:
            os.remove(f"uploads/{pos_id}/{cand_id}/{candidates_db.get(cand_id)[3]}-letter.pdf")
        except OSError as error:
            logger.error(f"{type(error)}\n{error}")
    mls_db.delete(cand_id)

def interview_invitation(pos_id, cand_id, user_id):
    candidate = candidates_db.get(cand_id)
    position = positions_db.get(pos_id)
    signature, company = users_db.get(user_id)[8:10]
    response = response_positive(candidate, position, signature, company)
    logger.info(response)
    if company:
        subject = RESPONSE_EMAIL_SUBJECT_WITH_COMPANY.format(company)
    else:
        subject = RESPONSE_EMAIL_SUBJECT
    return {'candidate': candidate, 'response': response, 'subject': subject}

def rejection_email(pos_id, cand_id, user_id):
    candidate = candidates_db.get(cand_id)
    position = positions_db.get(pos_id)
    cons = pros_cons_db.get(cand_id) is not None
    signature, company = users_db.get(user_id)[8:10]
    response = response_negative(candidate, position, None, signature, company)
    logger.info(response)
    if company:
        subject = RESPONSE_EMAIL_SUBJECT_WITH_COMPANY.format(company)
    else:
        subject = RESPONSE_EMAIL_SUBJECT
    return {'candidate': candidate, 'response': response, 'subject': subject, 'cons': cons}

def rejection_email_with_reasons(pos_id, cand_id, user_id):
    candidate = candidates_db.get(cand_id)
    position = positions_db.get(pos_id)
    if pros_cons_db.get(cand_id) is not None:
        cons = pros_cons_db.get(cand_id)[3]
    else:
        cons = None
    signature, company = users_db.get(user_id)[8:10]
    response = response_negative(candidate, position, cons, signature, company)
    logger.info(response)
    if company:
        subject = RESPONSE_EMAIL_SUBJECT_WITH_COMPANY.format(company)
    else:
        subject = RESPONSE_EMAIL_SUBJECT
    return {'candidate': candidate, 'response': response, 'subject': subject, 'cons': True, 'reasons': True}

def add_interview(cand_id, pos_id, score, notes, date):
    if interviews_db.get(cand_id) is not None:
        return {'success': False, 'error': {'exist': True}}
    try:
        interviews_db.insert(cand_id, pos_id, score, notes, date)
        return {'success': True}
    except DatabaseError as error:
        logger.error(f"{type(error)}\n{error}")
        return {'success': False, 'error': {'error': True}}

def edit_interview(cand_id, score, notes, date):
    try:
        id = interviews_db.get(cand_id)[0]
        interviews_db.update_score(int(score), id)
        interviews_db.update_notes(notes, id)
        interviews_db.update_date(date, id)
        return {'success': True}
    except DatabaseError as error:
        logger.error(f"{type(error)}\n{error}")
        return {'success': False, 'error': {'error': True}}
