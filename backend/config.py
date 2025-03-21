
import os
from dotenv import load_dotenv

load_dotenv() 

DEBUG = True
FIREBASE_CREDENTIALS_PATH = os.environ.get('FIREBASE_CREDENTIALS_PATH')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
EMAIL_FROM = os.environ.get('EMAIL_FROM')
SMTP_SERVER = os.environ.get('SMTP_SERVER')
SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))
SMTP_USER = os.environ.get('SMTP_USER')
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD')

