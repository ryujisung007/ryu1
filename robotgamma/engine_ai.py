from __future__ import annotations
import streamlit as st
import json
from openai import OpenAI

def propose_formula(flavor: str, selected_sweeteners: list, base_type: str):
    """
    AI 시니어 연구원이 1,000여 종의 라이브러리를 기반으로 배합 설계
    - flavor: 선택된 플레이버
    - selected_sweeteners: 선택된 당류 리스트
    - base_type: NFC, 농축액 등 가공 방식
    """
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    sweetener_ctx = ", ".join(selected_sweeteners)
    
    prompt = f"""
    너는 20년 경력의 'AI 시니어 식품연구원'이다. '{flavor}'를 테마로 한 '{base_type}' 기반 음료를 설계하라.
    당류는 [{sweetener_ctx}]를 사용하고, 1,000개 이상의 원료 라이브러리 지식을 활용하라.

    [요구사항]
    1. 원료 10종 이상 구성 (정제수 필수).
    2. 배합표 항목: 원료명, AI 추천값(AI), min, max, 사용목적, 용도, 용법, 사용주의사항.
    3. 정제수는 합계 100%를 조절하는 Water-Balance 역할.
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
