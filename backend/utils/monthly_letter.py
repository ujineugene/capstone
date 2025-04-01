# backend/utils/monthly_letter.py
import openai
from config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

def generate_monthly_letter(name, month, year, summary, dominant_emotion, top_words):
    """
    name: 사용자 이름
    month, year: 분석 대상 월/연도
    summary: 감정 분석 요약 (예: "3월에는 총 10개의 일기 중 Angry:0일, Fear:0일, Happy:6일, Tender:0일, Sad:1일 감정을 기록했습니다.")
    dominant_emotion: 해당 달에 가장 많이 느낀 감정 (예: "Happy")
    top_words: 단어 빈도 분석 결과 문자열 (예: "가장 많이 사용한 단어는 학교이고 두번째로 많이 사용한 단어는 친구야.")
    
    이 정보를 바탕으로, 편지 생성 prompt에 감정 요약과 함께, 
    가장 많이 사용한 단어(첫 번째 단어)를 추출하여 추가적인 공감 및 응원의 메시지를 포함시킵니다.
    """
    # 추출: top_words 형식이 "가장 많이 사용한 단어는 학교이고 두번째로 많이 사용한 단어는 친구야."라고 가정
    try:
        first_word = top_words.split("가장 많이 사용한 단어는")[1].split("이고")[0].strip()
    except Exception:
        first_word = ""

    prompt = (
        f"안녕, {name}!\n\n"
        f"이번 달({year}년 {month}월)을 돌아보니, 네 일기를 분석한 결과 가장 많이 느낀 감정은 '{dominant_emotion}'이었어.\n"
        f"{summary}\n\n"
        "이번 달을 잘 보냈는지 스스로에게 물어보고, 네 감정에 공감하며 위로와 응원의 메시지를 담은 편지를 작성해줘. "
        "예를 들어, '하루하루 기록한 네 일기를 보니 힘든 날도 있었지만 그 경험이 너를 더욱 강하게 만들어줬어. 앞으로 더 행복한 날들이 오길 바라.'와 같은 내용을 포함해줘.\n\n"
        f"네 일기에서 '{first_word}'라는 단어가 자주 등장했어."
        "그 단어와 관련된 공감과 격려와 응원이 담긴 내용을 두세줄로 편지로 작성해줘.마지막 줄에는 다음 달에 대한 응원으로 마무리해줘.\n\n"
        "From. 이번 달의 너"
    )
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "너는 따뜻하고 공감이 가는 편지 작가야."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=500
    )
    
    letter_text = response.choices[0].message.content.strip()
    return letter_text
