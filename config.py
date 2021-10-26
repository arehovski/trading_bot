import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent

if os.environ.get('ENV') == 'test':
    filepath = os.path.join(BASE_DIR, ".env.test")
else:
    filepath = os.path.join(BASE_DIR, ".env")

load_dotenv(filepath)

API_KEY = os.environ.get('API_KEY')
API_SECRET = os.environ.get('API_SECRET')
API_PASSPHRASE = os.environ.get('API_PASSPHRASE')
