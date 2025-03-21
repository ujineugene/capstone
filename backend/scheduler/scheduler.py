# backend/scheduler/scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from utils.email_utils import send_email

scheduler = BackgroundScheduler()

def schedule_letter_send(letter, to_email, subject="1년 후의 나에게 보내는 편지"):
    run_date = datetime.now() + timedelta(days=365)
    scheduler.add_job(send_email, 'date', run_date=run_date, args=[subject, letter, to_email])
    scheduler.start()

def init_scheduler():
    if not scheduler.running:
        scheduler.start()
