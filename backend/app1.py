'''# backend/app.py
from flask import Flask
import firebase_admin
from firebase_admin import credentials, firestore
from config import DEBUG, FIREBASE_CREDENTIALS_PATH
from routes.auth import auth_bp
from routes.diary import diary_bp
from routes.letter import letter_bp
from scheduler.scheduler import init_scheduler

app = Flask(__name__)
app.config['DEBUG'] = DEBUG

# Firebase 초기화
cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
firebase_admin.initialize_app(cred)
# Firestore 클라이언트는 필요시 utils나 각 라우트에서 불러오면 됩니다.
db = firestore.client()

# 블루프린트 등록
app.register_blueprint(auth_bp)
app.register_blueprint(diary_bp)
app.register_blueprint(letter_bp)

# 스케줄러 초기화
init_scheduler()

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=DEBUG)
'''
# app1.py
from flask import Flask
import firebase_admin
from firebase_admin import credentials, firestore
from config import FIREBASE_CREDENTIALS_PATH, DEBUG

# 가장 먼저 Firebase 초기화
cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
firebase_admin.initialize_app(cred)

app = Flask(__name__)
app.config['DEBUG'] = DEBUG

# 그 이후에 라우트 모듈을 import합니다.
from routes.auth import auth_bp
from routes.diary import diary_bp
from routes.letter import letter_bp
from scheduler.scheduler import init_scheduler

# 블루프린트 등록
app.register_blueprint(auth_bp)
app.register_blueprint(diary_bp)
app.register_blueprint(letter_bp)

# 스케줄러 초기화
init_scheduler()

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=DEBUG)
