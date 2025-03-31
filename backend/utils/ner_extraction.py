# backend/utils/ner_extraction.py
from transformers import pipeline
#from config import OPENAI_API_KEY  # 필요 시 사용

# NER 파이프라인 설정 (모델, 토크나이저는 적절히 수정)
ner_pipeline = pipeline("ner", model="rkdaldus/ko-sent5-classification", tokenizer="monologg/kobert", trust_remote_code=True)

def extract_entities(text):
    """
    주어진 텍스트에 대해 NER 파이프라인을 실행하여 개체명 인식 결과를 추출합니다.
    반환 예시: [{"word": "서울", "type": "B-LOC"}, {"word": "한국", "type": "I-LOC"}, ...]
    Firestore에 저장 가능한 딕셔너리 형태로 반환합니다.
    """
    ner_results = ner_pipeline(text)
    entities = [{"word": res["word"], "type": res["entity"]} for res in ner_results]
    return entities
