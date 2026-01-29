import streamlit as st
import json
import hashlib
from typing import Any, Dict, List, Optional

def get_hash(data: Any) -> str:
    return hashlib.sha256(json.dumps(data, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()[:16]

def analyze_trends(top5: List[Dict[str, Any]]) -> Dict[str, Any]:
    key = get_hash(top5)
    if "ai_cache" not in st.session_state:
        st.session_state.ai_cache = {}
    if key in st.session_state.ai_cache:
        return st.session_state.ai_cache[key]

    result = {
        "summary": "상큼함과 건강 지향적 로우슈거 트렌드가 지속되고 있습니다.",
        "flavors": {}
    }
    st.session_state.ai_cache[key] = result
    return result

def propose_formula(flavor: str) -> Dict[str, Any]:
    """마케팅 전략 요소 개조식 정리 및 상세 배합비 데이터"""
    try:
        result = {
            "marketing_strategy": {
                "제품컨셉": [f"프리미엄 {flavor} 본연의 맛을 구현한 'Pure Nature' 라인업", "2030 직장인을 위한 데일리 리프레시 음료"],
                "핵심USP": ["NFC 공법을 통한 영양 손실 최소화", "알룰로스 대체 공법으로 당류 0g 구현", "환경친화적 rPET 및 이지필(Easy-peel) 라벨 적용"],
                "타겟전략": ["20대: SNS 친화적 투명 패키징 및 비주얼 강조", "30대: 건강 지표(Zero-sugar) 중심의 기능성 소구"],
                "품질관리": ["과즙 침전물 방지를 위한 균질화 공정 최적화", "rPET 내열성 보강을 위한 Hot-fill 온도 정밀 제어"]
            },
            "table": [
                {"원재료": "정제수", "기존": 82.0, "AI": 80.0},
                {"원재료": f"NFC {flavor} 과즙", "기존": 10.0, "AI": 15.0},
                {"원재료": "액상알룰로스", "기존": 5.0, "AI": 4.0},
                {"원재료": "구연산", "기존": 0.3, "AI": 0.3},
                {"원재료": "천연향료", "기존": 0.2, "AI": 0.3},
                {"원재료": "비타민C", "기존": 0.1, "AI": 0.1},
                {"원재료": "펙틴", "기존": 0.2, "AI": 0.2},
                {"원재료": "정제소금", "기존": 0.05, "AI": 0.05},
                {"원재료": "천연클라우드", "기존": 1.5, "AI": 1.0},
                {"원재료": "베타카로틴", "기존": 0.65, "AI": 0.05}
            ]
        }
        return result
    except Exception:
        return {"marketing_strategy": {}, "table": []}
