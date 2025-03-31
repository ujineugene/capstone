# backend/routes/profile.py
from flask import Blueprint, request, jsonify
from firebase_admin import auth, firestore
from config import DEBUG

profile_bp = Blueprint('profile_bp', __name__, url_prefix='')

db = firestore.client()

# 회원정보 불러오기 엔드포인트
'''
함수 get_my_profile()
변수 idToken, uid, user_data(firstore,딕셔너리)
'''
@profile_bp.route('/my_profile', methods=['POST'])
def get_my_profile():
    id_token = request.json.get('idToken')
    if not id_token:
        return jsonify({"error": "ID 토큰이 필요합니다."}), 400

    try:
        # Firebase ID 토큰 검증
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token.get('uid')
        
        # Firestore에서 사용자 정보 조회
        user_doc = db.collection('users').document(uid).get()
        if user_doc.exists:
            user_data = user_doc.to_dict()
            return jsonify({"user": user_data}), 200
        else:
            return jsonify({"error": "사용자 정보를 찾을 수 없습니다."}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


#회원정보 수정 엔드포인트
'''
함수 update_profile()
변수 idToken, new_name, new_email, update_data(딕셔너리)
'''
@profile_bp.route('/update_profile', methods=['POST'])
def update_profile():
    """
    클라이언트에서 idToken과 수정할 정보를 받아,
    Firestore의 사용자 문서 및 Firebase Authentication(이메일 변경 등)에 반영합니다.
    """
    data = request.json
    id_token = data.get('idToken')
    new_name = data.get('name')     # 수정할 이름
    new_email = data.get('email')   # 수정할 이메일 (선택사항)
    
    if not id_token:
        return jsonify({"error": "ID 토큰이 필요합니다."}), 400
    
    try:
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']
        
        # Firebase Authentication에서 사용자 프로필(이메일) 업데이트
        # (이메일 변경 시, 보안 정책에 따라 추가 인증이 필요할 수 있음)
        if new_email:
            auth.update_user(uid, email=new_email)
        
        # Firestore 'users' 컬렉션에서 사용자 문서 업데이트
        user_ref = db.collection('users').document(uid)
        
        update_data = {}
        if new_name:
            update_data["name"] = new_name
        if new_email:
            update_data["email"] = new_email
        
        if update_data:
            user_ref.update(update_data)
        
        return jsonify({"message": "회원정보가 성공적으로 업데이트되었습니다."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
