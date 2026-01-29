"""
ABC 제품개발 교육용 Streamlit 앱
안정 레이아웃 + 빈 상태 UX + 진행 단계 표시 적용
"""

from __future__ import annotations

import json
import random
import hashlib
from collections import Counter
from datetime import datetime, timedelta
from typing import Any, Dict, List

import streamlit as st


# =========================
# 기본 설정
# =========================
st.set_page_config(page_title="ABC 제품개발 교육 시뮬레이터", layout="wide")


# =========================
# 상수 정의
# =========================
FLAVORS = [
    "오렌지", "사과", "포도", "망고", "레몬",
    "자몽", "복숭아", "파인애플", "딸기",
    "블루베리", "유자", "배"
]

PACKAGING_TYPES = [
    "PET 병", "유리병", "알루미늄 캔", "종이팩",
    "무균팩", "파우치", "리필 파우치"
]

BEVERAGE_COMPANIES = [
    "롯데칠성음료", "코카콜라음료", "웅진식품", "동아오츠카",
    "빙그레", "매일유업", "CJ제일제당", "풀무원",
    "광동제약", "하이트진로음료", "팔도", "일화"
]

PRODUCT_PREFIX = ["FRESHLAB", "VITAPOP", "NATURA", "JUICY+", "FRESHWAY"]
PRODUCT_STYLE = ["데일리 주스", "저당 클린 드링크", "비타민 부스트", "리프레시 음료"]


# =========================
# 세션 상태 초기화
# =========================
def init_state():
    defaults = {
        "records": None,
        "top5": None,
        "selected_flavor": None,
        "step": 0,  # 0: 미실행, 1: 데이터, 2: 플레이버 선택, 3: 컨셉/배합
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


init_state()


# =========================
# 유틸 함수
# =========================
def random_product_name(flavor: str) -> str:
    brand = random.choice(PRODUCT_PREFIX)
    style = random.choice(PRODUCT_STYLE)
    if random.random() < 0.35:
        other = random.choice([f for f in FLAVORS if f != flavor])
        name = f"{flavor}·{other}"
    else:
        name = flavor
    return f"{brand} {name} {style}"


def get_demo_image(flavor: str) -> str:
    return f"https://picsum.photos/seed/{flavor}/420/420"


def generate_fake_products(months: int) -> List[Dict[str, Any]]:
    today = datetime.today()
    records = []
    for _ in range(months):
        for _ in range(300):
            flavor = random.choice(FLAVORS)
            records.append({
                "보고일자": (today - timedelta(days=random.randint(0, 30))).strftime("%Y-%m-%d"),
                "제품명": random_product_name(flavor),
                "플레이버": flavor,
                "제품유형": "주스류",
                "포장": random.choice(PACKAGING_TYPES),
                "음료제조회사": random.choice(BEVERAGE_COMPANIES),
            })
    return records


def calculate_top5(records):
    c = Counter(r["플레이버"] for r in records)
    total = sum(c.values()) or 1
    return [{"flavor": f, "share": round(cnt / total * 100, 1)} for f, cnt in c.most_common(5)]


# =========================
# UI: 타이틀 & 진행 단계
# =========================
st.title("🥤 ABC 제품개발 교육 시뮬레이터")
st.caption("데이터 → 트렌드 → 컨셉/배합 → 제조공정 이해")

steps = ["① 데이터 생성", "② 플레이버 선택", "③ 컨셉·배합 설계", "④ 제조공정 미션"]
cols = st.columns(4)
for i, (col, label) in enumerate(zip(cols, steps), start=1):
    with col:
        if st.session_state.step >= i:
            st.success(label)
        else:
            st.info(label)


# =========================
# Sidebar
# =========================
st.sidebar.header("조건 설정")
months = st.sidebar.slider("조회 개월 수", 1, 6, 1)
run = st.sidebar.button("▶ 실행")

if run:
    records = generate_fake_products(months)
    st.session_state.records = records
    st.session_state.top5 = calculate_top5(records)
    st.session_state.selected_flavor = None
    st.session_state.step = 1


records = st.session_state.records
top5 = st.session_state.top5


# =========================
# (4) 품목제조보고 테이블
# =========================
st.subheader("📋 음료류 품목제조보고")

if records:
    st.dataframe(records, use_container_width=True, height=320)
else:
    st.info("좌측에서 조건을 설정하고 실행하면 데이터가 생성됩니다.")

st.divider()


# =========================
# (1) Top5 플레이버 카드
# =========================
st.subheader("🔥 Top5 플레이버")

if not top5:
    st.info("데이터 생성 후 Top5 플레이버가 표시됩니다.")
else:
    cols = st.columns(5)
    for col, t in zip(cols, top5):
        f = t["flavor"]
        selected = (st.session_state.selected_flavor == f)
        with col:
            st.image(get_demo_image(f), use_container_width=True)
            st.markdown(f"**{f}**")
            st.caption(f"점유율 {t['share']}%")

            if selected:
                st.success("선택됨")
            else:
                if st.button("이 맛으로 기획", key=f"pick_{f}"):
                    st.session_state.selected_flavor = f
                    st.session_state.step = 2

st.divider()


# =========================
# (2) 좌/우 분할: 컨셉 / 배합비
# =========================
st.subheader("🧠🧪 AI 신규 제품 제안 & 배합비 설계")

if not st.session_state.selected_flavor:
    st.info("Top5 플레이버 중 하나를 선택하면 컨셉과 배합비가 표시됩니다.")
else:
    st.session_state.step = 3
    left, right = st.columns(2)

    with left:
        st.markdown(f"### 🧠 제품 컨셉 – {st.session_state.selected_flavor}")
        st.write("- 데일리 음용에 적합한 상큼한 포지션")
        st.write("- 저당/클린 트렌드 반영")
        st.write("- 20~30대 타깃 반복구매 설계")

    with right:
        st.markdown("### 🧪 배합비(예시)")
        st.dataframe([
            {"원재료": "정제수", "기존": 83.0, "AI A": 80.0, "AI B": 81.0},
            {"원재료": "과즙", "기존": 10.0, "AI A": 12.0, "AI B": 13.0},
            {"원재료": "설탕", "기존": 5.0, "AI A": 3.0, "AI B": 4.0},
            {"원재료": "기타", "기존": 2.0, "AI A": 5.0, "AI B": 2.0},
        ], use_container_width=True)

st.divider()


# =========================
# (3) 제조공정 미션
# =========================
st.subheader("🎯 신입사원 제조공정 미션")

st.markdown("**문제**. NFC 과즙 음료의 올바른 공정 순서는?")
answer = st.radio(
    "선택",
    ["원료계량 → 살균 → 혼합 → 충전",
     "원료계량 → 혼합 → 살균 → 충전",
     "혼합 → 충전 → 살균 → 냉각"]
)

if st.button("정답 확인"):
    if answer == "원료계량 → 혼합 → 살균 → 충전":
        st.success("정답입니다. 혼합 후 살균이 기본 공정입니다.")
    else:
        st.error("오답입니다. 공정 흐름을 다시 확인하세요.")

st.caption("※ 교육용 미션: 공정 흐름·품질·포장 연계를 이해하는 것이 목표입니다.")
