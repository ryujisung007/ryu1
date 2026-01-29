"""
ABC 제품개발 교육용 Streamlit 앱 (AI 미션 자동 생성 포함 최종본)
"""

from __future__ import annotations

import random
from collections import Counter
from datetime import datetime, timedelta
from typing import List, Dict, Any

import streamlit as st
import matplotlib.pyplot as plt

# =========================
# 기본 설정
# =========================
st.set_page_config(page_title="ABC 제품개발 교육 시뮬레이터", layout="wide")

# =========================
# 세션 초기화
# =========================
def init_state():
    defaults = {
        "records": None,
        "top5": None,
        "selected_flavor": None,
        "role": "통합(ABC)",
        "mission": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# =========================
# 상수
# =========================
ROLES = ["통합(ABC)", "A: 기획", "B: 마케팅", "C: 연구/개발"]
FLAVORS = ["오렌지", "사과", "포도", "망고", "레몬", "자몽", "복숭아", "파인애플"]

# =========================
# 데이터 생성
# =========================
def generate_records(months: int):
    rows = []
    today = datetime.today()
    for _ in range(months * 300):
        f = random.choice(FLAVORS)
        rows.append({
            "보고일자": (today - timedelta(days=random.randint(0, 30))).strftime("%Y-%m-%d"),
            "제품명": f"{f} 블렌드 주스",
            "플레이버": f,
            "제품유형": "주스류",
            "포장": random.choice(["PET", "캔", "종이팩"]),
            "제조회사": random.choice(["롯데", "웅진", "빙그레", "코카콜라"]),
        })
    return rows

def calc_top5(records):
    c = Counter(r["플레이버"] for r in records)
    total = sum(c.values())
    return [{"flavor": f, "share": round(v / total * 100, 1)} for f, v in c.most_common(5)]

# =========================
# 차트
# =========================
def plot_top5(top5):
    fig, ax = plt.subplots(figsize=(5, 3))
    ax.barh([t["flavor"] for t in top5], [t["share"] for t in top5])
    ax.invert_yaxis()
    st.pyplot(fig)

# =========================
# AI 미션 생성 (로컬 자동)
# =========================
def generate_ai_mission(role: str, flavor: str) -> Dict[str, Any]:
    if role.startswith("A"):
        return {
            "question": f"{flavor} 기반 신제품의 핵심 USP로 가장 적절한 것은?",
            "options": [
                "원가 최소화",
                "관능 차별화",
                "패키지 색상",
                "유통 마진",
            ],
            "answer": 1,
            "explain": "기획 관점에서는 소비자 체감 가치가 핵심입니다."
        }

    if role.startswith("B"):
        return {
            "question": f"{flavor} 주스를 20대 타깃으로 마케팅할 때 가장 중요한 메시지는?",
            "options": [
                "저당",
                "상큼함",
                "대용량",
                "전통성",
            ],
            "answer": 1,
            "explain": "젊은 층은 즉각적 맛 인지가 중요합니다."
        }

    if role.startswith("C"):
        return {
            "question": f"{flavor} 과즙 음료 제조 시 가장 먼저 관리해야 할 공정 변수는?",
            "options": [
                "라벨 디자인",
                "pH",
                "병 색상",
                "광택",
            ],
            "answer": 1,
            "explain": "pH는 미생물 안정성과 관능에 직접적 영향을 줍니다."
        }

    # 통합
    return {
        "question": f"{flavor} 신제품 개발 시 가장 우선 고려해야 할 요소는?",
        "options": [
            "원가",
            "시장성",
            "공정 안정성",
            "모두 중요",
        ],
        "answer": 3,
        "explain": "ABC 통합 관점이 필요합니다."
    }

# =========================
# UI
# =========================
st.title("🥤 ABC 제품개발 교육 시뮬레이터")

st.sidebar.header("설정")
st.session_state.role = st.sidebar.radio("직무 선택", ROLES)
months = st.sidebar.number_input("조회 개월", 1, 6, 1)

if st.sidebar.button("▶ 실행"):
    st.session_state.records = generate_records(months)
    st.session_state.top5 = calc_top5(st.session_state.records)
    st.session_state.selected_flavor = None
    st.session_state.mission = None

# ---------- (4) 테이블 ----------
st.subheader("📋 품목제조보고")
if st.session_state.records:
    st.dataframe(st.session_state.records, use_container_width=True)
else:
    st.info("실행 버튼을 누르세요.")

st.divider()

# ---------- (1) Top5 ----------
st.subheader("🔥 Top5 플레이버")
if st.session_state.top5:
    plot_top5(st.session_state.top5)
    cols = st.columns(5)
    for col, t in zip(cols, st.session_state.top5):
        with col:
            if st.button(t["flavor"]):
                st.session_state.selected_flavor = t["flavor"]
else:
    st.info("Top5 없음")

st.divider()

# ---------- (2) 분석 ----------
st.subheader("🧠 직무별 분석")
if st.session_state.selected_flavor:
    st.write(f"선택 플레이버: **{st.session_state.selected_flavor}**")
    st.write(f"직무: **{st.session_state.role}**")
else:
    st.info("플레이버를 선택하세요.")

st.divider()

# ---------- (3) AI 생성 미션 ----------
st.subheader("🎯 AI 생성 미션")

if st.session_state.selected_flavor:
    if st.session_state.mission is None:
        st.session_state.mission = generate_ai_mission(
            st.session_state.role,
            st.session_state.selected_flavor
        )

    m = st.session_state.mission
    st.markdown(f"**문제**: {m['question']}")
    choice = st.radio("선택", m["options"])

    if st.button("정답 확인"):
        if m["options"].index(choice) == m["answer"]:
            st.success("정답입니다.")
        else:
            st.error("오답입니다.")
        st.info(f"해설: {m['explain']}")
else:
    st.info("플레이버 선택 후 미션이 생성됩니다.")
