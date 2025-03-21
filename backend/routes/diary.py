# backend/routes/diary.py
from flask import Blueprint, request, jsonify
from firebase_admin import auth
from firebase_admin import firestore
from datetime import datetime, timedelta
import pytz

diary_bp = Blueprint('diary_bp', __name__, url_prefix='')

db = firestore.client()

# 일기 저장 엔드포인트
@diary_bp.route('/diary', methods=['POST'])
def write_diary():
    id_token = request.json.get('idToken')
    diary_text = request.json.get('diary')
    if not id_token or not diary_text:
        return jsonify({"error": "ID 토큰과 일기 내용이 필요합니다."}), 400
    try:
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']
        now = datetime.now(pytz.timezone('Asia/Seoul'))
        diary_entry = {
            "uid": uid,
            "diary": diary_text,
            "timestamp": now.isoformat()
        }
        db.collection('diaries').add(diary_entry)
        return jsonify({"message": "일기가 저장되었습니다."}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 날짜별 일기 조회 엔드포인트
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
