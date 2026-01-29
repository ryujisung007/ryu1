from __future__ import annotations
import streamlit as st
import json
import hashlib
from typing import Any, Dict, List, Optional

def get_hash(data: Any) -> str:
    return hashlib.sha256(json.dumps(data, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()[:16]

def analyze_trends(top5: List[Dict[str, Any]]) -> Dict[str, Any]:
    key = get_hash(top5)
    if "ai_cache" not in st.session_state: st.session_state.ai_cache = {}
    if key in st.session_state.ai_cache: return st.session_state.ai_cache[key]
    result = {"summary": "천연 원료 기반의 'Healthy-Pleasure'가 시장의 핵심 테마입니다.", "flavors": {}}
    st.session_state.ai_cache[key] = result
    return result

def propose_formula(flavor: str):
    """마케팅 전략 및 원료 라이브러리"""
    strategy = {
        "🚀 제품 R&D 및 마케팅 전략": [
            f"• [컨셉] {flavor} 본연의 풍미를 극대화한 'Sensory-Origin' 설계",
            "• [관능] 소비자 수용도 최적화를 위한 당산비(Brix/Acid) 정밀 조정",
            "• [포장] rPET 및 이지필 라벨을 통한 ESG 가치 마케팅 소구"
        ]
    }
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
