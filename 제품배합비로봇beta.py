"""
ABC 제품개발 교육용 Streamlit 앱
개선 적용:
1) 제품명 다양화
2) 이미지 의미 안정성 보완(컬러 배지)
3) Top5 카드 선택 UX 강화
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
PACKAGING_TYPES = [
    "PET 병", "유리병", "알루미늄 캔", "종이팩",
    "무균팩", "파우치", "리필 파우치"
]

BEVERAGE_COMPANIES = [
    "롯데칠성음료", "코카콜라음료", "웅진식품", "동아오츠카",
    "빙그레", "매일유업", "CJ제일제당", "풀무원",
    "광동제약", "하이트진로음료", "팔도", "일화",
    "대상웰라이프", "농심", "SPC삼립", "해태htb"
]

FLAVORS = [
    "오렌지", "사과", "포도", "망고", "레몬",
    "자몽", "복숭아", "파인애플", "딸기",
    "블루베리", "유자", "배"
]

FLAVOR_COLOR = {
    "오렌지": "#FDBA74",
    "사과": "#86EFAC",
    "포도": "#C4B5FD",
    "망고": "#FACC15",
    "레몬": "#FDE047",
    "자몽": "#FB7185",
    "복숭아": "#FDA4AF",
    "파인애플": "#FCD34D",
    "딸기": "#F87171",
    "블루베리": "#818CF8",
    "유자": "#FDE68A",
    "배": "#A7F3D0",
}

PRODUCT_PREFIX = ["FRESHLAB", "VITAPOP", "NATURA", "JUICY+", "FRESHWAY"]
PRODUCT_STYLE = [
    "데일리 주스",
    "저당 클린 드링크",
    "비타민 부스트",
    "리프레시 음료",
    "클린 주스"
]


# =========================
# 세션 상태 초기화
# =========================
def init_state():
    for k in ["records", "top5", "selected_flavor"]:
        if k not in st.session_state:
            st.session_state[k] = None


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
    seed = flavor
    return f"https://picsum.photos/seed/{seed}/480/480"


def generate_fake_products(months: int, seed: int) -> List[Dict[str, Any]]:
    rng = random.Random(seed)
    today = datetime.today()
    records = []

    for _ in range(months):
        for _ in range(300):
            flavor = rng.choice(FLAVORS)
            records.append({
                "보고일자": (today - timedelta(days=rng.randint(0, 30))).strftime("%Y-%m-%d"),
                "제품명": random_product_name(flavor),
                "플레이버": flavor,
                "제품유형": "주스류",
                "포장": rng.choice(PACKAGING_TYPES),
                "음료제조회사": rng.choice(BEVERAGE_COMPANIES),
            })
    return records


def calculate_top5(records):
    c = Counter(r["플레이버"] for r in records)
    total = sum(c.values()) or 1
    return [{"flavor": f, "share": round(cnt / total * 100, 1)} for f, cnt in c.most_common(5)]


# =========================
# UI
# =========================
st.title("🥤 ABC 제품개발 교육 시뮬레이터")
st.caption("신입사원 교육용 · 제품기획 → 배합 → 공정 이해")

st.sidebar.header("조건 설정")
months = st.sidebar.slider("조회 개월 수", 1, 6, 1)
run = st.sidebar.button("실행")

if run:
    seed = random.randint(1, 9_999_999)
    records = generate_fake_products(months, seed)
    st.session_state.records = records
    st.session_state.top5 = calculate_top5(records)
    st.session_state.selected_flavor = None

records = st.session_state.records
top5 = st.session_state.top5

if not records:
    st.info("좌측에서 조건을 설정하고 실행하세요.")
    st.stop()

# -------------------------
# 테이블
# -------------------------
st.subheader("📋 음료류 품목제조보고")
st.dataframe(records, use_container_width=True, height=320)

st.divider()

# -------------------------
# Top5 카드 (선택 UX 강화)
# -------------------------
st.subheader("🔥 Top5 플레이버")

cols = st.columns(5)
for col, t in zip(cols, top5):
    f = t["flavor"]
    selected = (st.session_state.selected_flavor == f)

    with col:
        st.markdown(
            f"""
            <div style="
                border:3px solid {'#2563eb' if selected else '#e5e7eb'};
                border-radius:12px;
                padding:10px;
                background:white;
            ">
            """,
            unsafe_allow_html=True
        )

        st.image(get_demo_image(f), use_container_width=True)

        st.markdown(
            f"""
            <div style="
                background:{FLAVOR_COLOR.get(f, '#e5e7eb')};
                color:#111827;
                padding:4px 8px;
                border-radius:999px;
                font-size:12px;
                display:inline-block;
                margin-top:6px;
            ">
                {f}
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(f"**점유율 {t['share']}%**")

        if selected:
            st.success("선택됨")
        else:
            if st.button("이 맛으로 기획", key=f"pick_{f}"):
                st.session_state.selected_flavor = f

        st.markdown("</div>", unsafe_allow_html=True)

