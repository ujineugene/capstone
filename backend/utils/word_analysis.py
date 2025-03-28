# backend/utils/word_analysis.py
from collections import Counter
from konlpy.tag import Okt

def analyze_word_frequency(diaries, top_n=5):
    """
    diaries: 일기 데이터 리스트 (각 항목은 dict이며 'content' 필드 포함)
    top_n: 상위 몇 개 단어를 반환할지 지정 (기본 10)
    
    KoNLPy의 Okt를 사용하여 각 일기 내용에서 명사를 추출한 후, 
    가장 많이 사용된 단어와 그 빈도수를 반환합니다.
    
    반환 형식: [{"word": "행복", "count": 5}, {"word": "우울", "count": 3}, ...]
    """
    okt = Okt()
    all_words = []
    
    for diary in diaries:
        content = diary.get("content", "")
        if content:
            words = okt.nouns(content)
            all_words.extend(words)
    
    # 단어 빈도 계산
    counter = Counter(all_words)
    most_common = counter.most_common(top_n)
    # 튜플 형식을 딕셔너리 형식으로 변환
    most_common_dict = [{"word": word, "count": count} for word, count in most_common]
    
    if len(most_common_dict) == 0:
        return "일기에서 단어를 찾을 수 없습니다."
    elif len(most_common_dict) == 1:
        return f"가장 많이 사용한 단어는 {most_common_dict[0]['word']}입니다."
    else:
        return f"가장 많이 사용한 단어는 {most_common_dict[0]['word']}이고 두번째로 많이 사용한 단어는 {most_common_dict[1]['word']}야."
