from __future__ import annotations
import streamlit as st

def propose_formula(flavor: str):
    """마케팅 전략(개조식) 및 원료 데이터 통합 관리"""
    # 1. 마케팅/개발 세부 전략 (AI 관여 영역)
    strategy = {
        "🚀 제품 개발 및 마케팅 전략": [
            f"• [컨셉] {flavor}의 순수성을 강조한 'Pure-Extract' 포지셔닝",
            "• [타겟] 성분 분석형 소비자(Check-sumer)를 위한 당류 0g 설계",
            "• [리스크] rPET 내열 Tg점(75~80°C)을 고려한 저온 살균/충전 공정 검토"
        ]
    }
    
    # 2. 원료 데이터 및 슬라이더 제약 조건
    # 그룹화하여 UI에서 묶어서 출력 가능
    ingredients = [
        {"name": "정제수", "val": 80.0, "min": 50.0, "max": 95.0, "unit": "%"},
        {"name": f"NFC {flavor} 과즙", "val": 15.0, "min": 5.0, "max": 90.0, "unit": "%"},
        {"name": "천연향료", "val": 0.2, "min": 0.0, "max": 1.0, "unit": "%"},
        {"name": "안정제(펙틴)", "val": 0.1, "min": 0.0, "max": 0.5, "unit": "%"},
        # ... 추가 원료들
    ]
    return strategy, ingredients
