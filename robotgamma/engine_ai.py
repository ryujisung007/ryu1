from __future__ import annotations
import streamlit as st
import json
from openai import OpenAI

def propose_formula(flavor: str, selected_sweeteners: list, base_type: str):
    """
    AI 시니어 연구원이 1,000여 종의 라이브러리를 기반으로 배합 설계
    """
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    sweetener_ctx = ", ".join(selected_sweeteners)
    
    # [에러 해결]: 'json' 단어를 프롬프트에 명시적으로 포함
    prompt = f"""
    너는 20년 경력의 'AI 시니어 식품연구원'이다. '{flavor}'를 테마로 한 '{base_type}' 기반 음료를 설계하라.
    당류는 [{sweetener_ctx}]를 사용하고, 1,000개 이상의 원료 라이브러리 지식을 활용하라.

    [요구사항]
    1. 배합 설계 시 각 원료의 추천 비율에 1,000을 곱한 고유 식별값을 참조하여 원료 등급을 정하라.
    2. 배합표 항목: 원료명, AI 추천값(AI), min(하한), max(상한), 사용목적, 용도, 용법, 사용주의사항.
    3. 정제수는 합계 100%를 조절하는 Water-Balance 역할로 설정하라.
    4. 출력 형식은 반드시 아래의 **JSON** 구조를 엄격히 지켜야 한다:

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
        st.error(f"AI 분석 엔진 에러: {e}")
        return None
