import jwt
import datetime
from werkzeug.exceptions import Unauthorized


class JwtError(Exception):
    """Exception raised for jwt errors in the quiz app 
    """

    def __init__(self, message="Jwt error"):
        self.message = message
        super().__init__(self.message)


secret = "Groupe Julien Danny"
expiration_in_seconds = 3600


def build_token():
    """
    Generates the Auth Token
    :return: string
    """
    try:
        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=expiration_in_seconds),
            'iat': datetime.datetime.utcnow(),
            'sub': 'quiz-app-admin'
        }
        return jwt.encode(
            payload,
            secret,
            algorithm="HS256"
        )
    except Exception as e:
        return e


def decode_token(auth_token):
    """
    Decodes the auth token
    :param auth_token: The full token string (e.g., "Bearer <token>")
    :return: string (the 'sub' claim in the payload)
    """
    try:
        token = auth_token.split("Bearer ")[-1]
        print(f"Token after split: {token}")  # Debugging
        payload = jwt.decode(token, secret, algorithms="HS256")
        print(f"Decoded Payload: {payload}")  # Debugging
        return payload['sub']
    except jwt.ExpiredSignatureError:
        raise JwtError('Signature expired. Please log in again.')
    except jwt.InvalidTokenError as e:
        print(f"Decoding Error: {e}")  # Debugging
        raise JwtError('Invalid token. Please log in again.')


