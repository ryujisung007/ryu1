from __future__ import annotations
import streamlit as st
import json
import hashlib
from typing import Any, Dict, List, Optional

def get_hash(data: Any) -> str:
    """캐시용 해시 생성"""
    return hashlib.sha256(json.dumps(data, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()[:16]

def analyze_trends(top5: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Top5 트렌드 분석 및 캐싱"""
    key = get_hash(top5)
    if "ai_cache" not in st.session_state:
        st.session_state.ai_cache = {}
    
    if key in st.session_state.ai_cache:
        return st.session_state.ai_cache[key]

    result = {
        "summary": "상큼함과 건강 지향적 '제로슈거' 트렌드가 시장을 주도하고 있습니다.",
        "flavors": {}
    }
    st.session_state.ai_cache[key] = result
    return result

def propose_formula(flavor: str) -> Dict[str, Any]:
    """
    마케팅 전략 개조식 데이터 및 표준 배합비 생성.
    연구원 배합비 수정 슬라이더의 초기값으로 활용됩니다.
    """
    try:
        # 마케팅 전략 요소 (개조식 보고용)
        strategy = {
            "1. 제품 컨셉 전략": [
                f"프리미엄 {flavor} 본연의 풍미를 극대화한 'Pure-Squeeze' 라인업",
                "바쁜 현대인을 위한 저칼로리 데일리 리프레시 음료"
            ],
            "2. 핵심 USP (Unique Selling Proposition)": [
                "NFC(비농축과즙) 공법 적용으로 천연 영양소 파괴 최소화",
                "천연 감미료(알룰로스, 스테비아) 배합을 통한 당류 0g 구현",
                "환경 친화적 rPET 용기 및 수분리성 라벨 적용 (포장기술사 권고)"
            ],
            "3. 타겟팅 및 채널 전략": [
                "메인 타겟: 2030 오피스 워커 및 헬스케어 관심층",
                "핵심 채널: 편의점(CVS) 및 온라인 신선 배송 플랫폼 전용"
            ],
            "4. 제조 및 품질 관리 리스크": [
                "NFC 과즙 특유의 침전 발생 제어를 위한 균질화(Homogenization) 공정 강화",
                "rPET 내열 특성(Tg)을 고려한 충전 온도(Hot-fill) 정밀 모니터링"
            ]
        }

        # 초기 배합비 데이터
        table = [
            {"원재료": "정제수", "기존": 82.0, "AI":
