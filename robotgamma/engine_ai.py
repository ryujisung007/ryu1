from __future__ import annotations
import streamlit as st
import json
from openai import OpenAI

def propose_formula(flavor: str, selected_sweeteners: list, base_type: str):
    """
    AI 시니어 연구원이 1,000배수 식별 로직을 포함하여 배합 설계
    """
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    sweetener_ctx = ", ".join(selected_sweeteners)
    
    prompt = f"""
    너는 20년 경력의 'AI 시니어 식품연구원'이다. '{flavor}'를 테마로 한 '{base_type}' 기반 음료를 설계하라.
    당류는 [{sweetener_ctx}]를 사용하라. 

    [지시사항]
    1. 원료 10~15종 구성. 각 원료의 AI 추천값(AI)은 % 단위(예: 0.15)로 작성하라.
    2. 내부 식별을 위해 (AI * 1000) 값이 원료의 고유 특성과 매칭되도록 설계하라.
    3. 배합표 항목: 원료명, AI(추천%), min(하한%), max(상한%), 사용목적, 주의사항.
    4. 출력 형식은 반드시 JSON이어야 한다.
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
