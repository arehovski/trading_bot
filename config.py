import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent

if os.environ.get('ENV') == 'test':
    filepath = os.path.join(BASE_DIR, ".env.test")
else:
    filepath = os.path.join(BASE_DIR, ".env")

load_dotenv(filepath)

is_sandbox = True if os.environ.get('ENV') == 'test' else False

API_KEY = os.environ.get('API_KEY')
API_SECRET = os.environ.get('API_SECRET')
API_PASSPHRASE = os.environ.get('API_PASSPHRASE')

REDIS_HOST = os.environ.get('REDIS_HOST')
REDIS_PORT = os.environ.get('REDIS_PORT')
