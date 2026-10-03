import sys
import os

# =====================================================
# PROJECT ROOT
# =====================================================

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


# =====================================================
# DATABASE
# =====================================================

from app.database.db import get_connection


# =====================================================
# CHECK DATABASE
# =====================================================

def check_attendance():
    connection = get_connection()

    if connection is None:
        print("\nDatabase connection failed.")
        return

    try:
        cursor = connection.cursor()

        # -------------------------------------------------
        # STUDENTS
        # -------------------------------------------------

        cursor.execute("""
            SELECT
                student_id,
                name,
                created_at
            FROM students
            ORDER BY student_id;
        """)

        students = cursor.fetchall()

        print("\n" + "=" * 70)
        print("REGISTERED STUDENTS")
        print("=" * 70)

        if not students:
            print("No students registered.")

        else:
            for student in students:
                print(
                    f"ID: {student[0]} | "
                    f"Name: {student[1]} | "
                    f"Registered: {student[2]}"
                )

        # -------------------------------------------------
        # ATTENDANCE
        # -------------------------------------------------

        cursor.execute("""
            SELECT
                student_id,
                attendance_date,
                attendance_time,
                status
            FROM attendance
            ORDER BY attendance_date DESC,
                     attendance_time DESC;
        """)

        attendance = cursor.fetchall()

        print("\n" + "=" * 70)
        print("ATTENDANCE RECORDS")
        print("=" * 70)

        if not attendance:
            print("No attendance records found.")

        else:
            for record in attendance:
                print(
                    f"Student ID: {record[0]} | "
                    f"Date: {record[1]} | "
                    f"Time: {record[2]} | "
                    f"Status: {record[3]}"
                )

        # -------------------------------------------------
        # ATTENDANCE SESSIONS
        # -------------------------------------------------

        cursor.execute("""
            SELECT
                id,
                session_date,
                start_time,
                end_time,
                status
            FROM attendance_sessions
            ORDER BY id DESC;
        """)

        sessions = cursor.fetchall()

        print("\n" + "=" * 70)
        print("ATTENDANCE SESSIONS")
        print("=" * 70)

        if not sessions:
            print("No attendance sessions found.")

        else:
            for session in sessions:
                print(
                    f"Session ID: {session[0]} | "
                    f"Date: {session[1]} | "
                    f"Start: {session[2]} | "
                    f"End: {session[3]} | "
                    f"Status: {session[4]}"
                )

        print("\n" + "=" * 70)
        print("DATABASE CHECK COMPLETED")
        print("=" * 70)

    except Exception as e:
        print("\nError while checking attendance:")
        print(e)

    finally:
        connection.close()
        print("\nDatabase connection closed.")


# =====================================================
# MAIN
# =====================================================

if __name__ == "__main__":
    check_attendance()