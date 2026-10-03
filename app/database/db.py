import os
import psycopg2


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():
    """
    Create and return a PostgreSQL database connection.

    Local:
        Uses individual DB environment variables.

    Render:
        Uses DATABASE_URL.

    Returns:
        psycopg2 connection object if successful.
        None if connection fails.
    """

    try:

        database_url = os.getenv("DATABASE_URL")

        # ====================================================
        # RENDER / PRODUCTION
        # ====================================================

        if database_url:

            connection = psycopg2.connect(
                database_url
            )

        # ====================================================
        # LOCAL DEVELOPMENT
        # ====================================================

        else:

            connection = psycopg2.connect(
                host=os.getenv("DB_HOST", "localhost"),
                port=os.getenv("DB_PORT", "5432"),
                database=os.getenv(
                    "DB_NAME",
                    "facial-attendance"
                ),
                user=os.getenv(
                    "DB_USER",
                    "postgres"
                ),
                password=os.getenv(
                    "DB_PASSWORD"
                )
            )

        return connection

    except psycopg2.Error as e:

        print("Database connection error:")
        print(e)

        return None