from __future__ import annotations
import streamlit as st
import json
import hashlib
from typing import Any, Dict, List, Optional

def get_hash(data: Any) -> str:
    return hashlib.sha256(json.dumps(data, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()[:16]

def propose_formula(flavor: str) -> Dict[str, Any]:
    """
    [로직 집중 관리] 
    이 함수 안의 데이터만 수정하면 UI 레이아웃은 유지된 채 내용만 바뀝니다.
    """
    try:
        # 1. 마케팅 전략 세부 요소 (개조식 상세 보고)
        # 마케터 및 관능 전문가 페르소나 반영
        strategy = {
            "🚀 제품 포지셔닝 및 개발 컨셉": [
                f"• {flavor} 고유의 향미 프로파일(Flavor Profile)을 극대화한 'Sensory-Pure' 라인",
                "• 무설탕/무보존료 설계를 통한 'Clean Label' 시장 선점 전략",
                "• 박사 과정 연구 및 관능 평가 데이터를 기반으로 한 소비자 수용도 최적화 컨셉"
            ],
            "✨ 핵심 USP 및 마케팅 전략": [
                "• [관능] 당산비(Brix/Acid ratio) 정밀 조정을 통한 대중적 선호도 확보",
                "• [포장] rPET 및 친환경 패키징을 강조한 '지속가능한 가치 소비' 소구",
                "• [채널] 건강 지향적 헤비 유저를 타겟으로 한 정기 구독 및 프리미엄 신선 유통"
            ],
            "⚠️ 제조 리스크 및 품질 관리(SOP)": [
                "• 원료별 수화(Hydration) 속도 차이를 고려한 투입 순서 표준화",
                "• rPET 내열 한계 온도를 준수한 살균/냉각 임계관리점(CCP) 설정",
                "• 천연 향료의 휘발 방지를 위한 냉각 후 밀폐 순환 시스템 가동"
            ]
        }

        # 2. 원료별 슬라이더 제약 조건 (상하한선 및 초기값)
        # UI 레이아웃에서 '표'와 '슬라이더'에 동시에 쓰입니다.
        formulation = [
            {"원재료": "정제수", "AI": 79.50, "min": 50.0, "max": 95.0, "role": "용매"},
            {"원재료": f"NFC {flavor} 과즙", "AI": 15.00, "min": 5.0, "max": 90.0, "role": "주원료"},
            {"원재료": "액상알룰로스", "AI": 4.00, "min": 1.0, "max": 15.0, "role": "감미료"},
            {"원재료": "구연산", "AI": 0.35, "min": 0.05, "max": 0.5, "role": "산미료"},
            {"원재료": "천연향료", "AI": 0.25, "min": 0.01, "max": 0.5, "role": "착향료"},
            {"원재료": "비타민C", "AI": 0.15, "min": 0.05, "max": 0.3, "role": "항산화제"},
            {"원재료": "펙틴", "AI": 0.15, "min": 0.02, "max": 0.5, "role": "안정제"},
            {"원재료": "정제소금", "AI": 0.05, "min": 0.01, "max": 0.1, "role": "맛 밸런스"},
            {"원재료": "천연클라우드", "AI": 0.50, "min": 0.1, "max": 2.0, "role": "혼탁제"},
            {"원재료": "천연색소", "AI": 0.05, "min": 0.01, "max": 0.2, "role": "착색료"}
        ]
        
        return {"marketing_strategy": strategy, "table": formulation}
    except Exception as e:
        return {"marketing_strategy": {}, "table": [], "error": str(e)}

def analyze_trends(top5: List[Dict[str, Any]]) -> Dict[str, Any]:
    # (생략: 기존 트렌드 분석 로직)
    return {"summary": "건강과 본질을 중시하는 트렌드가 강세입니다.", "flavors": {}}
