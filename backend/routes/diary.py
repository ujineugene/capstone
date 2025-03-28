# backend/routes/diary.py
from flask import Blueprint, request, jsonify
from firebase_admin import auth, firestore
from datetime import datetime
import pytz
from utils.sentiment_analysis import analyze_sentiment  # 감정분석함수사용
from konlpy.tag import Okt

diary_bp = Blueprint('diary_bp', __name__, url_prefix='')

db = firestore.client()

@diary_bp.route('/diary', methods=['POST'])
def create_diary():
    id_token = request.json.get('idToken')
    date = request.json.get('date')      # 사용자 지정 날짜(YYYY-MM-DD)
    title = request.json.get('title')
    content = request.json.get('content')
    
    if not id_token or not date or not title or not content:
        return jsonify({"error": "ID 토큰, 날짜, 제목, 내용이 모두 필요합니다."}), 400
    
    try:
        # Firebase 토큰 검증
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']
        now = datetime.now(pytz.timezone('Asia/Seoul')).isoformat()
        diary_entry = {
            "uid": uid,
            "date": date,          # 사용자 지정한 날짜(YYYY-MM-DD)
            "title": title,
            "content": content,
            "timestamp": now }
        
        result=db.collection('diaries').add(diary_entry)
        doc_ref=result[1]

        sentiment_result = analyze_sentiment(content)   #감정분석 
      
        okt = Okt()
        nouns = okt.nouns(content)   #단어명사분석

        analysis_data={"sentiment" :sentiment_result ,"nouns":nouns}

        doc_ref.update(analysis_data)

        return jsonify({"message": "일기가 저장되고 분석 결과가 업데이트되었습니다."}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
        
        '''
        sentiment_result = analyze_sentiment(content)

        okt = Okt()
        nouns = okt.nouns(content)

        diary_entry = {
            "uid": uid,
            "date": date,          # 사용자가 지정한 날짜 (YYYY-MM-DD)
            "title": title,
            "content": content,
            "timestamp": now,      # 저장 시각
            "sentiment" :sentiment_result ,
            "nouns":nouns
        }

        db.collection('diaries').add(diary_entry) 
        
        return jsonify({"message": "일기가 저장되고 분석 결과가 업데이트되었습니다."}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500'''

# backend/routes/diary.py

#일기 수정 
@diary_bp.route('/update_diary', methods=['POST'])
def update_diary():
    """
    일기 수정 API:
    클라이언트로부터 idToken, diary_id, 새 제목, 새 내용, (선택적으로) 새 날짜를 받아,
    해당 일기 문서를 업데이트한 후 새 내용으로 감정 분석 및 단어(명사) 추출을 재실행하여
    분석 결과를 문서에 업데이트합니다.
    """
    id_token = request.json.get('idToken')
    diary_id = request.json.get('diary_id')
    new_title = request.json.get('title')
    new_content = request.json.get('content')
    new_date = request.json.get('date')  # 선택사항

    if not id_token or not diary_id or not new_title or not new_content:
        return jsonify({"error": "ID 토큰, 일기 ID, 새 제목, 새 내용이 필요합니다."}), 400

    try:
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']

        # 해당 일기 문서 참조
        doc_ref = db.collection('diaries').document(diary_id)
        doc = doc_ref.get()
        if not doc.exists:
            return jsonify({"error": "일기를 찾을 수 없습니다."}), 404

        data = doc.to_dict()
        # 문서의 uid와 요청한 사용자의 uid가 일치하는지 확인
        if data.get("uid") != uid:
            return jsonify({"error": "권한이 없습니다."}), 403

        now = datetime.now(pytz.timezone('Asia/Seoul')).isoformat()

        # 일기 내용 업데이트 (새 제목, 내용, 날짜, 타임스탬프)
        update_data = {
            "title": new_title,
            "content": new_content,
            "timestamp": now
        }
        if new_date:
            update_data["date"] = new_date

        doc_ref.update(update_data)

        # 감정 분석 및 단어명사 추출 수행
        sentiment_result = analyze_sentiment(new_content) 
        okt = Okt()
        nouns = okt.nouns(new_content)  

        analysis_data = {
            "sentiment": sentiment_result,
            "nouns": nouns
        }
        doc_ref.update(analysis_data)

        return jsonify({"message": "일기가 수정되고 분석 결과가 업데이트되었습니다."}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



# backend/routes/diary.py 일기 제목/날짜 리스트업업
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