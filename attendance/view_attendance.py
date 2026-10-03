import os
import sys
from datetime import date

# ==========================================
# PROJECT ROOT
# ==========================================

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

sys.path.insert(0, PROJECT_ROOT)

from app.database.db import get_connection


# ==========================================
# VIEW TODAY'S ATTENDANCE
# ==========================================

def view_today_attendance():

    connection = None
    cursor = None

    try:

        connection = get_connection()
        cursor = connection.cursor()

        today = date.today()

        cursor.execute(
            """
            SELECT
                a.student_id,
                s.name,
                a.attendance_date,
                a.attendance_time,
                a.status
            FROM public.attendance AS a
            JOIN public.students AS s
                ON a.student_id = s.student_id
            WHERE a.attendance_date = %s
            ORDER BY a.attendance_time ASC
            """,
            (today,)
        )

        records = cursor.fetchall()

        print("\n==============================================")
        print("             TODAY'S ATTENDANCE")
        print("==============================================")
        print(f"Date: {today}")
        print("==============================================")

        if not records:

            print("No attendance recorded today.")

        else:

            print(
                f"{'ID':<10}"
                f"{'NAME':<25}"
                f"{'TIME':<15}"
                f"{'STATUS':<10}"
            )

            print("----------------------------------------------")

            for record in records:

                student_id = record[0]
                name = record[1]
                attendance_time = record[3]
                status = record[4]

                print(
                    f"{student_id:<10}"
                    f"{name:<25}"
                    f"{str(attendance_time):<15}"
                    f"{status:<10}"
                )

            print("----------------------------------------------")
            print(f"Total Present: {len(records)}")

        print("==============================================\n")

    except Exception as e:

        print("Database error:")
        print(e)

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ==========================================
# VIEW ALL ATTENDANCE
# ==========================================

def view_all_attendance():

    connection = None
    cursor = None

    try:

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                a.student_id,
                s.name,
                a.attendance_date,
                a.attendance_time,
                a.status
            FROM public.attendance AS a
            JOIN public.students AS s
                ON a.student_id = s.student_id
            ORDER BY
                a.attendance_date DESC,
                a.attendance_time DESC
            """
        )

        records = cursor.fetchall()

        print("\n==============================================================")
        print("                    ALL ATTENDANCE")
        print("==============================================================")

        if not records:

            print("No attendance records found.")

        else:

            print(
                f"{'ID':<10}"
                f"{'NAME':<25}"
                f"{'DATE':<15}"
                f"{'TIME':<15}"
                f"{'STATUS':<10}"
            )

            print("--------------------------------------------------------------")

            for record in records:

                student_id = record[0]
                name = record[1]
                attendance_date = record[2]
                attendance_time = record[3]
                status = record[4]

                print(
                    f"{student_id:<10}"
                    f"{name:<25}"
                    f"{str(attendance_date):<15}"
                    f"{str(attendance_time):<15}"
                    f"{status:<10}"
                )

        print("==============================================================\n")

    except Exception as e:

        print("Database error:")
        print(e)

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ==========================================
# VIEW STUDENT ATTENDANCE
# ==========================================

def view_student_attendance():

    student_id = input("\nEnter Student ID: ").strip()

    if not student_id:

        print("Student ID cannot be empty.")
        return

    connection = None
    cursor = None

    try:

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                s.name,
                a.attendance_date,
                a.attendance_time,
                a.status
            FROM public.attendance AS a
            JOIN public.students AS s
                ON a.student_id = s.student_id
            WHERE a.student_id = %s
            ORDER BY
                a.attendance_date DESC,
                a.attendance_time DESC
            """,
            (student_id,)
        )

        records = cursor.fetchall()

        print("\n==============================================")
        print(f"       ATTENDANCE FOR STUDENT {student_id}")
        print("==============================================")

        if not records:

            print("No attendance records found.")

        else:

            # Student name is in the first column
            name = records[0][0]

            print(f"Student Name: {name}")
            print("----------------------------------------------")

            print(
                f"{'DATE':<15}"
                f"{'TIME':<15}"
                f"{'STATUS':<10}"
            )

            print("----------------------------------------------")

            for record in records:

                attendance_date = record[1]
                attendance_time = record[2]
                status = record[3]

                print(
                    f"{str(attendance_date):<15}"
                    f"{str(attendance_time):<15}"
                    f"{status:<10}"
                )

            print("----------------------------------------------")
            print(f"Total Attendance Records: {len(records)}")

        print("==============================================\n")

    except Exception as e:

        print("Database error:")
        print(e)

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ==========================================
# MENU
# ==========================================

def main():

    while True:

        print("\n==============================================")
        print("       FACIAL ATTENDANCE MANAGEMENT")
        print("==============================================")
        print("1. View Today's Attendance")
        print("2. View All Attendance")
        print("3. View Student Attendance")
        print("4. Exit")
        print("==============================================")

        choice = input("Enter your choice: ").strip()

        if choice == "1":

            view_today_attendance()

        elif choice == "2":

            view_all_attendance()

        elif choice == "3":

            view_student_attendance()

        elif choice == "4":

            print("\nExiting Attendance Management System...")
            break

        else:

            print("\nInvalid choice. Please try again.")


# ==========================================
# MAIN
# ==========================================

if __name__ == "__main__":

    main()