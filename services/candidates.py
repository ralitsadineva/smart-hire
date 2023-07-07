from models.candidate_repo import CandidateRepository
from models.cv_repo import CVRepository
from models.ml_repo import MLRepository
from exceptions import DatabaseError
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(name)s] %(levelname)s: %(message)s',
    # datefmt='%Y-%m-%d %H:%M:%S',
)
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
