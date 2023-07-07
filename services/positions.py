from models.position_repo import PositionRepository
from models.candidate_repo import CandidateRepository
from exceptions import DatabaseError
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(name)s] %(levelname)s: %(message)s',
    # datefmt='%Y-%m-%d %H:%M:%S',
)
logger = logging.getLogger(__name__)

positions_db = PositionRepository()
candidates_db = CandidateRepository()

def get_all():
    return positions_db.get_all_active()

def add(id, title, description):
    try:
        positions_db.insert(id, title, description)
        return {'success': True}
    except DatabaseError as error:
        logger.error(f"{type(error)}\n{error}")
        return {'success': False, 'error': {'error': True}}

def duplicate(id):
    return positions_db.get(id)[2:4]

def history():
    return positions_db.get_all_inactive()

def get(id):
    position = positions_db.get(id)
    candidates = candidates_db.get_all_for_pos(id)
    return {'position': position, 'candidates': candidates}

def edit(id, title, description):
    try:
        positions_db.update(id, title, description)
        return {'success': True}
    except DatabaseError as error:
        logger.error(f"{type(error)}\n{error}")
        position = positions_db.get(id)
        return {'success': False, 'error': {'error': True}, 'position': position}

def archive(id):
    return positions_db.make_inactive(id)

def activate(id):
    return positions_db.make_active(id)
