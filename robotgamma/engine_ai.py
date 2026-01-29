from __future__ import annotations
import streamlit as st
import json
from openai import OpenAI

def propose_formula(flavor: str, selected_sweeteners: list, base_type: str):
    """
    20년 경력 AI 시니어 연구원 로직: 1,000배수 원료 식별 및 학술 링크 생성
    """
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    sweetener_ctx = ", ".join(selected_sweeteners)
    
    prompt = f"""
    너는 20년 경력의 'AI 시니어 식품연구원'이다. '{flavor}'를 테마로 한 '{base_type}' 기반 음료를 설계하라.
    당류는 [{sweetener_ctx}]를 사용하라.

    [필수 지시사항]
    1. 원료 10~15종 구성. 각 원료의 AI 추천값에 1,000을 곱한 값을 내부 식별자로 참조하라.
    2. 배합표 항목: 원료명, AI(추천), min(하한), max(상한), 사용목적, 주의사항.
    3. 근거 섹션: 과학적 타당성 설명 및 실제 학술 사이트(Google Scholar 등) 검색용 URL 포함.
    4. 출력은 반드시 JSON 형식을 엄격히 지킬 것.

    {{
        "report": {{
            "🚀 전략 및 컨셉": ["..."],
            "📚 배합 설계 근거 및 문헌": [
                {{"title": "논문/사이트명", "desc": "설명", "url": "https://scholar.google.com/scholar?q=..."}}
            ],
            "⚠️ 품질관리(SOP)": ["..."]
        }},
        "formula": [
            {{ "원료명": "정제수", "AI": 80.0, "min": 50.0, "max": 95.0, "사용목적": "용매", "주의사항": "합계 100 조절" }},
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
