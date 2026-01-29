from __future__ import annotations
import streamlit as st
import json
from openai import OpenAI

def propose_formula(flavor: str, selected_sweeteners: list):
    """
    AI 시니어 연구원이 문헌 근거로 배합비 및 전략 생성
    - selected_sweeteners: 사용자가 선택한 당류 리스트 반영
    """
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    
    # 당류 선택에 따른 프롬프트 동적 구성
    sweetener_context = ", ".join(selected_sweeteners)
    
    prompt = f"""
    너는 20년 경력의 'AI 시니어 식품연구원'이다. '{flavor}' 음료의 표준 배합비를 작성하라.
    특히 당류는 사용자가 선택한 [{sweetener_context}]를 중심으로 설계하라.
    
    [지시사항]
    1. 배합 근거: 식품공전 및 학술 논문 근거를 '📚 배합 설계 근거' 섹션에 3가지 이상 포함할 것.
    2. 원료 구성: 정제수(용매), {flavor}농축액, 선택된 당류({sweetener_context}), 산미료, 향료, 안정제 등 10개 내외.
    3. 정제수는 합계 100% 조절용(Water-Balance)으로 설정하고 min 함량을 반드시 명시할 것.
    4. 각 원료별로 AI 추천값(AI), min(하한), max(상한), 사용목적, 사용주의사항을 포함할 것.
    
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
        data = json.loads(response.choices[0].message.content)
        return data["report"], data["formula"]
    except Exception as e:
        st.error(f"AI 시뮬레이션 오류: {e}")
        return None, None

def analyze_trends(top5):
    # 트렌드 분석 로직 (캐싱 적용)
    return {"summary": "건강 지향적 저당 음료 트렌드 지속 중"}
