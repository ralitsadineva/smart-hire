from models.candidate_repo import CandidateRepository
from models.cv_repo import CVRepository
from models.ml_repo import MLRepository
from exceptions import DatabaseError
from read_pdf import read_pdf, page_count
from openai_eval import extract_cv, evaluate_cv, evaluate_ml
from utils import check_empty, convert_to_dict, convert_to_dict_extracted
import logging
import os

logger = logging.getLogger(__name__)

candidates_db = CandidateRepository()
cvs_db = CVRepository()
mls_db = MLRepository()

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
    return {'candidate': candidate, 'cv': cv, 'ml': ml}

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
        if candidates_db.get(cand_id)[2] != cand_info['First name'] or candidates_db.get(cand_id)[3] != cand_info['Last name']:
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
        filename = f"{candidates_db.get(cand_id)[3]}-cv.pdf"
        if not os.path.exists(f"uploads/{candidates_db.get(cand_id)[1]}/{cand_id}"):
            os.makedirs(f"uploads/{candidates_db.get(cand_id)[1]}/{cand_id}")
        cv.seek(0)
        cv.save(f"uploads/{candidates_db.get(cand_id)[1]}/{cand_id}/{filename}")
        candidate = candidates_db.get(cand_id)
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

def delete_ml(pos_id, cand_id):
    if os.path.exists(f"uploads/{pos_id}/{cand_id}/{candidates_db.get(cand_id)[3]}-letter.pdf"):
        try:
            os.remove(f"uploads/{pos_id}/{cand_id}/{candidates_db.get(cand_id)[3]}-letter.pdf")
        except OSError as error:
            logger.error(f"{type(error)}\n{error}")
    mls_db.delete(cand_id)
