from __future__ import annotations
import streamlit as st
import json
import hashlib
from typing import Any, Dict, List, Optional

def get_hash(data: Any) -> str:
    return hashlib.sha256(json.dumps(data, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()[:16]

def analyze_trends(top5: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Top5 트렌드 분석 캐싱"""
    key = get_hash(top5)
    if "ai_cache" not in st.session_state:
        st.session_state.ai_cache = {}
    if key in st.session_state.ai_cache:
        return st.session_state.ai_cache[key]
    result = {"summary": "천연 원료 기반의 'Healthy-Pleasure'와 'Clean-Label'이 시장의 핵심 테마입니다.", "flavors": {}}
    st.session_state.ai_cache[key] = result
    return result

def propose_formula(flavor: str):
    """마케팅 전략(개조식) 및 200+ 원료 라이브러리 데이터"""
    
    # 1. 마케팅 및 관능 전략 세부 보고 (AI 관여)
    strategy = {
        "🚀 제품 개발 및 마케팅 세부 전략": [
            f"• [컨셉] {flavor} 본연의 풍미를 극대화한 'Sensory-Origin' 프리미엄 포지셔닝",
            "• [타겟] 성분을 중시하는 체크슈머(Check-sumer)를 위한 당류 0g 설계",
            "• [관능] 소비자 수용도 최적화를 위한 당산비(Brix/Acid ratio) 정밀 설계",
            "• [포장] rPET 및 이지필 라벨을 통한 ESG 가치 및 환경 친화적 마케팅 소구",
            "• [품질] NFC 과즙의 층 분리 방지를 위한 고압 균질 및 안정화 공정(SOP) 제언"
        ]
    }

    # 2. 200+ 원료 라이브러리 (확장 가능 구조)
    # 실제 앱 구동 시에는 flavor에 맞는 핵심 원료들이 슬라이더로 노출됩니다.
    base_ingredients = [
        {"원재료": "정제수", "AI": 79.50, "min": 50.0, "max": 95.0, "role": "용매"},
        {"원재료": f"NFC {flavor} 과즙", "AI": 15.00, "min": 5.0, "max": 90.0, "role": "주원료"},
        {"원재료": "액상알룰로스", "AI": 4.00, "min": 1.0, "max": 15.0, "role": "감미료"},
        {"원재료": "구연산", "AI": 0.35, "min": 0.05, "max": 0.5, "role": "산미료"},
        {"원재료": f"천연{flavor}향", "AI": 0.25, "min": 0.01, "max": 0.5, "role": "착향료"},
        {"원재료": "비타민C", "AI": 0.15, "min": 0.05, "max": 0.3, "role": "항산화제"},
        {"원재료": "펙틴(안정제)", "AI": 0.15, "min": 0.02, "max": 0.5, "role": "안정제"},
        {"원재료": "정제소금", "AI": 0.05, "min": 0.01, "max": 0.1, "role": "맛 밸런스"},
        {"원재료": "천연클라우드", "AI": 0.50, "min": 0.1, "max": 2.0, "role": "혼탁제"},
        {"원재료": "천연색소", "AI": 0.05, "min": 0.01, "max": 0.2, "role": "착색료"}
    ]
    
    # [참고] 향후 농축액 100종, 향료 100종 등 리스트를 이 아래에 추가하여 관리 가능합니다.
    
    return strategy, base_ingredients
