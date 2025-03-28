# backend/routes/auth.py
from flask import Blueprint, request, jsonify
from firebase_admin import auth
from config import DEBUG
from firebase_admin import firestore

auth_bp = Blueprint('auth_bp', __name__, url_prefix='')

db = firestore.client()  # 필요한 경우 사용

# 회원가입 엔드포인트
@auth_bp.route('/signup', methods=['POST'])
def signup():
    email = request.json.get('email')
    password = request.json.get('password')
    name = request.json.get('name') 
    if not email or not password or not name:
        return jsonify({"error": "이메일, 비밀번호, 이름을 모두 입력하세요."}), 400

    try:
        user = auth.create_user(email=email, password=password)
        user_data = {"email": email, 
                     "uid": user.uid,
                     "name": name}
        db.collection('users').document(user.uid).set(user_data)
        
        return jsonify({"message": "회원가입이 완료되었습니다.", "uid": user.uid}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 로그인 엔드포인트
@auth_bp.route('/login', methods=['POST'])
def login():
    id_token = request.json.get('idToken')
    if not id_token:
        return jsonify({"error": "ID 토큰이 필요합니다."}), 400

    try:
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']
        return jsonify({"message": "로그인 성공", "uid": uid}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
