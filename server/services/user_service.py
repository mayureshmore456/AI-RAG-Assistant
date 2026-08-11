import psycopg
import bcrypt

from server.config import DATABASE_URL


class UserService:
    """
    Handles user registration and authentication.
    """

    def __init__(self):
        self.database_url = DATABASE_URL

    # --------------------------------
    # Database Connection
    # --------------------------------

    def _get_connection(self):
        return psycopg.connect(self.database_url)

    # --------------------------------
    # Hash Password
    # --------------------------------

    def hash_password(self, password):

        password_bytes = password.encode("utf-8")

        hashed_password = bcrypt.hashpw(
            password_bytes,
            bcrypt.gensalt()
        )

        return hashed_password.decode("utf-8")

    # --------------------------------
    # Verify Password
    # --------------------------------

    def verify_password(self, password, password_hash):

        password_bytes = password.encode("utf-8")

        hashed_password_bytes = password_hash.encode("utf-8")

        return bcrypt.checkpw(
            password_bytes,
            hashed_password_bytes
        )

    # --------------------------------
    # Create User
    # --------------------------------

    def create_user(self, name, email, password):

        password_hash = self.hash_password(password)

        with self._get_connection() as connection:

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    INSERT INTO users (
                        name,
                        email,
                        password_hash
                    )
                    VALUES (%s, %s, %s)
                    RETURNING id, name, email, created_at;
                    """,
                    (
                        name,
                        email,
                        password_hash
                    )
                )

                user = cursor.fetchone()

            connection.commit()

        return {
            "id": str(user[0]),
            "name": user[1],
            "email": user[2],
            "created_at": user[3]
        }

    # --------------------------------
    # Find User By Email
    # --------------------------------

    def get_user_by_email(self, email):

        with self._get_connection() as connection:

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    SELECT
                        id,
                        name,
                        email,
                        password_hash,
                        created_at
                    FROM users
                    WHERE email = %s;
                    """,
                    (email,)
                )

                user = cursor.fetchone()

        if user is None:
            return None

        return {
            "id": str(user[0]),
            "name": user[1],
            "email": user[2],
            "password_hash": user[3],
            "created_at": user[4]
        }

    # --------------------------------
    # Authenticate User
    # --------------------------------

    def authenticate_user(self, email, password):

        user = self.get_user_by_email(email)

        if user is None:
            return None

        password_valid = self.verify_password(
            password,
            user["password_hash"]
        )

        if not password_valid:
            return None

        # Never return password_hash
        user.pop("password_hash")

        return user