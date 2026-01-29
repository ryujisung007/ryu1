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
# 상수 (괄호 및 문자열 에러 완벽 수정)
# =========================
PACKAGING_TYPES = [
    "PET 병", "유리병", "알루미늄 캔", "종이팩", "파우치",
    "스틱 파우치", "컵형", "대용량 PET", "무균팩", "리필 파우치"
]

BEVERAGE_COMPANIES = [
    "롯데칠성음료", "코카콜라음료", "웅진식품", "동아오츠카",
    "빙그레", "매일유업", "남양유업", "CJ제일제당",
    "풀무원", "오뚜기", "하이트진로음료", "일화",
    "해태htb", "팔도", "광동제약", "대상웰라이프",
    "정식품", "샘표", "농심", "SPC삼립"
]

FLAVORS = [
    "오렌지", "사과", "포도", "망고", "레몬",
    "자몽", "복숭아", "파인애플", "딸기",
    "블루베리", "유자", "배"
]

FLAVOR_EN_MAP: Dict[str, str] = {
    "오렌지": "orange juice", "사과": "apple juice", "포도": "grape juice",
    "망고": "mango juice", "레몬": "lemon citrus drink", "자몽": "grapefruit citrus drink",
    "복숭아": "peach juice", "파인애플": "pineapple juice", "딸기": "strawberry juice",
    "블루베리": "blueberry juice", "유자": "yuzu citrus drink", "배": "pear juice"
}

# 에러 해결 포인트: 모든 키-값 쌍 뒤에 쉼표 확인 및 중괄호 } 닫기
FLAVOR_COLOR = {
    "오렌지": "#FDBA74", "사과": "#86EFAC", "포도": "#C4B5FD", "망고": "#FACC15",
    "레몬": "#FDE047", "자몽": "#FB7185", "복숭아": "#FDA4AF", "파인애플": "#FCD34D",
    "딸기": "#F87171", "블루베리": "#818CF8", "유자": "#FDE68A", "배": "#A7F3D0"
}

PRODUCT_PREFIX = ["FRESHLAB", "VITAPOP", "NATURA", "JUICY+", "FRESHWAY"]
PRODUCT_STYLE = [
    "데일리 주스", "저당 클린 드링크", "비타민 부스트", "리프레시 음료",
    "클린 주스", "이뮨 부스트", "모닝 루틴 드링크", "애프터짐 리커버리"
]

FLAVOR_WEIGHTS = {"오렌지": 0.18, "사과": 0.14, "포도": 0.12, "망고": 0.10, "레몬": 0.08}
DEFAULT_WEIGHT = 0.38 / (len(FLAVORS) - 5)

B_SCORE_ITEMS = [
    ("Company 적합성", "자사 제조/브랜드/채널 적합성", 0.20),
    ("원가 안정성", "원재료/공정 기준 원가 리스크", 0.20),
    ("제조 난이도", "기존 설비 기준 생산 용이성", 0.15),
    ("Customer 수용성", "기존 고객층과의 정합성", 0.15),
    ("반복구매 가능성", "루틴화/재구매 가능성", 0.20),
    ("차별화/확장성", "라인업/시즌/콜라보 확장", 0.10),
]

ROLE_OPTIONS = ["통합(ABC)", "A: 기획", "B: 마케팅", "C: 연구/개발"]

# =========================
# 세션 상태 초기화
# =========================
def init_state() -> None:
    defaults = {
        "seed": 0, "months": 1, "records": None, "top5": None, "selected_flavor": None,
        "step": 0, "role": "통합(ABC)",
        "ai_top5_cache": {}, "ai_a_cache": {}, "ai_b_cache": {}, "ai_c_cache": {},
        "ai_error": None, "mission_submitted": False, "mission_score": 0,
    }
    for k, v in defaults.items():
        if k not in st.session_state: st.session_state[k] = v

init_state()

# =========================
# 데이터 생성 및 유틸리티
# =========================
def get_demo_image(flavor_kr: str) -> str:
    seed = FLAVOR_EN_MAP.get(flavor_kr, "fruit-juice").replace(" ", "-")
    return f"https://picsum.photos/seed/{seed}/480/480"

def generate_fake_products(months: int, seed: int) -> List[Dict[str, Any]]:
    rng = random.Random(seed)
    today = datetime.today()
    recs = []
    for _ in range(months * 300):
        flavor = rng.choices(FLAVORS, weights=[FLAVOR_WEIGHTS.get(f, DEFAULT_WEIGHT) for f in FLAVORS])[0]
        recs.append({
            "보고일자": (today - timedelta(days=rng.randint(0, 30))).strftime("%Y-%m-%d"),
            "제품명": f"{rng.choice(PRODUCT_PREFIX)} {flavor} {rng.choice(PRODUCT_STYLE)}",
            "플레이버": flavor, "제품유형": "주스류",
            "포장": rng.choice(PACKAGING_TYPES), "음료제조회사": rng.choice(BEVERAGE_COMPANIES),
        })
    return recs

def calculate_top5_flavors(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    cnts = Counter(r["플레이버"] for r in records)
    tot = sum(cnts.values()) or 1
    return [{"rank": i, "flavor": f, "count": c, "share": round(c/tot*100, 1)} 
            for i, (f, c) in enumerate(cnts.most_common(5), 1)]

# =========================
# 메인 UI
# =========================
st.title("🥤 ABC 제품개발 교육 시뮬레이터")

# 사이드바 설정
st.sidebar.header("R&D 설정")
st.session_state.role = st.sidebar.radio("직무 모드", ROLE_OPTIONS, index=ROLE_OPTIONS.index(st.session_state.role))
st.session_state.months = st.sidebar.number_input("조회 개월 수", 1, 6, st.session_state.months)

if st.sidebar.button("▶ 데이터 시뮬레이션 실행", use_container_width=True):
    st.session_state.seed = random.randint(1, 999999)
    st.session_state.records = generate_fake_products(st.session_state.months, st.session_state.seed)
    st.session_state.top5 = calculate_top5_flavors(st.session_state.records)
    st.session_state.selected_flavor = None

# 데이터 출력 영역
if st.session_state.records:
    st.subheader("📋 제품 트렌드 데이터")
    st.dataframe(st.session_state.records, use_container_width=True, height=300)

    st.divider()
    st.subheader("🔥 시장 Top5 플레이버 분석")
    cols = st.columns(5)
    for i, t in enumerate(st.session_state.top5):
        with cols[i]:
            st.image(get_demo_image(t['flavor']), use_container_width=True)
            st.markdown(f"**{t['flavor']}** ({t['share']}%)")
            if st.button(f"{t['flavor']} 기획하기", key=f"sel_{t['flavor']}"):
                st.session_state.selected_flavor = t['flavor']
                st.balloons()
