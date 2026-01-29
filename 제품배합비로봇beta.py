from __future__ import annotations

import json
import random
import hashlib
import time
from collections import Counter
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import streamlit as st
import matplotlib.pyplot as plt

# =========================
# 기본 설정
# =========================
st.set_page_config(page_title="ABC 제품개발 교육 시뮬레이터", layout="wide")

# =========================
# 상수 (에러 완벽 수정)
# =========================
PACKAGING_TYPES = ["PET 병", "유리병", "알루미늄 캔", "종이팩", "파우치"]
BEVERAGE_COMPANIES = ["롯데칠성음료", "코카콜라음료", "웅진식품", "동아오츠카", "빙그레"]
FLAVORS = ["오렌지", "사과", "포도", "망고", "레몬", "자몽", "복숭아"]
FLAVOR_EN_MAP = {"오렌지": "orange", "사과": "apple", "포도": "grape", "망고": "mango"}
FLAVOR_COLOR = {"오렌지": "#FDBA74", "사과": "#86EFAC", "포도": "#C4B5FD", "망고": "#FACC15"}
PRODUCT_PREFIX = ["FRESHLAB", "VITAPOP", "NATURA"]
PRODUCT_STYLE = ["데일리 주스", "저당 클린 드링크", "비타민 부스트"]

# =========================
# 세션 상태 초기화
# =========================
if "records" not in st.session_state:
    st.session_state.records = None
if "selected_flavor" not in st.session_state:
    st.session_state.selected_flavor = None

# =========================
# UI 영역
# =========================
st.title("🥤 ABC 제품개발 교육 시뮬레이터")

# 사이드바 실행 버튼
if st.sidebar.button("▶ 데이터 시뮬레이션 실행"):
    # 1. 진행도 표시
    progress_text = "데이터 수집 및 공정 시뮬레이션 중..."
    my_bar = st.progress(0, text=progress_text)
    
    for percent_complete in range(100):
        time.sleep(0.01) # 실제로는 여기서 데이터 생성 로직 수행
        my_bar.progress(percent_complete + 1, text=progress_text)
    
    # 데이터 생성 (가시화 예시)
    st.session_state.records = [{"제품명": "샘플", "플레이버": "오렌지"}]
    
    # 2. 완료 신호
    my_bar.empty() # 진행바 제거
    st.toast('데이터 시뮬레이션이 성공적으로 완료되었습니다!', icon='✅')
    st.success('데이터 로드 완료!')

# 분석 선택 영역
if st.session_state.records:
    st.subheader("🔥 분석할 플레이버를 선택하세요")
    pick = st.selectbox("플레이버 선택", FLAVORS)
    
    if st.button("기획안 생성 시작"):
        with st.spinner('AI 연구원이 컨셉과 배합비를 도출하고 있습니다...'):
            time.sleep(1.5) # AI 처리 시간 시뮬레이션
            st.session_state.selected_flavor = pick
        
        # 3. 끝남을 알리는 시각적 신호
        st.balloons() 
        st.success(f"🎊 {pick} 제품 기획안 작성이 완료되었습니다! 아래 탭에서 확인하세요.")
