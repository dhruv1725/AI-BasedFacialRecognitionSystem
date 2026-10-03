from app.database.db import get_connection


def check_database():

    connection = None
    cursor = None

    try:
        connection = get_connection()

        if connection is None:
            print("Could not connect to database.")
            return

        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                column_name,
                data_type
            FROM information_schema.columns
            WHERE table_name = 'attendance'
            ORDER BY ordinal_position;
        """)

        columns = cursor.fetchall()

        print("\n========== ATTENDANCE TABLE ==========\n")

        if not columns:
            print("Attendance table not found.")
        else:
            for column in columns:
                print(
                    f"Column: {column[0]} | "
                    f"Type: {column[1]}"
                )

        print("\n======================================")

    except Exception as e:
        print("Database error:", e)

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()


if __name__ == "__main__":
    check_database()