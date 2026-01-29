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
import math


# =========================================================
# 기본 설정
# =========================================================
st.set_page_config(page_title="ABC 제품개발 교육 시뮬레이터", layout="wide")


# =========================================================
# 상수
# =========================================================
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

FLAVOR_EN_MAP = {
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
    "클린 주스",
    "이뮨 부스트",
    "모닝 루틴 드링크",
    "애프터짐 리커버리",
]

FLAVOR_WEIGHTS = {
    "오렌지": 0.18,
    "사과": 0.14,
    "포도": 0.12,
    "망고": 0.10,
    "레몬": 0.08,
}
DEFAULT_WEIGHT = 0.38 / (len(FLAVORS) - 5)

ROLE_OPTIONS = ["통합(ABC)", "A: 기획", "B: 마케팅", "C: 연구/개발"]


# =========================================================
# 세션 상태 초기화
# =========================================================
def init_state():
    defaults = {
        "seed": 0,
        "months": 1,
        "records": None,
        "top5": None,
        "selected_flavor": None,
        "step": 0,
        "role": "통합(ABC)",
        "ai_error": None,
        "mission_data": None,
        "mission_submitted": False,
        "mission_score": 0,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


init_state()


# =========================================================
# 유틸
# =========================================================
def get_demo_image(flavor: str) -> str:
    seed = FLAVOR_EN_MAP.get(flavor, "fruit")
    return f"https://picsum.photos/seed/{seed}/400/400"


def random_product_name(rng: random.Random, flavor: str) -> str:
    brand = rng.choice(PRODUCT_PREFIX)
    style = rng.choice(PRODUCT_STYLE)
    if rng.random() < 0.35:
        other = rng.choice([f for f in FLAVORS if f != flavor])
        name = f"{flavor}·{other}"
    else:
        name = flavor
    tag = ""
    if rng.random() < 0.25:
        tag = " " + rng.choice(["저당", "제로슈가", "비타민C", "이뮨", "에너지"])
    return f"{brand} {name} {style}{tag}"


# =========================================================
# 데이터 생성
# =========================================================
def weighted_flavor_choice(rng: random.Random) -> str:
    pool = []
    for f in FLAVORS:
        w = FLAVOR_WEIGHTS.get(f, DEFAULT_WEIGHT)
        pool.extend([f] * max(1, int(w * 100)))
    return rng.choice(pool)


def generate_fake_products(months: int, seed: int) -> List[Dict[str, Any]]:
    rng = random.Random(seed)
    today = datetime.today()
    records = []
    for _ in range(months):
        for _ in range(300):
            flavor = weighted_flavor_choice(rng)
            records.append({
                "보고일자": (today - timedelta(days=rng.randint(0, 30))).strftime("%Y-%m-%d"),
                "제품명": random_product_name(rng, flavor),
                "플레이버": flavor,
                "제품유형": "주스류",
                "포장": rng.choice(PACKAGING_TYPES),
                "음료제조회사": rng.choice(BEVERAGE_COMPANIES),
            })
    return records


def calculate_top5(records):
    counter = Counter(r["플레이버"] for r in records)
    total = sum(counter.values()) or 1
    out = []
    for i, (f, c) in enumerate(counter.most_common(5), start=1):
        out.append({"rank": i, "flavor": f, "count": c, "share": round(c / total * 100, 1)})
    return out


# =========================================================
# 차트 (수정 완료)
# =========================================================
def plot_top5_bar(top5):
    labels = [FLAVOR_EN_MAP[t["flavor"]] for t in top5]
    shares = [t["share"] for t in top5]

    fig, ax = plt.subplots(figsize=(6, 3))
    ax.barh(labels, shares, color="#60a5fa")
    ax.set_xlabel("Share (%)")
    ax.set_title("Top 5 Flavor Share", fontsize=11)
    ax.invert_yaxis()

    for i, v in enumerate(shares):
        ax.text(v + 0.3, i, f"{v}%", va="center", fontsize=9)

    plt.tight_layout()
    st.pyplot(fig, clear_figure=True)


def plot_sensory_radar(sensory):
    labels = list(sensory.keys())
    values = list(sensory.values())
    baseline = [5.0] * len(labels)

    values += values[:1]
    baseline += baseline[:1]

    angles = [2 * math.pi * i / len(labels) for i in range(len(labels))]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(4, 4), subplot_kw=dict(polar=True))
    ax.plot(angles, values, linewidth=2, label="Target")
    ax.fill(angles, values, alpha=0.15)
    ax.plot(angles, baseline, linestyle="--", linewidth=1, label="Baseline(5)")

    ax.set_thetagrids([a * 180 / math.pi for a in angles[:-1]], labels, fontsize=9)
    ax.set_yticklabels([])
    ax.set_title("Sensory Target Radar (0–10)", fontsize=11)
    ax.legend(loc="upper right", bbox_to_anchor=(1.25, 1.1), fontsize=8)

    plt.tight_layout()
    st.pyplot(fig, clear_figure=True)


# =========================================================
# AI 미션 생성 (항상 새 문제)
# =========================================================
def generate_ai_mission():
    try:
        from openai import OpenAI
        client = OpenAI()
        prompt = """
신입 음료개발 연구원 교육용 문제를 3문항 생성하라.
- 제조공정/배합/품질관리 중심
- 4지선다
- JSON만 출력
"""
        r = client.responses.create(model="o4-mini", input=prompt)
        data = json.loads(r.output_text)
        if "questions" in data:
            return data
    except Exception:
        pass

    # 폴백
    return {
        "questions": [
            {
                "q": "Hot-fill 공정에서 가장 중요한 관리 요소는?",
                "options": ["당도", "충전온도", "라벨재질", "병색상"],
                "answer": 1,
            },
            {
                "q": "저당 음료에서 설탕 대체 시 가장 중요한 관점은?",
                "options": ["색상", "삼투압", "단맛 프로파일", "용기무게"],
                "answer": 2,
            },
            {
                "q": "Cloud break 발생 시 1차 점검 항목은?",
                "options": ["라벨", "pH/안정제", "병 두께", "마개"],
                "answer": 1,
            },
        ]
    }


# =========================================================
# Sidebar
# =========================================================
st.title("🥤 ABC 제품개발 교육 시뮬레이터")
st.sidebar.header("설정")

st.session_state.role = st.sidebar.radio("직무", ROLE_OPTIONS)
st.session_state.months = st.sidebar.number_input("조회 개월 수", 1, 6, st.session_state.months)

if st.sidebar.button("▶ 실행"):
    st.session_state.seed = random.randint(1, 9999999)
    st.session_state.records = generate_fake_products(st.session_state.months, st.session_state.seed)
    st.session_state.top5 = calculate_top5(st.session_state.records)
    st.session_state.selected_flavor = None
    st.session_state.mission_data = generate_ai_mission()
    st.session_state.mission_submitted = False
    st.session_state.mission_score = 0


# =========================================================
# (4) 테이블
# =========================================================
st.subheader("📋 음료류 품목제조보고")
if st.session_state.records:
    st.dataframe(st.session_state.records, height=360, use_container_width=True)
else:
    st.info("좌측에서 ▶ 실행을 누르세요.")

st.divider()


# =========================================================
# (1) Top5
# =========================================================
st.subheader("🔥 Top5 플레이버")
if st.session_state.top5:
    plot_top5_bar(st.session_state.top5)
    cols = st.columns(5)
    for col, t in zip(cols, st.session_state.top5):
        with col:
            st.image(get_demo_image(t["flavor"]))
            st.markdown(f"**{t['flavor']}** ({t['share']}%)")
            if st.button("이 맛으로 기획", key=t["flavor"]):
                st.session_state.selected_flavor = t["flavor"]
else:
    st.info("Top5 데이터 없음")

st.divider()


# =========================================================
# (2) A/B/C (요약 표시용)
# =========================================================
st.subheader("🧠🧪 직무별 분석")
if st.session_state.selected_flavor:
    st.success(f"선택 플레이버: {st.session_state.selected_flavor}")
else:
    st.info("플레이버를 선택하세요.")

st.divider()


# =========================================================
# (3) 미션 (항상 표시)
# =========================================================
st.subheader("🎯 AI 생성 신입사원 미션")

mission = st.session_state.mission_data
if mission:
    score = 0
    for i, q in enumerate(mission["questions"], start=1):
        ans = st.radio(f"Q{i}. {q['q']}", q["options"], key=f"mq_{i}")
        if st.session_state.mission_submitted:
            if q["options"].index(ans) == q["answer"]:
                score += 1

    if st.button("미션 제출"):
        st.session_state.mission_submitted = True
        st.session_state.mission_score = score

    if st.session_state.mission_submitted:
        st.metric("점수", st.session_state.mission_score)
