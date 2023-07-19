from models.abstract_repo import AbstractRepository

class TableRepository(AbstractRepository):
    @AbstractRepository.connection_wrapper
    def create_tables(self, **kwargs):
        cursor = kwargs.get('cursor')
        conn = kwargs.get('conn')
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id UUID NOT NULL PRIMARY KEY DEFAULT gen_random_uuid(), 
                email VARCHAR(255) NOT NULL UNIQUE, 
                username VARCHAR(255) NOT NULL UNIQUE, 
                password BYTEA NOT NULL,
                avatar VARCHAR(255) DEFAULT 'user.png',
                type CHAR NOT NULL DEFAULT '0' CHECK (type IN ('0', '1')),
                created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                last_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            """)  # type 0 = default, 1 = Google
        conn.commit()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS positions (
                pos_id UUID NOT NULL PRIMARY KEY DEFAULT gen_random_uuid(), 
                user_id UUID NOT NULL REFERENCES users (id), 
                title VARCHAR(255) NOT NULL, 
                description VARCHAR NOT NULL, 
                active BOOLEAN NOT NULL DEFAULT TRUE, 
                created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                last_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            """)
        conn.commit()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS candidates (
                cand_id UUID NOT NULL PRIMARY KEY DEFAULT gen_random_uuid(), 
                pos_id UUID NOT NULL REFERENCES positions (pos_id), 
                first_name VARCHAR(255) NOT NULL, 
                last_name VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL, 
                phone_number VARCHAR(255), 
                address VARCHAR(255),
                postal_code VARCHAR(255),
                city VARCHAR(255),
                country VARCHAR(255),
                date_of_birth DATE,
                created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                last_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            """)
        conn.commit()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cvs (
                cv_id UUID NOT NULL PRIMARY KEY DEFAULT gen_random_uuid(),
                cand_id UUID NOT NULL REFERENCES candidates (cand_id),
                score INTEGER CHECK (score >= 0 AND score <= 100),
                structure INTEGER CHECK (structure > 0 AND structure <= 5),
                contact_info INTEGER CHECK (contact_info > 0 AND contact_info <= 5),
                work_experience INTEGER CHECK (work_experience > 0 AND work_experience <= 10),
                education INTEGER CHECK (education > 0 AND education <= 10),
                skills INTEGER CHECK (skills > 0 AND skills <= 10),
                languages INTEGER CHECK (languages > 0 AND languages <= 10),
                length INTEGER,
                created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                last_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            """)
        conn.commit()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mls (
                ml_id UUID NOT NULL PRIMARY KEY DEFAULT gen_random_uuid(),
                cand_id UUID NOT NULL REFERENCES candidates (cand_id),
                motivation_lvl INTEGER CHECK (motivation_lvl > 0 AND motivation_lvl <= 10),
                sentiment VARCHAR(255) CHECK (sentiment IN ('Positive', 'Negative', 'Neutral')),
                tone VARCHAR(255),
                length INTEGER,
                grammar VARCHAR(255),
                created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                last_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            """)
        conn.commit()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pros_cons (
                id UUID NOT NULL PRIMARY KEY DEFAULT gen_random_uuid(),
                cand_id UUID NOT NULL REFERENCES candidates (cand_id),
                pros VARCHAR,
                cons VARCHAR,
                created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                last_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            """)
        conn.commit()

TableRepository().create_tables()
