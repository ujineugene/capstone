# backend/utils/sentiment_analysis.py
'''from transformers import BertTokenizer, BertForSequenceClassification, pipeline
# KoBERT 및 fine-tuned 감정 분석 모델 불러오기
MODEL_NAME = "monologg/kobert-finetuned-sentiment"
tokenizer = BertTokenizer.from_pretrained("monologg/kobert")
model = BertForSequenceClassification.from_pretrained(MODEL_NAME)
sentiment_pipeline = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)'''

import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# 모델 및 토크나이저 로드
MODEL_NAME = "rkdaldus/ko-sent5-classification"
# KoBERT 토크나이저는 "monologg/kobert"를 사용하며, trust_remote_code=True 옵션을 추가합니다.
tokenizer = AutoTokenizer.from_pretrained("monologg/kobert", trust_remote_code=True)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)

def analyze_sentiment(text):
    """
    주어진 텍스트에 대해 감정 분석 결과를 반환합니다.
    반환 예시: [{'label': 'Happy', 'score': 0.95}]
    """
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
    with torch.no_grad():
        outputs = model(**inputs)
    # 예측된 라벨과 점수 산출 (Softmax 적용)
    predicted_label = torch.argmax(outputs.logits, dim=1).item()
    probs = F.softmax(outputs.logits, dim=1)
    score = probs[0, predicted_label].item()

    # 감정 레이블 정의 (예시)
    emotion_labels = {
        0: ("Angry", "😡"),
        1: ("Fear", "😨"),
        2: ("Happy", "😊"),
        3: ("Tender", "🥰"),
        4: ("Sad", "😢")
    }
    # 해당 모델이 반환하는 숫자가 위의 범주와 일치하는지 확인해야 합니다.
    return [{"label": emotion_labels[predicted_label][0], "score": score}]

def generate_monthly_sentiment_summary(diaries, month, year):
    """
    diaries: 해당 사용자의 월간 일기 데이터 리스트 (각 항목은 dict이며 'content' 필드 포함)
    month, year: 분석 대상 월과 연도 (예: 3, 2025)
    
    각 일기의 'content'에 대해 감정 분석을 수행하여, 감정별 일기 수를 집계한 후
    요약 문자열을 생성합니다.
    """
    sentiment_counts = {"Angry": 0, "Fear": 0, "Happy": 0, "Tender": 0, "Sad": 0}
    total_entries = 0

    for diary in diaries:
        content = diary.get("content", "")
        if content:
            results = analyze_sentiment(content)
            if results and isinstance(results, list):
                label = results[0].get("label")
                if label in sentiment_counts:
                    sentiment_counts[label] += 1
                else:
                    sentiment_counts[label] = sentiment_counts.get(label, 0) + 1
            total_entries += 1

    summary_parts = [f"{sentiment} : {count}일" for sentiment, count in sentiment_counts.items()]
    summary_text = ", ".join(summary_parts)
    summary = f"{month}월에는 총 {total_entries}개의 일기 중 {summary_text} 감정을 기록했습니다."
    return summary

def get_dominant_emotion(diaries):
    """
    각 일기의 'content'에 대해 감정 분석을 수행하고, 
    가장 많이 나온 감정을 반환합니다.
    """
    sentiment_counts = {"Angry": 0, "Fear": 0, "Happy": 0, "Tender": 0, "Sad": 0}
    for diary in diaries:
        content = diary.get("content", "")
        if content:
            results = analyze_sentiment(content)
            if results and isinstance(results, list):
                label = results[0].get("label")
                sentiment_counts[label] += 1
    # 만약 일기가 없으면 기본값 "중립" 반환
    dominant_emotion = max(sentiment_counts, key=sentiment_counts.get) if sentiment_counts else "중립"
    return dominant_emotion
