"""
ABC 제품개발 교육용 Streamlit 앱 (안정화 최종본)
- 이미지 안정화 (picsum)
- 제품명 다양화
- AI 신규 제품 제안 & 배합비 설계 (좌/우 분할) 복구
- 제조공정 포함 신입사원 미션
"""

from __future__ import annotations

import random
import json
import hashlib
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


def get_image_url(flavor: str) -> str:
    seed = FLAVOR_EN.get(flavor, "fruit")
    return f"https://picsum.photos/seed/{seed}-drink/420/420"


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
# AI 로직 (실패 시 fallback)
# =========================
def ai_concept_and_formula(flavor: str):
    try:
        from openai import OpenAI
        client = OpenAI()

        prompt = f"""
너는 20년차 음료 제품개발 전문가다.

플레이버: {flavor}

1. 신제품 컨셉 (제품명 포함)
2. 핵심 USP 3가지
3. 마케팅 포인트 3가지
4. 음료 배합비 제안 (원재료 10개 이상)
   - 기존배합비 / AI 제안 A / AI 제안 B
   - 각각 합계 100%

JSON으로만 출력하라.
"""

        res = client.responses.create(model="o4-mini", input=prompt)
        return json.loads(res.output_text)

    except Exception:
        # fallback
        ingredients = [
            "정제수", f"{flavor} 과즙", "설탕", "구연산",
            "향료", "비타민C", "펙틴", "CMC",
            "클라우드", "소금"
        ]
        base = [80, 10, 5, 0.3, 0.4, 0.1, 0.1, 0.05, 3.95, 0.1]

        def variant(delta):
            return [round(v + d, 2) for v, d in zip(base, delta)]

        return {
            "concept": f"{flavor} 기반 데일리 저당 음료",
            "usp": ["클린 라벨", "산미 밸런스", "반복구매"],
            "marketing": ["출근 루틴", "운동 후", "저당 강조"],
            "formula": {
                "ingredients": ingredients,
                "기존": base,
                "A": variant([-2, 1, -2, 0, 0, 0, 0, 0, 3, 0]),
                "B": variant([-1, 2, -1, 0, 0.2, 0, 0, 0, -0.2, 0]),
            }
        }


# =========================
# UI
# =========================
st.title("🥤 ABC 제품개발 교육 시뮬레이터")
st.caption("데이터 → 트렌드 → AI 컨셉 → 배합비 → 제조공정 사고 훈련")

st.sidebar.header("조건 설정")
months = st.sidebar.slider("조회 개월 수", 1, 6, 1)
run = st.sidebar.button("실행")

if run:
    seed = random.randint(1, 999999)
    records = generate_fake_products(months, seed)
    st.session_state.records = records
    st.session_state.top5 = calculate_top5(records)
    st.session_state.selected_flavor = None
    st.session_state.ai_concept = None
    st.session_state.ai_formula = None

records = st.session_state.records
top5 = st.session_state.top5

if not records:
    st.info("좌측에서 조건을 설정하고 실행하세요.")
    st.stop()

# --- 테이블 ---
st.subheader("가상 품목제조보고 데이터")
st.dataframe(records, use_container_width=True, height=350)

st.divider()

# --- Top5 카드 ---
st.subheader("Top 플레이버 트렌드")
cols = st.columns(5)

for col, t in zip(cols, top5):
    with col:
        st.image(get_image_url(t["flavor"]), use_container_width=True)
        st.markdown(f"**{t['flavor']}**")
        st.caption(f"점유율 {t['share']}%")
        if st.button("이 맛으로 신제품 기획", key=t["flavor"]):
            st.session_state.selected_flavor = t["flavor"]
            data = ai_concept_and_formula(t["flavor"])
            st.session_state.ai_concept = data
            st.session_state.ai_formula = data.get("formula")

# --- AI 컨셉 & 배합비 (좌/우 분할) ---
if st.session_state.selected_flavor:
    st.divider()
    left, right = st.columns(2)

    with left:
        st.subheader("AI 신규 제품 컨셉")
        data = st.session_state.ai_concept
        st.markdown(f"**컨셉**: {data['concept']}")
        st.markdown("**USP**")
        for u in data["usp"]:
            st.write(f"- {u}")
        st.markdown("**마케팅 포인트**")
        for m in data["marketing"]:
            st.write(f"- {m}")

    with right:
        st.subheader("AI 추천 음료 배합비")
        f = st.session_state.ai_formula
        table = []
        for i, ing in enumerate(f["ingredients"]):
            table.append({
                "원재료": ing,
                "기존배합비(%)": f["기존"][i],
                "AI 제안 A(%)": f["A"][i],
                "AI 제안 B(%)": f["B"][i],
            })
        st.dataframe(table, use_container_width=True)

# --- 신입사원 미션 ---
st.divider()
st.subheader("신입사원 미션 – 음료 제조공정")

q = st.radio(
    "NFC 과즙 음료의 올바른 제조공정 순서는?",
    [
        "원료계량 → 혼합 → 살균 → 충전",
        "원료계량 → 살균 → 혼합 → 충전",
        "혼합 → 충전 → 살균 → 포장",
    ]
)

if st.button("정답 확인"):
    if q.startswith("원료계량 → 혼합"):
        st.success("정답입니다. 혼합 후 살균이 기본 공정입니다.")
    else:
        st.error("오답입니다. 공정 흐름을 다시 검토하세요.")
