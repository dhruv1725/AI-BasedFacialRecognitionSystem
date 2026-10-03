import psycopg2


# ============================================================
# DATABASE CONFIGURATION
# ============================================================

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "facial-attendance",
    "user": "postgres",
    "password": "Dhruv@123456"
}


# ============================================================
# GET DATABASE CONNECTION
# ============================================================

def get_connection():
    """
    Create and return a PostgreSQL database connection.

    Returns:
        psycopg2 connection object if successful.
        None if connection fails.
    """

    try:
        connection = psycopg2.connect(
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"],
            database=DB_CONFIG["database"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"]
        )

        return connection

    except psycopg2.Error as e:

        print("Database connection error:")
        print(e)

        return None
