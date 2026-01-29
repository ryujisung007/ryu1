from __future__ import annotations
import streamlit as st
import json
import hashlib
from typing import Any, Dict, List, Optional

def get_hash(data: Any) -> str:
    """캐시 키 생성을 위한 해시 함수"""
    return hashlib.sha256(json.dumps(data, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()[:16]

def analyze_trends(top5: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Top5 플레이버 트렌드 분석 및 캐싱"""
    key = get_hash(top5)
    if "ai_cache" not in st.session_state:
        st.session_state.ai_cache = {}
    
    if key in st.session_state.ai_cache:
        return st.session_state.ai_cache[key]

    result = {
        "summary": "건강 지향적 '저당(Zero-sugar)' 및 '천연 원료(NFC)' 트렌드가 시장의 핵심 동력입니다.",
        "flavors": {}
    }
    st.session_state.ai_cache[key] = result
    return result

def propose_formula(flavor: str) -> Dict[str, Any]:
    """
    마케팅 전략 개조식 데이터 및 표준 배합비 생성.
    각 요소를 범주별로 나누어 개조식 보고가 가능하도록 구성했습니다.
    """
    try:
        # 마케팅 전략 요소 (개조식 세부 보고용)
        strategy = {
            "1. 제품 포지셔닝 및 컨셉": [
                f"프리미엄 {flavor} 본연의 산미를 강조한 'Nature-Pure' 라인 확장",
                "헬스케어에 관심이 높은 MZ세대를 겨냥한 로우칼로리 데일리 음료 포지셔닝"
            ],
            "2. 핵심 USP (Unique Selling Proposition)": [
                "NFC(비농축) 공법 적용으로 천연 풍미 및 비타민C 보존 극대화",
                "합성 감미료 배제, 알룰로스 및 스테비아를 활용한 '당류 0g' 구현",
                "환경 친화적 rPET 용기 채택 및 수분리성 라벨로 ESG 가치 실현"
            ],
            "3. 타겟 마케팅 및 유통 전략": [
                "주 타겟: 운동 후 리커버리를 중시하는 2030 오피스 워커",
                "채널 전략: 프리미엄 편의점(CVS) 신상 코너 및 새벽배송 플랫폼 선점"
            ],
            "4. 기술 리스크 및 품질 관리": [
                "천연 과즙 층 분리 방지를 위한 펙틴 배합 및 균질화(Homogenization) 압력 최적화",
                "rPET 내열 특성(Tg)에 맞춘 85~90°C Hot-fill 공정 온도 정밀 제어"
            ]
        }

        # 연구원 슬라이더용 초기 배합비 데이터
        table = [
            {"원재료": "정제수", "AI": 80.0},
            {"원재료": f"NFC {flavor} 과즙", "AI": 15.0},
            {"원재료": "액상알룰로스", "AI": 3.5},
            {"원재료": "구연산", "AI": 0.3},
            {"원재료": "천연향료", "AI": 0.3},
            {"원재료": "비타민C", "AI": 0.1},
            {"원재료": "펙틴", "AI": 0.2},
            {"원재료": "정제소금", "AI": 0.05},
            {"원재료": "천연클라우드", "AI": 0.5},
            {"원재료": "스테비아", "AI": 0.05}
        ]
        
        return {"marketing_strategy": strategy, "table": table}
    except Exception:
        return {"marketing_strategy": {}, "table": []}
