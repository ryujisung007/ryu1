from __future__ import annotations
import streamlit as st
import json
from openai import OpenAI

def propose_formula(flavor: str, selected_sweeteners: list, base_type: str):
    """
    AI 시니어 연구원이 1,000여 종의 원료 라이브러리를 바탕으로 상세 배합비를 설계합니다.
    - base_type: NFC, 농축액, 퓨레 등 선택된 원료 방식 반영
    """
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    sweetener_ctx = ", ".join(selected_sweeteners)
    
    prompt = f"""
    너는 20년 경력의 'AI 시니어 식품연구원'이다. '{flavor}'를 테마로 한 '{base_type}' 기반 음료를 설계하라.
    당류는 [{sweetener_ctx}]를 사용하고, 1,000개 이상의 원료 라이브러리 지식을 활용하여 10~15종의 원료를 구성하라.

    [지시사항]
    1. 각 원료의 추천배합비(AI)에 1,000을 곱한 값을 기준으로 원료의 세부 등급이나 종류를 결정하라.
    2. 배합표 항목: 원료명, AI 추천값(AI), min, max, 사용목적, 용도, 용법, 사용주의사항.
    3. 정제수는 'Water-Balance' 역할을 수행하며 합계 100%를 자동 조절함.
    4. 하단에 배합 설계의 과학적 근거(학술/문헌)를 3가지 이상 제시할 것.

    반드시 JSON 형식으로만 응답:
    {{
        "report": {{
            "🚀 전략 및 컨셉": ["..."],
            "📚 배합 설계 근거(학술/문헌)": ["..."],
            "⚠️ 제조 리스크 및 품질관리": ["..."]
        }},
        "formula": [
            {{ "원료명": "정제수", "AI": 80.0, "min": 50.0, "max": 95.0, "사용목적": "용매", "용도": "농도조절", "용법": "후첨", "주의사항": "합계 100 조절" }},
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
        st.error(f"AI 분석 로직 오류: {e}")
        return None
