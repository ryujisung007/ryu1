from __future__ import annotations
import streamlit as st
import json
from openai import OpenAI

def propose_formula(flavor: str, selected_sweeteners: list):
    """AI 시니어 연구원이 문헌 근거로 배합비 및 전략 생성"""
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    sweetener_context = ", ".join(selected_sweeteners)
    
    prompt = f"""
    너는 20년 경력의 시니어 식품연구원이다. '{flavor}' 음료의 표준 배합비를 작성하라.
    당류는 [{sweetener_context}]를 중심으로 설계하고, 반드시 합계 100%가 되도록 하라.
    원료에는 '정제수'를 반드시 포함하고 사용목적을 '용매'로 설정하라.
    
    반드시 아래 JSON 형식으로만 응답:
    {{
        "report": {{
            "🚀 마케팅 및 개발 컨셉": ["..."],
            "📚 배합 설계 근거(학술/문헌)": ["..."],
            "⚠️ 제조 리스크 및 품질관리": ["..."]
        }},
        "formula": [
            {{ "원료명": "정제수", "AI": 80.0, "min": 50.0, "max": 95.0, "사용목적": "용매", "주의사항": "최종 100 조절" }},
            ...
        ]
    }}
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        st.error(f"AI 분석 오류: {e}")
        return None
