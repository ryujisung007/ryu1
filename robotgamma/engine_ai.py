from __future__ import annotations
import streamlit as st
import pandas as pd
import json
from openai import OpenAI

def propose_formula_from_db(flavor: str, selected_sweeteners: list, base_type: str, db_df: pd.DataFrame):
    """
    기술사님이 제공한 CSV DB를 분석하여 1,000포인트 로직에 따라 원료를 추출합니다.
    """
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    
    # DB의 원료 요약 정보(카테고리명, 원료명 등)를 AI에게 전달하여 선택 보조
    db_summary = db_df[['카테고리', '원료명', '사용대한(min)', '사용제한(max)']].to_string()
    
    prompt = f"""
    너는 20년 경력의 'AI 시니어 식품연구원'이다. 제공된 아래 CSV 데이터(DB)를 기반으로 '{flavor}' 음료를 설계하라.
    
    [DB 데이터 요약]
    {db_summary}

    [R&D 설계 핵심 로직]
    1. 정제수를 제외한 가용 원료의 총합을 1,000포인트로 설정하라.
    2. 선택된 '{base_type}'과 '{selected_sweeteners}'의 비중에 따라 DB 내 해당 카테고리 원료를 우선 선별하라.
    3. 모든 원료의 min, max 수치는 반드시 DB에 정의된 값을 따르며, 슬라이더 제어용으로 JSON에 포함하라.
    4. 출력 형식: JSON 엄격 준수.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        st.error(f"DB 분석 엔진 에러: {e}")
        return None
