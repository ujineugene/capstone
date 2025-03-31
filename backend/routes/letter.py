# backend/routes/letters.py
from flask import Blueprint, request, jsonify
from firebase_admin import auth, firestore

letters_bp = Blueprint('letters_bp', __name__, url_prefix='')

db = firestore.client()

@letters_bp.route('/monthly_letters', methods=['POST'])
def list_monthly_letters():
    id_token = request.json.get('idToken')
    if not id_token:
        return jsonify({"error": "ID 토큰이 필요합니다."}), 400
    try:
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']
        letters_ref = db.collection('monthly_letters')
        query = letters_ref.where("uid", "==", uid).order_by("created_at", direction=firestore.Query.DESCENDING)
        letters = query.stream()

        letter_list = []
        for letter in letters:
            data = letter.to_dict()
            letter_list.append({
                "letter_id": letter.id,
                "month": data.get("month"),
                "year": data.get("year"),
                "letter": data.get("letter"),
                "created_at": data.get("created_at")
            })
        return jsonify({"monthly_letters": letter_list}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
