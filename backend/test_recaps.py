# backend/test_recaps.py
import firebase_admin
from firebase_admin import credentials, firestore
from config import FIREBASE_CREDENTIALS_PATH
from scheduler.scheduler import run_monthly_recaps
# Firebase 초기화 (app.py와 동일하게)

<<<<<<< HEAD
cred = credentials.Certificate("FIREBASE_CREDENTIALS_PATH")
=======
cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH) #경로를 못찾아서 실제 실행시엔 파일이름 바로 넣어서 돌림
>>>>>>> aeac0bdb4934469c3d60e18ca54c348bd6c0fd57
firebase_admin.initialize_app(cred)

# run_monthly_recaps() 호출하여 월간 리캡 데이터를 생성
run_monthly_recaps()

# 결과 확인: 콘솔에 "Monthly recaps generated at ..." 메시지가 출력되면 성공
