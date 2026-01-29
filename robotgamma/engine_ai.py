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
    OpenAI 모델(o4-mini 등) 호출 시에도 이 구조를 표준으로 사용합니다.
    """
    try:
        # 마케팅 전략 요소 (개조식 보고용 데이터 구조)
        strategy = {
            "1. 신제품 컨셉 및 포지셔닝": [
                f"프리미엄 {flavor} 본연의 산미를 강조한 'Nature-Pure' 라인",
                "헬스케어에 관심이 높은 MZ세대를 겨냥한 로우칼로리 데일리 음료"
            ],
            "2. 핵심 USP (차별화 포인트)": [
                "NFC(비농축) 과즙 공법으로 원료의 풍미와 영양소 보존 극대화",
                "합성 감미료 대신 알룰로스 및 스테비아를 사용한 클린 라벨 구현",
                "포장기술사 관점의 재활용 용이성 1등급 rPET 용기 채택"
            ],
            "3. 타겟팅 및 유통 전략": [
                "타겟: 운동 후 리커버리 음료를 찾는 2030 오피스 워커",
                "채널: 대형 편의점 신상 코너 및 컬리/쿠팡 등 프리미엄 온라인몰"
            ],
            "4. 기술적 리스크 및 대응방안": [
                "천연 과즙의 층 분리 현상 방지를 위한 안정제(펙
