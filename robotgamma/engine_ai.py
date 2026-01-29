import streamlit as st
import json
import hashlib
from typing import Any, Dict, List, Optional

def get_hash(data: Any) -> str:
    """캐시용 해시 생성"""
    return hashlib.sha256(json.dumps(data, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()[:16]

def safe_json_loads(text: str) -> Optional[Dict[str, Any]]:
    """불완전한 JSON 텍스트 보정 및 파싱"""
    try:
        start, end = text.find("{"), text.rfind("}")
        return json.loads(text[start:end + 1]) if start != -1 else None
    except:
        return None

def analyze_trends(top5: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Top5 트렌드 분석 및 캐싱"""
    key = get_hash(top5)
    if "ai_cache" not in st.session_state:
        st.session_state.ai_cache = {}
    
    if key in st.session_state.ai_cache:
        return st.session_state.ai_cache[key]

    # 기본 결과 구조 (API 미연결 시 폴백)
    result = {
        "summary": "상큼함과 건강 지향적 로우슈거 트렌드가 지속되고 있습니다.",
        "flavors": {}
    }
    
    # 실제 OpenAI 연동 시 이 부분에서 로직 수행
    st.session_state.ai_cache[key] = result
    return result

def propose_formula(flavor: str) -> Dict[str, Any]:
    """
    배합비 산출 함수: 항상 유효한 딕셔너리를 반환하여 AttributeError 방지.
    기존배합비 대비 AI 제안(A/B)을 비교 형식으로 생성합니다.
    """
    try:
        # 교육용 표준 배합비 데이터 구성
        result = {
            "concept": f"{flavor} 본연의 풍미를 극대화한 '클린 라벨' 및 '저당' 설계 전략",
            "table": [
                {"원재료": "정제수", "기존배합비(%)": 82.0, "AI제안A(%)": 80.0, "AI제안B(%)": 78.0},
                {"원재료": f"NFC {flavor} 과즙", "기존배합비(%)": 10.0, "AI제안A(%)": 12.0, "AI제안B(%)": 15.0},
                {"원재료": "액상알룰로스", "기존배합비(%)": 5.0, "AI제안A(%)": 6.0, "AI제안B(%)": 4.0},
                {"원재료": "구연산", "기존배합비(%)": 0.3, "AI제안A(%)": 0.3, "AI제안B(%)": 0.4},
                {"원재료": "천연향료", "기존배합비(%)": 0.2, "AI제안A(%)": 0.3, "AI제안B(%)": 0.3},
                {"원재료": "비타민C", "기존배합비(%)": 0.1, "AI제안A(%)": 0.1, "AI제안B(%)": 0.1},
                {"원재료": "펙틴", "기존배합비(%)": 0.2, "AI제안A(%)": 0.2, "AI제안B(%)": 0.2},
                {"원재료": "정제소금", "기존배합비(%)": 0.05, "AI제안A(%)": 0.05, "AI제안B(%)": 0.05},
                {"원재료": "천연클라우드", "기존배합비(%)": 1.5, "AI제안A(%)": 1.0, "AI제안B(%)": 1.8},
                {"원재료": "베타카로틴", "기존배합비(%)": 0.65, "AI제안A(%)": 0.05, "AI제안B(%)": 0.1}
            ]
        }
        return result
    except Exception:
        # 오류 시에도 빈 구조를 반환하여 UI 충돌 방지
        return {"concept": "배합비를 산출할 수 없습니다.", "table": []}
