# backend/utils/openai_utils.py
import openai
from config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

def generate_letter(diary_text):
    prompt = (
        "다음 일기 내용을 참고하여 1년 후의 나에게 보내는 편지를 작성해줘. "
        "편지에는 1년 전의 나의 상황과 감정이 담겨 있으며, "
        "미래에 대한 안부와 변화에 대한 궁금증, 응원을 포함해줘.\n\n"
        f"{diary_text}"
    )
    response = openai.ChatCompletion.create(
       model="gpt-3.5-turbo",
       messages=[
           {"role": "system", "content": "너는 따뜻하고 격려하는 어조의 친구같은 편지 작가야."},
           {"role": "user", "content": prompt}
       ],
       max_tokens=500
    )
    letter = response.choices[0].message.content.strip()
    return letter
