from __future__ import annotations
import streamlit as st
import json
from openai import OpenAI

def propose_formula(flavor: str, selected_sweeteners: list, base_type: str):
    """
    AI 시니어 연구원: 정제수 제외 원료 총합 1,000 포인트를 기준으로 라이브러리 뎁스 할당
    """
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    sweetener_ctx = ", ".join(selected_sweeteners)
    
    prompt = f"""
    너는 20년 경력의 'AI 시니어 식품연구원'이다. '{flavor}' 테마의 '{base_type}' 음료를 설계하라.
    
    [R&D 설계 핵심 로직]
    1. 정제수를 제외한 나머지 원료의 비중 총합을 100%(=1,000포인트)로 본다.
    2. 각 원료가 차지하는 비중(%)에 10을 곱하여 해당 원료의 '라이브러리 검토 뎁스'를 결정하라.
       예: 농축액이 비중의 60%라면 600개의 라이브러리 종류 중 최적을 선택.
    3. 원료 구성: 10~15종 구성. (원료명, AI 추천%, min%, max%, 사용목적, 주의사항)
    4. 근거 섹션: 국내 DBpia, RISS 및 국외 PubMed 논문 링크를 포함하라.
    5. 출력 형식: 반드시 JSON 형식을 엄격히 준수하라 (JSON 단어 포함).
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
