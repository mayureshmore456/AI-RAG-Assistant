import jwt
from datetime import datetime, timedelta, timezone

from server.config import JWT_SECRET_KEY


class AuthService:
    """
    Handles JWT token creation and verification.
    """

    def __init__(self):
        self.secret_key = JWT_SECRET_KEY
        self.algorithm = "HS256"

    # --------------------------------
    # Create Token
    # --------------------------------

    def create_access_token(self, user_id):

        payload = {
            "user_id": user_id,
            "exp": datetime.now(timezone.utc) + timedelta(hours=24)
        }

        token = jwt.encode(
            payload,
            self.secret_key,
            algorithm=self.algorithm
        )

        return token

    # --------------------------------
    # Verify Token
    # --------------------------------

    def verify_token(self, token):

        try:

            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )

            return payload

        except jwt.ExpiredSignatureError:

            return None

        except jwt.InvalidTokenError:

            return None