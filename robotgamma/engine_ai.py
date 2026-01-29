import streamlit as st
import json
import hashlib
from typing import Any, Dict, List, Optional

# 해시 생성 함수 (캐시 키로 활용)
def get_hash(data: Any) -> str:
    return hashlib.sha256(json.dumps(data, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()[:16]

# JSON 파싱 안전 장치
def safe_json_loads(text: str) -> Optional[Dict[str, Any]]:
    try:
        start, end = text.find("{"), text.rfind("}")
        return json.loads(text[start:end + 1]) if start != -1 else None
    except:
        return None

# AI 분석 메인 함수 (Top5 트렌드 분석)
def analyze_trends(top5: List[Dict[str, Any]]) -> Dict[str, Any]:
    key = get_hash(top5)
    
    # 캐시 확인 (불필요한 API 호출 방지)
    if "ai_cache" not in st.session_state:
        st.session_state.ai_cache = {}
    if key in st.session_state.ai_cache:
        return st.session_state.ai_cache[key]

    try:
        from openai import OpenAI
        client = OpenAI() # Streamlit secrets 사용
        
        prompt = f"음료 트렌드 전문가로서 다음 데이터를 분석해 JSON으로만 응답해: {json.dumps(top5, ensure_ascii=False)}"
        # 실제 호출 로직 (생략: 이전 코드와 동일)
        # result = client.chat.completions.create(...)
        result = {"summary": "AI 분석 결과 샘플", "flavors": {}} # 예시
        
        st.session_state.ai_cache[key] = result
        return result
    except Exception as e:
        # 오류 발생 시 로컬 폴백 데이터 반환
        return {
            "summary": "기본 트렌드 분석 모드입니다. 상큼하고 건강한 원료가 대세입니다.",
            "flavors": {}
        }

# 배합비 제안 함수
def propose_formula(flavor: str) -> Dict[str, Any]:
    # 기존 코드의 local_formula 로직을 이쪽으로 이동하여 구현
    pass
