"""
ABC 제품개발 교육용 Streamlit 앱 (이미지 의미 개선 버전)
- 플레이버 연관 Unsplash 이미지 적용
- 제품명 다양화
- AI 신규 제품 제안 & 배합비 설계 (좌/우 분할)
"""

from __future__ import annotations

import random
import json
from collections import Counter
from datetime import datetime, timedelta
from typing import Dict, List

import streamlit as st


# =========================
# 기본 설정
# =========================
st.set_page_config(page_title="ABC 제품개발 교육 시뮬레이터", layout="wide")


# =========================
# 상수 정의
# =========================
PACKAGING_TYPES = [
    "PET 병", "유리병", "알루미늄 캔",
    "종이팩", "무균팩", "파우치", "리필 파우치"
]

BEVERAGE_COMPANIES = [
    "롯데칠성음료", "코카콜라음료", "웅진식품", "동아오츠카",
    "빙그레", "매일유업", "CJ제일제당", "풀무원",
    "광동제약", "하이트진로음료", "팔도", "일화",
    "대상웰라이프", "농심", "SPC삼립", "해태htb",
    "정식품", "샘표", "남양유업", "오뚜기"
]

FLAVORS = [
    "오렌지", "사과", "포도", "망고", "레몬",
    "자몽", "복숭아", "파인애플", "딸기",
    "블루베리", "유자", "배"
]

FLAVOR_EN = {
    "오렌지": "orange",
    "사과": "apple",
    "포도": "grape",
    "망고": "mango",
    "레몬": "lemon",
    "자몽": "grapefruit",
    "복숭아": "peach",
    "파인애플": "pineapple",
    "딸기": "strawberry",
    "블루베리": "blueberry",
    "유자": "yuzu",
    "배": "pear",
}

PRODUCT_PREFIX = ["FRESHLAB", "VITAPOP", "NATURA", "FRESHWAY", "JUICY+"]
PRODUCT_STYLE = ["데일리 주스", "저당 드링크", "비타민 부스트", "리프레시 음료", "클린 주스"]


# =========================
# 세션 상태 초기화
# =========================
def init_state():
    defaults = {
        "records": None,
        "top5": None,
        "selected_flavor": None,
        "ai_concept": None,
        "ai_formula": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


init_state()


# =========================
# 유틸 함수
# =========================
def random_product_name(flavor: str) -> str:
    prefix = random.choice(PRODUCT_PREFIX)
    style = random.choice(PRODUCT_STYLE)
    if random.random() < 0.35:
        other = random.choice([f for f in FLAVORS if f != flavor])
        name = f"{flavor}·{other}"
    else:
        name = flavor
    return f"{prefix} {name} {style}"


def get_flavor_image(flavor_kr: str) -> str:
    flavor_en = FLAVOR_EN.get(flavor_kr, "fruit")
    query = f"{flavor_en},juice,drink,beverage"
    return f"https://source.unsplash.com/featured/480x480/?{query}"


def generate_fake_products(months: int, seed: int) -> List[Dict]:
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
    total = sum(c.values())
    return [{"flavor": f, "share": round(cnt / total * 100, 1)} for f, cnt in c.most_common(5)]


# =========================
# UI
# =========================
st.title("🥤 ABC 제품개발 교육 시뮬레이터")
st.caption("플레이버 의미 기반 이미지 · AI 제품기획 · 배합비 설계")

st.sidebar.header("조건 설정")
months = st.sidebar.slider("조회 개월 수", 1, 6, 1)
run = st.sidebar.button("실행")

if run:
    seed = random.randint(1, 999999)
    records = generate_fake_products(months, seed)
    st.session_state.records = records
    st.session_state.top5 = calculate_top5(records)
    st.session_state.selected_flavor = None

records = st.session_state.records
top5 = st.session_state.top5

if not records:
    st.info("좌측에서 조건을 설정하고 실행하세요.")
    st.stop()

st.subheader("Top 플레이버 트렌드")

cols = st.columns(5)
for col, t in zip(cols, top5):
    with col:
        st.image(get_flavor_image(t["flavor"]), use_container_width=True)
        st.markdown(f"**{t['flavor']}**")
        st.caption(f"점유율 {t['share']}%")
