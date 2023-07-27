from models.position_repo import PositionRepository
from models.candidate_repo import CandidateRepository
from exceptions import DatabaseError
import logging

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
    return [positions_db.get(id)['title'], positions_db.get(id)['description']]

def history():
    return positions_db.get_all_inactive()

def get_with_cand(id, sort_column):
    if sort_column not in ['candidates.first_name', 'cvs.score', 'cvs.structure', 'cvs.contact_info', 'cvs.work_experience', 'cvs.education', 'cvs.skills', 'cvs.languages', 'mls.motivation_lvl']:
        sort_column = 'candidates.first_name'
    position = positions_db.get(id)
    candidates = candidates_db.get_all_for_pos(id, sort_column)
    return {'position': position, 'candidates': candidates}

def get(id):
    return positions_db.get(id)

def edit(id, title, description):
    try:
        positions_db.update(id, title, description)
        return {'success': True}
    except DatabaseError as error:
        logger.error(f"{type(error)}\n{error}")
        position = positions_db.get(id)
        return {'success': False, 'error': {'error': True}, 'position': position}

def archive(id):
    positions_db.make_inactive(id)

def activate(id):
    positions_db.make_active(id)
