from utils import memoize
import json
import secrets
import string

@memoize
def get_google_client_id():
    client_secret = json.load(open('client_secret.json'))
    return client_secret['web']['client_id']

def generate_random_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(characters) for _ in range(length))
    return password
