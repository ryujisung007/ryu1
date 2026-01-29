from __future__ import annotations
import streamlit as st
import json
from openai import OpenAI

def propose_formula_with_db(flavor: str, s_choice: list, b_type: str, db_df):
    """
    로드된 DB에서 플레이버와 가공방법에 최적화된 원료를 선별하여 배합 설계
    """
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    
    # [데이터 처리] 플레이버 관련 원료 추출
    relevant_items = db_df[db_df['원료명'].str.contains(flavor, na=False)].head(15)
    db_sample = relevant_items.to_dict(orient='records')
    
    prompt = f"""
    너는 20년 경력의 'AI 시니어 식품연구원'이다. 제공된 DB를 참고하여 '{flavor}' 음료를 설계하라.
    
    [참고 DB 원료 풀]
    {db_sample}

    [R&D 로직]
    1. 정제수 제외 원료 총합 = 1,000포인트 비중 로직 적용.
    2. 당류 {s_choice}, 가공방식 {b_type} 반영.
    3. 배합표 항목: 원료명, AI(추천%), min(하한%), max(상한%), 사용목적, 주의사항.
    4. 출력 형식: 반드시 JSON (응답 내 'json' 단어 포함 필수).
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        st.error(f"AI 시뮬레이션 엔진 에러: {e}")
        return None
