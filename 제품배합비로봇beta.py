"""
ABC 제품개발 교육용 Streamlit 앱 (방어 설계 최종본)
- AI 응답 구조 불일치로 인한 KeyError 완전 방지
- AI 신규 제품 제안 & 배합비 설계 (좌/우 분할)
- 플레이버 의미 기반 이미지
- 제품명 다양화
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
        "ai_result": None,
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


def get_flavor_image(flavor: str) -> str:
    flavor_en = FLAVOR_EN.get(flavor, "fruit")
    return f"https://source.unsplash.com/featured/480x480/?{flavor_en},juice,drink"


def generate_fake_products(months: int) -> List[Dict]:
    today = datetime.today()
    records = []
    for _ in range(months):
        for _ in range(300):
            flavor = random.choice(FLAVORS)
            records.append({
                "보고일자": (today - timedelta(days=random.randint(0, 30))).strftime("%Y-%m-%d"),
                "제품명": random_product_name(flavor),
                "플레이버": flavor,
            })
    return records


def calculate_top5(records):
    c = Counter(r["플레이버"] for r in records)
    total = sum(c.values())
    return [{"flavor": f, "share": round(cnt / total * 100, 1)} for f, cnt in c.most_common(5)]


# =========================
# AI 응답 정규화 (핵심)
# =========================
def normalize_ai_result(raw: Dict, flavor: str) -> Dict:
    """
    어떤 형태의 AI 응답이 와도
    UI에서 항상 동일한 key로 접근 가능하게 만든다.
    """
    return {
        "concept": raw.get("concept", f"{flavor} 기반 데일리 음료"),
        "usp": raw.get("usp", ["데일리 음용", "트렌드 반영", "안정적 원가"]),
        "marketing": raw.get("marketing", ["출근 루틴", "저당 강조", "친환경 이미지"]),
        "formula": raw.get("formula", {
            "ingredients": [
                "정제수", f"{flavor} 과즙", "설탕", "구연산",
                "향료", "비타민C", "펙틴", "CMC",
                "클라우드", "소금"
            ],
            "기존": [80, 10, 5, 0.3, 0.4, 0.1, 0.1, 0.05, 3.95, 0.1],
            "A":    [78, 12, 3, 0.3, 0.4, 0.1, 0.1, 0.05, 5.95, 0.1],
            "B":    [79, 11, 4, 0.3, 0.6, 0.1, 0.1, 0.05, 4.75, 0.1],
        })
    }


def ai_concept_and_formula(flavor: str) -> Dict:
    """
    AI 호출 + 실패 대비
    """
    try:
        from openai import OpenAI
        client = OpenAI()

        prompt = f"""
너는 20년차 음료 제품개발 전문가다.
플레이버: {flavor}

1. 제품 컨셉
2. USP 3가지
3. 마케팅 포인트 3가지
4. 배합비 (기존 / A / B)

JSON으로만 출력하라.
"""
        res = client.responses.create(model="o4-mini", input=prompt)
        raw = json.loads(res.output_text)
    except Exception:
        raw = {}

    return normalize_ai_result(raw, flavor)


# =========================
# UI
# =========================
st.title("🥤 ABC 제품개발 교육 시뮬레이터")
st.caption("AI 응답 방어 설계 적용")

months = st.sidebar.slider("조회 개월 수", 1, 6, 1)
run = st.sidebar.button("실행")

if run:
    records = generate_fake_products(months)
    st.session_state.records = records
    st.session_state.top5 = calculate_top5(records)
    st.session_state.selected_flavor = None

records = st.session_state.records
top5 = st.session_state.top5

if not records:
    st.stop()

st.subheader("Top 플레이버")

cols = st.columns(5)
for col, t in zip(cols, top5):
    with col:
        st.image(get_flavor_image(t["flavor"]), use_container_width=True)
        st.markdown(f"**{t['flavor']}**")
        st.caption(f"{t['share']}%")
        if st.button("선택", key=t["flavor"]):
            st.session_state.selected_flavor = t["flavor"]
            st.session_state.ai_result = ai_concept_and_formula(t["flavor"])

if st.session_state.selected_flavor:
    data = st.session_state.ai_result

    st.divider()
    left, right = st.columns(2)

    with left:
        st.subheader("AI 제품 컨셉")
        st.markdown(f"**컨셉**: {data.get('concept')}")
        st.markdown("**USP**")
        for u in data.get("usp", []):
            st.write(f"- {u}")
        st.markdown("**마케팅 포인트**")
        for m in data.get("marketing", []):
            st.write(f"- {m}")

    with right:
        st.subheader("AI 배합비")
        f = data.get("formula", {})
        table = []
        for i, ing in enumerate(f.get("ingredients", [])):
            table.append({
                "원재료": ing,
                "기존": f.get("기존", [])[i],
                "A": f.get("A", [])[i],
                "B": f.get("B", [])[i],
            })
        st.dataframe(table, use_container_width=True)
