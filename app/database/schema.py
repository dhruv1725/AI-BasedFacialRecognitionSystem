from app.database.db import get_connection


# ============================================================
# CREATE DATABASE TABLES
# ============================================================

def create_tables():

    connection = get_connection()

    if connection is None:
        print("Could not connect to database.")
        return False

    cursor = None

    try:
        cursor = connection.cursor()

        # ====================================================
        # STUDENTS
        # ====================================================

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id SERIAL PRIMARY KEY,
                student_id VARCHAR(50) UNIQUE NOT NULL,
                name VARCHAR(100) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # ====================================================
        # ATTENDANCE
        # ====================================================

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                id SERIAL PRIMARY KEY,
                student_id VARCHAR(50) NOT NULL,
                attendance_date DATE NOT NULL,
                attendance_time TIME NOT NULL,
                status VARCHAR(20) DEFAULT 'Present',
                UNIQUE(student_id, attendance_date)
            );
        """)

        # ====================================================
        # ATTENDANCE SESSIONS
        # ====================================================

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS attendance_sessions (
                id SERIAL PRIMARY KEY,
                session_date DATE NOT NULL,
                start_time TIME NOT NULL,
                end_time TIME,
                status VARCHAR(20) DEFAULT 'Active',
                CHECK (status IN ('Active', 'Completed'))
            );
        """)

        # ====================================================
        # ATTENDANCE SETTINGS
        #
        # id = 1 is treated as the single settings row.
        # ====================================================

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS attendance_settings (
                id INTEGER PRIMARY KEY,
                attendance_start_date DATE NOT NULL
            );
        """)

        # Create default settings row if it does not exist.
        cursor.execute("""
            INSERT INTO attendance_settings
                (id, attendance_start_date)
            VALUES
                (1, CURRENT_DATE)
            ON CONFLICT (id) DO NOTHING;
        """)

        connection.commit()

        print("Database tables are ready.")
        return True

    except Exception as e:

        connection.rollback()

        print("Database schema error:")
        print(e)

        return False

    finally:

        if cursor:
            cursor.close()

        connection.close()


if __name__ == "__main__":
    create_tables()