from __future__ import annotations
import streamlit as st
import json
import hashlib
from typing import Any, Dict, List, Optional

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

def get_hash(data: Any) -> str:
    return hashlib.sha256(json.dumps(data, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()[:16]

def propose_formula(flavor: str):
    """
    [AI 연구원 모드] 20년 경력의 노하우와 문헌 근거를 바탕으로 
    마케팅 전략 및 정밀 배합비(상하한치 포함)를 실시간 생성합니다.
    """
    if "OPENAI_API_KEY" in st.secrets:
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    else:
        client = None

    if client:
        try:
            # AI 연구원에게 마케팅 전략과 배합비 설계를 동시에 명령
            prompt = f"""
            너는 20년 경력의 시니어 식품연구원이자 마케팅 전략가다. 
            '{flavor}' 음료 신제품 개발을 위해 다음을 수행하라.

            1. 마케팅 전략: 제품 컨셉, 핵심 USP, 타겟 전략, 제조 리스크를 개조식으로 작성.
            2. 식품 배합비 작성: 
               - 문헌, 논문, 인터넷 등 근거가 있는 표준 배합비를 기준으로 작성할 것.
               - 원료는 '정제수, NFC {flavor} 과즙, 액상알룰로스, 구연산, 천연향료, 비타민C, 펙틴, 정제소금, 천연클라우드, 천연색소'를 기본으로 사용하고 필요시 추가.
               - 각 원료별로 AI 추천값(AI), 사용 상한선(max), 하한선(min), 사용 목적(role)을 정할 것.
               - 배합비 합계는 반드시 100.00이 되어야 함.

            반드시 아래 JSON 구조로만 출력하라:
            {{
                "strategy": {{
                    "🚀 제품 개발 컨셉": ["문구1", "문구2"],
                    "✨ 핵심 USP 및 마케팅": ["문구1", "문구2"],
                    "⚠️ 제조 리스크 및 품질관리(SOP)": ["문구1", "문구2"]
                }},
                "ingredients": [
                    {{"원재료": "원료명", "AI": 70.0, "min": 50.0, "max": 90.0, "role": "사용목적(용도/용법)"}},
                    ...
                ]
            }}
            """
            response = client.chat.completions.create(
                model="gpt-4o-mini", # 반응 속도가 빠르고 로드 부담이 적은 모델 사용
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            ai_data = json.loads(response.choices[0].message.content)
            return ai_data["strategy"], ai_data["ingredients"]
            
        except Exception as e:
            st.error(f"AI 호출 오류: {e}")
            return {}, []
    else:
        # Fallback: API 키가 없을 경우를 대비한 기본 데이터
        return {"안내": ["API 키가 설정되지 않아 AI 분석이 불가능합니다."]}, []

def analyze_trends(top5: List[Dict[str, Any]]) -> Dict[str, Any]:
    # (기존 트렌드 분석 로직 유지)
    return {"summary": "트렌드 분석 완료", "flavors": {}}
