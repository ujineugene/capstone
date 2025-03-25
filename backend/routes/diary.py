# backend/routes/diary.py
from flask import Blueprint, request, jsonify
from firebase_admin import auth, firestore
from datetime import datetime
import pytz

diary_bp = Blueprint('diary_bp', __name__, url_prefix='')

db = firestore.client()

@diary_bp.route('/diary', methods=['POST'])
def create_diary():
    id_token = request.json.get('idToken')
    date = request.json.get('date')      # 사용자 지정 날짜, 예: "2025-03-18"
    title = request.json.get('title')
    content = request.json.get('content')
    
    if not id_token or not date or not title or not content:
        return jsonify({"error": "ID 토큰, 날짜, 제목, 내용이 모두 필요합니다."}), 400
    
    try:
        # Firebase 토큰 검증
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']
        
        # 현재 시간 (시스템 저장 시각)
        now = datetime.now(pytz.timezone('Asia/Seoul')).isoformat()
        
        diary_entry = {
            "uid": uid,
            "date": date,          # 사용자가 지정한 날짜 (YYYY-MM-DD)
            "title": title,
            "content": content,
            "timestamp": now       # 저장 시각
        }
        
        db.collection('diaries').add(diary_entry)
        return jsonify({"message": "일기가 저장되었습니다."}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

'''
# 날짜별 일기 조회 엔드포인트 한번에 모든걸 조회회
@diary_bp.route('/get_diary_bydate', methods=['POST'])
def get_diary_by_date():
    id_token = request.json.get('idToken')
    date_str = request.json.get('date')  # "YYYY-MM-DD"
    if not id_token or not date_str:
        return jsonify({"error": "ID 토큰과 날짜가 필요합니다."}), 400
    try:
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']
        start_date = datetime.fromisoformat(date_str)
        start_time = start_date.strftime("%Y-%m-%dT00:00:00")
        end_date = start_date + timedelta(days=1)
        end_time = end_date.strftime("%Y-%m-%dT00:00:00")
        diaries_ref = db.collection('diaries')
        query = diaries_ref.where("uid", "==", uid)\
                           .where("timestamp", ">=", start_time)\
                           .where("timestamp", "<", end_time)
        diaries = query.stream()
        diary_list = [diary.to_dict() for diary in diaries]
        diary_list = sorted(diary_list, key=lambda x: x['timestamp'])
        return jsonify({"diaries": diary_list}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
'''
# backend/routes/diary.py 제목/날짜 리스트
@diary_bp.route('/list_diaries', methods=['POST'])
def list_diaries():
    id_token = request.json.get('idToken')
    if not id_token:
        return jsonify({"error": "ID 토큰이 필요합니다."}), 400
    try:
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']
        
        # Firestore에서 해당 사용자의 일기 문서들을 'date' 필드를 기준으로 내림차순 정렬합니다.
        diaries_ref = db.collection('diaries')
        # 날짜 형식이 YYYY-MM-DD이면 문자열 정렬이 올바르게 작동합니다.
        query = diaries_ref.where("uid", "==", uid).order_by("date", direction=firestore.Query.DESCENDING)
        diaries = query.stream()
        
        diary_list = []
        for diary in diaries:
            data = diary.to_dict()
            diary_list.append({
                "diary_id": diary.id,
                "date": data.get("date"),
                "title": data.get("title")
            })
        return jsonify({"diaries": diary_list}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

#제목 선택시 상세 일기 불러오기
@diary_bp.route('/diary_detail', methods=['POST'])
def get_diary_detail():
    """
    클라이언트가 일기 상세 조회 요청 시,
    idToken과 diary_id를 받아 해당 일기의 모든 정보를 반환합니다.
    """
    id_token = request.json.get('idToken')
    diary_id = request.json.get('diary_id')
    
    if not id_token or not diary_id:
        return jsonify({"error": "ID 토큰과 일기 ID가 필요합니다."}), 400
    
    try:
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']
        
        # diary_id로 해당 일기 문서를 불러옴
        doc_ref = db.collection('diaries').document(diary_id)
        doc = doc_ref.get()
        if doc.exists:
            data = doc.to_dict()
            # 사용자가 작성한 일기가 맞는지 확인 (uid 일치)
            if data.get("uid") != uid:
                return jsonify({"error": "권한이 없습니다."}), 403
            return jsonify(data), 200
        else:
            return jsonify({"error": "일기를 찾을 수 없습니다."}), 404
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500