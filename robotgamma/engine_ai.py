from __future__ import annotations
import streamlit as st
import json
from openai import OpenAI

def propose_formula(flavor: str, selected_category: str, selected_sweeteners: list, base_type: str):
    """
    AI 시니어 연구원: 당감미 특성 카테고리와 선택된 당류를 기반으로 정밀 배합
    """
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    sweetener_ctx = ", ".join(selected_sweeteners)
    
    prompt = f"""
    너는 20년 경력의 'AI 시니어 식품연구원'이다. '{flavor}' 테마의 '{base_type}' 음료를 설계하라.
    
    [당류 설계 조건]
    - 당감미 특성: {selected_category}
    - 선택된 당류: {sweetener_ctx}

    [R&D 설계 핵심 로직]
    1. 정제수 제외 원료 비중 총합을 100%(=1,000포인트)로 설정하라.
    2. 각 원료의 비중(%)에 10을 곱한 값이 해당 원료군의 '라이브러리 검토 뎁스'가 되도록 종류를 결정하라.
    3. 원료 구성: 10~15종. (원료명, AI 추천%, min%, max%, 사용목적, 주의사항)
    4. 근거 섹션: 국내 DBpia, RISS 논문 검색 링크 및 과학적 타당성을 포함하라.
    5. 출력: 반드시 JSON 형식을 엄격히 준수할 것.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        st.error(f"AI 분석 엔진 에러: {e}")
        return None
