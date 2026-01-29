from __future__ import annotations
import streamlit as st
import pandas as pd
import json
from openai import OpenAI

def propose_formula_with_flavor_db(flavor: str, s_choice: list, b_type: str, db_df: pd.DataFrame):
    """
    AI 시니어 연구원: 플레이버에 최적화된 원료를 DB에서 선별하여 1,000포인트 로직으로 배합
    """
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    
    # 1. 플레이버와 가공방식에 매칭되는 DB 필터링 (속도 최적화)
    # DB에 '원료명' 또는 '카테고리' 컬럼이 있다고 가정
    relevant_db = db_df[db_df['원료명'].str.contains(flavor, na=False) | 
                        db_df['카테고리'].str.contains(b_type, na=False)].head(20)
    db_context = relevant_db.to_string()
    
    prompt = f"""
    너는 20년 경력의 'AI 시니어 식품연구원'이다. 제공된 DB 조각을 기반으로 '{flavor}' 음료를 설계하라.
    
    [R&D 설계 로직]
    1. 정제수 제외 원료 총합 = 1,000포인트.
    2. 각 원료 비중(%)에 따라 제공된 DB 리스트 내에서 최적 원료 종류를 확정하라.
    3. 배합표 항목: 원료명, AI(추천%), min(하한%), max(상한%), 사용목적, 주의사항.
    4. 근거 섹션: 국내 DBpia, RISS의 실제 논문 검색 쿼리를 제목으로 포함하라.
    5. 출력: 반드시 JSON 형식을 엄격히 지킬 것.
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
