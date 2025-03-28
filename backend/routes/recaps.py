# backend/routes/recaps.py
from flask import Blueprint, request, jsonify
from firebase_admin import auth, firestore

recaps_bp = Blueprint('recaps_bp', __name__, url_prefix='')

db = firestore.client()

@recaps_bp.route('/monthly_recaps', methods=['POST'])
def list_monthly_recaps():
    id_token = request.json.get('idToken')
    if not id_token:
        return jsonify({"error": "ID 토큰이 필요합니다."}), 400

    try:
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']
        
        # 사용자의 월간 리캡 목록을 생성일(created_at) 기준 내림차순으로 조회합니다.
        recaps_ref = db.collection('monthly_recaps')
        query = recaps_ref.where("uid", "==", uid).order_by("created_at", direction=firestore.Query.DESCENDING)
        recaps = query.stream()

        recap_list = []
        for recap in recaps:
            data = recap.to_dict()
            recap_list.append({
                "recap_id": recap.id,
                "month": data.get("month"),
                "year": data.get("year"),
                "summary": data.get("summary"),
                "top_words":data.get("top_words"),
                "created_at": data.get("created_at")
            })
        return jsonify({"monthly_recaps": recap_list}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500