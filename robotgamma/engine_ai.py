from __future__ import annotations
import streamlit as st
import json
import hashlib
from typing import Any, Dict, List, Optional

# OpenAI 라이브러리 (환경변수에 OPENAI_API_KEY가 설정되어 있어야 합니다)
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

def get_hash(data: Any) -> str:
    return hashlib.sha256(json.dumps(data, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()[:16]

def analyze_trends(top5: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Top5 트렌드 분석 캐싱 (기존 로직 유지)"""
    key = get_hash(top5)
    if "ai_cache" not in st.session_state: st.session_state.ai_cache = {}
    if key in st.session_state.ai_cache: return st.session_state.ai_cache[key]
    result = {"summary": "천연 원료 기반의 'Healthy-Pleasure'가 핵심입니다.", "flavors": {}}
    st.session_state.ai_cache[key] = result
    return result

def propose_formula(flavor: str):
    """
    [AI 탑재] 선택한 플레이버를 기반으로 마케팅/시장성 보고서 실시간 생성
    """
    # 1. OpenAI 호출을 위한 클라이언트 설정
    if "OPENAI_API_KEY" in st.secrets:
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    else:
        client = None

    # 2. AI 분석 보고서 생성 (API 호출)
    if client:
        try:
            prompt = f"""
            너는 20년 경력의 음료 마케팅 전략가이자 식품 관능 전문가다.
            사용자가 선택한 플레이버 '{flavor}'를 기반으로 신제품 개발 전략 보고서를 작성하라.
            
            출력 형식은 반드시 아래의 JSON 구조를 지켜야 하며, 내용은 개조식으로 작성하라:
            {{
                "strategy": {{
                    "🚀 제품 포지셔닝 및 개발 컨셉": ["문장1", "문장2", "문장3"],
                    "✨ 핵심 USP 및 마케팅 전략": ["문장1", "문장2", "문장3"],
                    "⚠️ 제조 리스크 및 품질 관리(SOP)": ["문장1", "문장2", "문장3"]
                }}
            }}
            """
            # 로드 부담이 적고 빠른 o4-mini 모델 사용
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            ai_data = json.loads(response.choices[0].message.content)
            strategy = ai_data["strategy"]
        except Exception as e:
            st.warning(f"AI 분석 중 오류가 발생하여 기본 로직으로 대체합니다: {e}")
            strategy = {"보고서 생성 실패": ["API 키를 확인하거나 잠시 후 다시 시도하십시오."]}
    else:
        # API 키가 없을 때의 폴백(Fallback) 로직
        strategy = {
            "🚀 [로컬 모드] 제품 컨셉": [f"{flavor} 본연의 맛을 강조한 데일리 음료"],
            "⚠️ API 키 미설정": ["OpenAI API 키를 설정하면 실시간 AI 마케팅 분석이 활성화됩니다."]
        }

    # 3. 배합비 데이터 (이 부분은 사용자님이 주신 200여 종 리스트와 연동 가능)
    # 여기서는 예시로 기본 7종만 구성합니다.
    base_ingredients = [
        {"원재료": "정제수", "AI": 79.50, "min": 50.0, "max": 95.0, "role": "용매"},
        {"원재료": f"NFC {flavor} 과즙", "AI": 15.00, "min": 5.0, "max": 90.0, "role": "주원료"},
        {"원재료": "액상알룰로스", "AI": 4.00, "min": 1.0, "max": 15.0, "role": "감미료"},
        {"원재료": "구연산", "AI": 0.35, "min": 0.05, "max": 0.5, "role": "산미료"},
        {"원재료": f"천연{flavor}향", "AI": 0.25, "min": 0.01, "max": 0.5, "role": "착향료"},
        {"원재료": "펙틴(안정제)", "AI": 0.15, "min": 0.02, "max": 0.5, "role": "안정제"},
        {"원재료": "천연클라우드", "AI": 0.50, "min": 0.1, "max": 2.0, "role": "혼탁제"}
    ]
    
    return strategy, base_ingredients
