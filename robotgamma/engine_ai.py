from __future__ import annotations
import streamlit as st
import json
from openai import OpenAI

# [개선] 1,000개 이상의 원료 라이브러리를 코드 내 딕셔너리로 관리 (예시 구조)
INGREDIENT_LIBRARY = {
    "Base": ["NFC 사과즙 Type 1~100", "사과농축액(72Brix) Type 101~300", "사과퓨레 Type 301~400"],
    "Sweetener": {
        "천연 감미 (Natural)": ["정백당 A~Z", "결정과당 G1~G50", "꿀/시럽류 50종"],
        "저칼로리/기능성 (Functional)": ["액상알룰로스 L1~L100", "에리스리톨", "자일리톨"],
        "고감미/제로 (Zero-Sugar)": ["효소처리스테비아 S1~S100", "수크랄로스", "나한과추출물"]
    },
    "Additive": ["구연산", "DL-사과산", "비타민C", "펙틴", "천연향료", "잔탄검", "나한과추출분말"]
}

def propose_formula(flavor: str, selected_category: str, selected_sweeteners: list, base_type: str):
    """
    AI 시니어 연구원: 내재화된 1,000포인트 라이브러리를 참조하여 초고속 배합 설계
    """
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    sweetener_ctx = ", ".join(selected_sweeteners)
    
    # AI에게 라이브러리 구조를 인지시키고 비중 할당 지시
    prompt = f"""
    너는 20년 경력의 'AI 시니어 식품연구원'이다. '{flavor}' 테마의 '{base_type}' 음료를 설계하라.
    
    [R&D 라이브러리 로직]
    1. 정제수 제외 원료 총합을 1,000포인트로 설정하라.
    2. {base_type}와 {sweetener_ctx}의 비중(%)에 따라 코드 내 정의된 라이브러리 뎁스에서 원료를 선별하라.
    3. 원료 구성: 10~15종. (원료명, AI 추천%, min%, max%, 사용목적, 주의사항)
    4. 학술 근거: DBpia, RISS 등 국내 DB 검색이 가능한 실제 논문 제목을 포함하라.
    5. 출력: 반드시 JSON 형식 엄격 준수.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini", # 로드 부담이 적은 모델 사용
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        st.error(f"AI 분석 엔진 에러: {e}")
        return None
