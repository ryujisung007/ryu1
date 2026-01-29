"""
ABC 제품개발 Streamlit GUI 데모
- 가상 품목제조보고 데이터
- Top5 플레이버 분석
- 카드형 제품 출력

Author role:
- 20년 경력 시니어 풀스택 개발자
- 가독성 우선 / 오류 최소화
"""

import streamlit as st
import random
from collections import Counter
from datetime import datetime, timedelta

# =========================
# 설정
# =========================
st.set_page_config(page_title="ABC 제품개발 데모", layout="wide")

# =========================
# 가상 데이터 생성 로직
# =========================

FLAVORS = [
    "오렌지", "사과", "포도", "망고", "레몬",
    "자몽", "복숭아", "파인애플", "딸기",
    "블루베리", "유자", "배"
]

FLAVOR_WEIGHTS = {
    "오렌지": 0.18,
    "사과": 0.14,
    "포도": 0.12,
    "망고": 0.10,
    "레몬": 0.08
}

DEFAULT_WEIGHT = 0.38 / (len(FLAVORS) - 5)


def weighted_flavor_choice() -> str:
    pool = []
    for f in FLAVORS:
        weight = FLAVOR_WEIGHTS.get(f, DEFAULT_WEIGHT)
        pool.extend([f] * int(weight * 100))
    return random.choice(pool)


def generate_fake_products(months: int):
    records = []
    today = datetime.today()

    for _ in range(months):
        for _ in range(300):
            flavor = weighted_flavor_choice()
            product_name = f"FRESHLAB {flavor} 스퀴지 주스 350mL"
            report_date = today - timedelta(days=random.randint(0, 30))

            records.append({
                "보고일자": report_date.strftime("%Y-%m-%d"),
                "제품명": product_name,
                "플레이버": flavor,
                "제품유형": "주스류",
                "포장": "rPET 350mL"
            })
    return records


def calculate_top5_flavors(records):
    counter = Counter(r["플레이버"] for r in records)
    total = sum(counter.values())
    top5 = counter.most_common(5)

    result = []
    for rank, (flavor, count) in enumerate(top5, start=1):
        result.append({
            "rank": rank,
            "flavor": flavor,
            "count": count,
            "share": round(count / total * 100, 1)
        })
    return result


# =========================
# UI
# =========================

st.title("🥤 ABC 제품개발 GUI 데모")
st.caption("가상 품목제조보고 데이터 기반 · Streamlit 데모")

# --- Sidebar ---
st.sidebar.header("🔍 검색 조건")

months = st.sidebar.number_input(
    "조회 개월 수",
    min_value=1,
    max_value=6,
    value=1,
    step=1
)

run = st.sidebar.button("검색 / 분석 실행")

# --- 상태 초기화 ---
if "records" not in st.session_state:
    st.session_state.records = None
    st.session_state.top5 = None

# --- 실행 ---
if run:
    records = generate_fake_products(months)
    top5 = calculate_top5_flavors(records)

    st.session_state.records = records
    st.session_state.top5 = top5

# =========================
# Dashboard
# =========================

if st.session_state.records:
    records = st.session_state.records
    top5 = st.session_state.top5

    st.subheader("📊 실행 요약")
    st.write(f"총 **{len(records)}건** 생성됨 · 최근 **{months}개월**")

    st.divider()

    # --- Top5 ---
    st.subheader("🔥 Top5 플레이버")

    for t in top5:
        st.write(
            f"{t['rank']}위 **{t['flavor']}** – "
            f"{t['count']}건 ({t['share']}%)"
        )

    st.divider()

    # --- 카드 영역 ---
    st.subheader("🧃 플레이버별 대표 제품 (가상)")

    cols = st.columns(5)

    for col, t in zip(cols, top5):
        with col:
            st.markdown(
                f"""
                <div style="
                    border:1px solid #e5e7eb;
                    border-radius:8px;
                    padding:12px;
                    text-align:center;
                    background-color:white;
                ">
                    <div style="
                        height:90px;
                        background:#fde68a;
                        border-radius:6px;
                        margin-bottom:10px;
                        display:flex;
                        align-items:center;
                        justify-content:center;
                        font-size:12px;
                    ">
                        가상 이미지
                    </div>
                    <strong>{t['flavor']} 스퀴지 주스</strong><br/>
                    <span style="font-size:13px;">rPET 350mL</span><br/>
                    <span style="color:#2563eb;font-size:12px;">
                        상큼 / 데일리
                    </span>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.divider()

    # --- 테이블 ---
    st.subheader("📋 가상 품목제조보고 테이블")
    st.dataframe(records, use_container_width=True)

else:
    st.info("좌측에서 조건을 선택한 후 **검색 / 분석 실행**을 눌러주세요.")
