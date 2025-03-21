# backend/routes/letter.py
from flask import Blueprint, request, jsonify
from firebase_admin import auth, firestore
from datetime import datetime, timedelta
from utils.openai_utils import generate_letter
from scheduler.scheduler import schedule_letter_send

letter_bp = Blueprint('letter_bp', __name__, url_prefix='')

db = firestore.client()

@letter_bp.route('/send_letter_by_date', methods=['POST'])
def send_letter_by_date():
    data = request.json
    id_token = data.get('idToken')
    date_str = data.get('date')  # "YYYY-MM-DD"
    email_address = data.get('email')
    if not id_token or not date_str or not email_address:
        return jsonify({"error": "ID 토큰, 날짜, 이메일 주소가 모두 필요합니다."}), 400

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
        if not diary_list:
            return jsonify({"error": "해당 날짜에 저장된 일기가 없습니다."}), 404

        combined_diary_text = "\n\n".join(entry["diary"] for entry in diary_list)
        letter = generate_letter(combined_diary_text)
        schedule_letter_send(letter, email_address)
        return jsonify({"message": "편지가 생성되었고, 1년 후에 이메일로 전송되도록 예약되었습니다."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
