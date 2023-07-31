import psycopg2
from models.abstract_repo import AbstractRepository
from exceptions import DatabaseError

class CandidateRepository(AbstractRepository):
    table_name = 'candidates'
    pk_name = 'cand_id'
    insert_columns = '(pos_id, first_name, last_name, email)'
    insert_values = '(%s, %s, %s, %s)'

    @AbstractRepository.connection_wrapper
    def get_all_for_pos(self, pos_id, sort_column, **kwargs):
        cursor = kwargs.get('cursor')
        cursor.execute(f"""
            SELECT candidates.*, cvs.score AS cv_score, cvs.structure, cvs.contact_info, cvs.work_experience, cvs.education, cvs.skills, cvs.languages, mls.motivation_lvl, interviews.score, interviews.date
            FROM candidates
            LEFT JOIN cvs ON candidates.cand_id = cvs.cand_id
            LEFT JOIN mls ON candidates.cand_id = mls.cand_id
            LEFT JOIN interviews ON candidates.cand_id = interviews.cand_id
            WHERE candidates.pos_id = %s AND candidates.deleted = FALSE
            ORDER BY {sort_column} {'ASC' if sort_column == 'candidates.first_name' else 'DESC'} NULLS LAST;
            """, (pos_id, ))
        return cursor.fetchall()
    
    @AbstractRepository.connection_wrapper
    def get_stats(self, pos_id, **kwargs):
        cursor = kwargs.get('cursor')
        cursor.execute("""
            SELECT
                COUNT(cand_id) FILTER (WHERE NOT deleted) AS candidates_count,
                COUNT(cand_id) FILTER (WHERE NOT deleted AND invited) AS invited_count,
                COUNT(cand_id) FILTER (WHERE NOT deleted AND offer) AS offer_count,
                COUNT(cand_id) FILTER (WHERE NOT deleted AND reject_reason IS NOT NULL) AS rejected_count,
                COUNT(cand_id) FILTER (WHERE NOT deleted AND reject_reason = '1') AS rr1_count,
                COUNT(cand_id) FILTER (WHERE NOT deleted AND reject_reason = '2') AS rr2_count,
                COUNT(cand_id) FILTER (WHERE NOT deleted AND reject_reason = '3') AS rr3_count,
                COUNT(cand_id) FILTER (WHERE NOT deleted AND reject_reason = '4') AS rr4_count,
                COUNT(cand_id) FILTER (WHERE NOT deleted AND reject_reason = '5') AS rr5_count,
                COUNT(cand_id) FILTER (WHERE NOT deleted AND reject_reason = '6') AS rr6_count,
                COUNT(cand_id) FILTER (WHERE NOT deleted AND reject_reason = '7') AS rr7_count,
                COUNT(cand_id) FILTER (WHERE NOT deleted AND decline_reason IS NOT NULL) AS declined_count,
                COUNT(cand_id) FILTER (WHERE NOT deleted AND decline_reason = '1') AS dr1_count,
                COUNT(cand_id) FILTER (WHERE NOT deleted AND decline_reason = '2') AS dr2_count,
                COUNT(cand_id) FILTER (WHERE NOT deleted AND decline_reason = '3') AS dr3_count,
                COUNT(cand_id) FILTER (WHERE NOT deleted AND decline_reason = '4') AS dr4_count,
                COUNT(cand_id) FILTER (WHERE NOT deleted AND decline_reason = '5') AS dr5_count,
                COUNT(cand_id) FILTER (WHERE NOT deleted AND decline_reason = '6') AS dr6_count,
                COUNT(cand_id) FILTER (WHERE NOT deleted AND decline_reason = '7') AS dr7_count
            FROM candidates
            WHERE pos_id = %s;
            """, (pos_id, ))
        return cursor.fetchone()

    @AbstractRepository.connection_wrapper
    def get_all(self, **kwargs):
        cursor = kwargs.get('cursor')
        cursor.execute("SELECT * FROM candidates WHERE deleted = FALSE;")
        return cursor.fetchall()

    @AbstractRepository.connection_wrapper
    def update(self, cand_id, email, phone_number, address, postal_code, city, country, date_of_birth, **kwargs):
        cursor = kwargs.get('cursor')
        conn = kwargs.get('conn')
        try:
            cursor.execute("""
                UPDATE candidates
                SET email = %s, phone_number = %s, address = %s, postal_code = %s, city = %s, country = %s, date_of_birth = %s, last_updated = CURRENT_TIMESTAMP
                WHERE cand_id = %s;
                """, (email, phone_number, address, postal_code, city, country, date_of_birth, cand_id))
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            conn.rollback()
            raise DatabaseError(error)

    @AbstractRepository.connection_wrapper
    def last_added(self, **kwargs):
        cursor = kwargs.get('cursor')
        cursor.execute("""
            SELECT candidates.*, positions.title, cvs.score, mls.motivation_lvl
            FROM candidates
            LEFT JOIN positions ON candidates.pos_id = positions.pos_id
            LEFT JOIN cvs ON candidates.cand_id = cvs.cand_id
            LEFT JOIN mls ON candidates.cand_id = mls.cand_id
            WHERE positions.active = TRUE AND candidates.deleted = FALSE
            ORDER BY candidates.created DESC
            LIMIT 5;
            """)
        return cursor.fetchall()

    @AbstractRepository.connection_wrapper
    def last_updated(self, **kwargs):
        cursor = kwargs.get('cursor')
        cursor.execute("""
            SELECT candidates.*, positions.title, cvs.score, mls.motivation_lvl
            FROM candidates
            LEFT JOIN positions ON candidates.pos_id = positions.pos_id
            LEFT JOIN cvs ON candidates.cand_id = cvs.cand_id
            LEFT JOIN mls ON candidates.cand_id = mls.cand_id
            WHERE positions.active = TRUE AND candidates.deleted = FALSE
            ORDER BY candidates.last_updated DESC
            LIMIT 5;
            """)
        return cursor.fetchall()

    @AbstractRepository.connection_wrapper
    def with_highest_cv_score(self, **kwargs):
        cursor = kwargs.get('cursor')
        cursor.execute("""
            SELECT candidates.*, positions.title, cvs.score, mls.motivation_lvl
            FROM candidates
            LEFT JOIN positions ON candidates.pos_id = positions.pos_id
            JOIN cvs ON candidates.cand_id = cvs.cand_id
            LEFT JOIN mls ON candidates.cand_id = mls.cand_id
            WHERE positions.active = TRUE AND candidates.deleted = FALSE
            ORDER BY cvs.score DESC
            LIMIT 5;
            """)
        return cursor.fetchall()

    @AbstractRepository.connection_wrapper
    def with_highest_motivation_lvl(self, **kwargs):
        cursor = kwargs.get('cursor')
        cursor.execute("""
            SELECT candidates.*, positions.title, cvs.score, mls.motivation_lvl
            FROM candidates
            LEFT JOIN positions ON candidates.pos_id = positions.pos_id
            LEFT JOIN cvs ON candidates.cand_id = cvs.cand_id
            JOIN mls ON candidates.cand_id = mls.cand_id
            WHERE positions.active = TRUE AND candidates.deleted = FALSE
            ORDER BY mls.motivation_lvl DESC
            LIMIT 5;
            """)
        return cursor.fetchall()
    
    @AbstractRepository.connection_wrapper
    def mark_invited(self, cand_id, **kwargs):
        cursor = kwargs.get('cursor')
        conn = kwargs.get('conn')
        try:
            cursor.execute("""
                UPDATE candidates
                SET invited = TRUE, last_updated = CURRENT_TIMESTAMP
                WHERE cand_id = %s;
                """, (cand_id, ))
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            conn.rollback()
            raise DatabaseError(error)
    
    @AbstractRepository.connection_wrapper
    def unmark_invited(self, cand_id, **kwargs):
        cursor = kwargs.get('cursor')
        conn = kwargs.get('conn')
        try:
            cursor.execute("""
                UPDATE candidates
                SET invited = FALSE, last_updated = CURRENT_TIMESTAMP
                WHERE cand_id = %s;
                """, (cand_id, ))
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            conn.rollback()
            raise DatabaseError(error)

    @AbstractRepository.connection_wrapper
    def mark_offer(self, cand_id, **kwargs):
        cursor = kwargs.get('cursor')
        conn = kwargs.get('conn')
        try:
            cursor.execute("""
                UPDATE candidates
                SET offer = TRUE, last_updated = CURRENT_TIMESTAMP
                WHERE cand_id = %s;
                """, (cand_id, ))
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            conn.rollback()
            raise DatabaseError(error)
    
    @AbstractRepository.connection_wrapper
    def unmark_offer(self, cand_id, **kwargs):
        cursor = kwargs.get('cursor')
        conn = kwargs.get('conn')
        try:
            cursor.execute("""
                UPDATE candidates
                SET offer = FALSE, last_updated = CURRENT_TIMESTAMP
                WHERE cand_id = %s;
                """, (cand_id, ))
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            conn.rollback()
            raise DatabaseError(error)
        
    @AbstractRepository.connection_wrapper
    def mark_hired(self, cand_id, **kwargs):
        cursor = kwargs.get('cursor')
        conn = kwargs.get('conn')
        try:
            cursor.execute("""
                UPDATE candidates
                SET hired = TRUE, last_updated = CURRENT_TIMESTAMP
                WHERE cand_id = %s;
                """, (cand_id, ))
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            conn.rollback()
            raise DatabaseError(error)
    
    @AbstractRepository.connection_wrapper
    def unmark_hired(self, cand_id, **kwargs):
        cursor = kwargs.get('cursor')
        conn = kwargs.get('conn')
        try:
            cursor.execute("""
                UPDATE candidates
                SET hired = FALSE, last_updated = CURRENT_TIMESTAMP
                WHERE cand_id = %s;
                """, (cand_id, ))
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            conn.rollback()
            raise DatabaseError(error)
    
    @AbstractRepository.connection_wrapper
    def update_reject_reason(self, cand_id, reason, **kwargs):
        cursor = kwargs.get('cursor')
        conn = kwargs.get('conn')
        try:
            cursor.execute("""
                UPDATE candidates
                SET reject_reason = %s, last_updated = CURRENT_TIMESTAMP
                WHERE cand_id = %s;
                """, (reason, cand_id))
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            conn.rollback()
            raise DatabaseError(error)
    
    @AbstractRepository.connection_wrapper
    def update_decline_reason(self, cand_id, reason, **kwargs):
        cursor = kwargs.get('cursor')
        conn = kwargs.get('conn')
        try:
            cursor.execute("""
                UPDATE candidates
                SET decline_reason = %s, last_updated = CURRENT_TIMESTAMP
                WHERE cand_id = %s;
                """, (reason, cand_id))
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            conn.rollback()
            raise DatabaseError(error)
    
    @AbstractRepository.connection_wrapper
    def delete(self, cand_id, **kwargs):
        cursor = kwargs.get('cursor')
        conn = kwargs.get('conn')
        try:
            cursor.execute("""
                UPDATE candidates
                SET deleted = TRUE, last_updated = CURRENT_TIMESTAMP
                WHERE cand_id = %s;
                """, (cand_id, ))
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            conn.rollback()
            raise DatabaseError(error)
    
    @AbstractRepository.connection_wrapper
    def search_by_email(self, email, **kwargs):
        cursor = kwargs.get('cursor')
        cursor.execute("""
            SELECT * FROM candidates
            WHERE email = %s AND deleted = FALSE;
            """, (email, ))
        return cursor.fetchall()
    
    @AbstractRepository.connection_wrapper
    def search_by_name(self, name, **kwargs):
        cursor = kwargs.get('cursor')
        cursor.execute("""
            SELECT * FROM candidates
            WHERE (first_name ILIKE %s OR last_name ILIKE %s) AND deleted = FALSE;
            """, (name, name))
        return cursor.fetchall()
