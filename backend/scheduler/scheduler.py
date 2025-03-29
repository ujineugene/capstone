# backend/scheduler/scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import pytz
from firebase_admin import firestore
from utils.sentiment_analysis import generate_monthly_sentiment_summary, get_dominant_emotion
from utils.word_analysis import analyze_word_frequency
from utils.monthly_letter import generate_monthly_letter
from collections import Counter

scheduler = BackgroundScheduler()

def get_user_diaries_for_month(uid, month, year):
    """
    Firestore의 'diaries' 컬렉션에서 해당 사용자의 지정 월(YYYY-MM)의 일기 데이터를 반환합니다.
    'date' 필드는 "YYYY-MM-DD" 형식으로 저장되어 있다고 가정합니다.
    """
    db = firestore.client()
    diaries_ref = db.collection('diaries')
    start_date_str = f"{year}-{month:02d}-01"
    if month == 12:
        next_month_year = year + 1
        next_month = 1
    else:
        next_month_year = year
        next_month = month + 1
    end_date_str = f"{next_month_year}-{next_month:02d}-01"
    
    query = diaries_ref.where("uid", "==", uid) \
                       .where("date", ">=", start_date_str) \
                       .where("date", "<", end_date_str)
    diaries = query.stream()
    diary_list = [diary.to_dict() for diary in diaries]
    return diary_list

def run_monthly_recaps():
    """
    각 사용자에 대해 해당 월의 일기 데이터를 조회하고,
    KoBERT 기반 감정 분석 요약과 단어 빈도 분석 결과를 생성하여,
    Firestore의 'monthly_recaps' 컬렉션에 저장합니다.
    """
    db = firestore.client()
    now = datetime.now(pytz.timezone('Asia/Seoul'))
    month = now.month
    year = now.year

    users = db.collection('users').stream()
    for user in users:
        user_data = user.to_dict()
        uid = user_data.get("uid")
        name = user_data.get("name", "나")
        diaries = get_user_diaries_for_month(uid, month, year)
        if diaries:
            '''
            summary = generate_monthly_sentiment_summary(diaries, month, year)
            top_words = analyze_word_frequency(diaries, top_n=5)
            recap_data = {
                "uid": uid,
                "name": name,
                "month": month,
                "year": year,
                "summary": summary,
                "top_words": top_words,
                "created_at": now.isoformat()
            }
            db.collection('monthly_recaps').add(recap_data)
    print("Monthly recaps generated at", now.isoformat())'''
            # 각 일기에 저장된 감정 결과를 활용하여 집계합니다.
            sentiment_counts = {"Angry": 0, "Fear": 0, "Happy": 0, "Tender": 0, "Sad": 0}
            total_entries = 0
            all_nouns = []
            for diary in diaries:
                # diary에 저장된 'sentiment' 필드가 존재한다면 사용
                s = diary.get("sentiment")
                if s and isinstance(s, list) and len(s) > 0:
                    label = s[0].get("label")
                    sentiment_counts[label] += 1
                total_entries += 1
                # diary에 저장된 'nouns' 필드를 합칩니다.
                nouns = diary.get("nouns", [])
                all_nouns.extend(nouns)
            
            # 감정 요약 문자열 생성
            summary_parts = [f"{emotion} {count}일" for emotion, count in sentiment_counts.items()]
            summary_text = ", ".join(summary_parts)
            summary = f"{month}월에는 총 {total_entries}개의 일기 중 {summary_text} 감정을 기록했어."
            
            # 우세 감정 산출
            dominant_emotion = max(sentiment_counts, key=sentiment_counts.get)
            
            # 단어 빈도 집계: 상위 3개 단어 선택
            counter = Counter(all_nouns)
            top_common = counter.most_common(3)
            if len(top_common) == 0:
                top_words_str = "일기에서 단어를 찾을 수 없습니다."
            elif len(top_common) == 1:
                top_words_str = f"가장 많이 사용한 단어는 {top_common[0][0]}입니다."
            else:
                top_words_str = (f"가장 많이 사용한 단어는 {top_common[0][0]}, "
                                 f"두번째는 {top_common[1][0]}, "
                                 f"세번째는 {top_common[2][0]}야.")
            
            recap_data = {
                "uid": uid,
                "name": name,
                "month": month,
                "year": year,
                "summary": summary,
                "top_words": top_words_str,
                "created_at": now.isoformat()
            }
            db.collection('monthly_recaps').add(recap_data)
    print("Monthly recaps generated at", now.isoformat())


def run_monthly_letters():
    """
    각 사용자에 대해 해당 월의 일기 데이터를 조회하고,
    감정 분석 결과(요약 및 가장 많이 느낀 감정)를 반영하여, OpenAI API를 사용한 prompt 기반 월간 편지를 생성하고,
    Firestore의 'monthly_letters' 컬렉션에 저장합니다.
    """
    db = firestore.client()
    now = datetime.now(pytz.timezone('Asia/Seoul'))
    month = now.monthㄴㄴ
    year = now.year

    users = db.collection('users').stream()
    for user in users:
        user_data = user.to_dict()
        uid = user_data.get("uid")
        name = user_data.get("name", "나")
        diaries = get_user_diaries_for_month(uid, month, year)
        if diaries:
            summary = generate_monthly_sentiment_summary(diaries, month, year)
            dominant_emotion = get_dominant_emotion(diaries)
            letter_text = generate_monthly_letter(name, month, year, summary, dominant_emotion)
            letter_data = {
                "uid": uid,
                "name": name,
                "month": month,
                "year": year,
                "letter": letter_text,
                "created_at": now.isoformat()
            }
            db.collection('monthly_letters').add(letter_data)
    print("Monthly letters generated at", now.isoformat())

def schedule_monthly_tasks():
    """
    매월 마지막 날 23:59(Asia/Seoul 기준)에 월간 리캡과 월간 편지 생성 작업을 예약합니다.
    """
    trigger = CronTrigger(day='last', hour=23, minute=59, timezone='Asia/Seoul')
    scheduler.add_job(run_monthly_recaps, trigger)
    scheduler.add_job(run_monthly_letters, trigger)
    scheduler.start()

def init_scheduler():
    schedule_monthly_tasks()

'''
# backend/scheduler/scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from utils.email_utils import send_email

scheduler = BackgroundScheduler()

def schedule_letter_send(letter, to_email, subject="1년 전 나에게서 온 편지"):
    run_date = datetime.now() + timedelta(days=365)
    scheduler.add_job(send_email, 'date', run_date=run_date, args=[subject, letter, to_email])
    scheduler.start()

def init_scheduler():
    if not scheduler.running:
        scheduler.start()'''
