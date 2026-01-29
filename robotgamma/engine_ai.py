from __future__ import annotations
import streamlit as st
import json
from openai import OpenAI

def propose_formula(flavor: str):
    """
    [AI 시니어 연구원 + 관능 전문가 협의 로직]
    1. 플레이버 선택 -> 2. 학습 데이터/트렌드 분석 -> 3. 표준 배합표(JSON) 생성
    """
    # 빠른 반응과 로드 부담이 적은 모델 설정
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    
    prompt = f"""
    너는 20년 경력의 'AI 시니어 식품연구원'이자 '식품 관능조사 전문가'이다.
    사용자가 선택한 플레이버 '{flavor}'를 바탕으로 다음 단계에 따라 표준 배합표를 작성하라.

    [단계 1] 시니어 연구원의 학습 데이터 기반 표준 배합 설계 (문헌/논문 근거)
    [단계 2] 최신 트렌드와 관능 요소(맛의 강도, 후미, 바디감) 접목
    [단계 3] 관능 전문가 협의를 통한 소비자 수용도 최적화

    [출력 요구사항]
    1. 마케팅 전략: 개조식 보고서 형태
    2. 식품 배합비 표: 
       - 원료명, AI 추천값(AI), 하한선(min), 상한선(max), 사용 목적, 용도, 용법, 사용주의사항 포함.
       - 배합비 합계는 반드시 100.00%가 되어야 함.
    
    반드시 아래 JSON 구조로만 응답하라:
    {{
        "marketing_report": {{
            "🚀 제품 포지셔닝 및 개발 컨셉": ["..."],
            "✨ 관능 전문가 협의 결과 (USP)": ["..."],
            "⚠️ 제조 리스크 및 품질관리": ["..."]
        }},
        "standard_formula": [
            {{
                "원료명": "...",
                "AI": 70.0,
                "min": 50.0,
                "max": 90.0,
                "사용목적": "...",
                "용도": "...",
                "용법": "...",
                "사용주의사항": "..."
            }}
        ]
    }}
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini", # 반응이 빠르고 효율적인 모델 사용
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        data = json.loads(response.choices[0].message.content)
        return data["marketing_report"], data["standard_formula"]
    except Exception as e:
        st.error(f"AI 엔진 호출 중 오류 발생: {e}")
        return None, None
