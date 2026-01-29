"""
ABC 제품개발 Streamlit GUI 데모
- 가상 품목제조보고 데이터
- Top5 플레이버 분석
- OpenAI 실제 호출 기반 트렌드 해석 및 맛 설명
- 카드형 제품 출력
"""

import streamlit as st
import random
from collections import Counter
from datetime import datetime, timedelta
import json

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
# OpenAI 실제 분석
# =========================

def analyze_with_openai(top5):
    """
    OpenAI에게 실제로:
    - 플레이버 트렌드 요약
    - 플레이버별 시장 포지션
    - 플레이버별 맛 설명
    을 JSON으로 생성하게 함
    """

    from openai import OpenAI

    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    flavor_stats = [
        {"flavor": t["flavor"], "share": t["share"]}
        for t in top5
    ]

    prompt = "\n".join([
        "너는 20년 경력의 식품음료 트렌드 분석 전문가다.",
        "아래는 최근 출시된 주스류 제품의 플레이버 점유율이다.",
        "이 데이터를 바탕으로 트렌드를 분석하라.",
        "",
        f"플레이버 데이터: {flavor_stats}",
        "",
        "아래 JSON 형식으로만 응답하라.",
        "{",
        '  "summary": "전체 트렌드 요약 문장",',
        '  "flavors": {',
        '    "플레이버명": {',
        '      "level": "메인스트림/성장형/니치",',
        '      "market_comment": "시장 해석",',
        '      "taste_description": "소비자 관점의 맛 설명"',
        '    }',
        '  }',
        "}"
    ])

    resp = client.responses.create(
        model="o4-mini",
        input=prompt
    )

    return json.loads(resp.output_text)


# =========================
# UI
# =========================

st.title("🥤 ABC 제품개발 GUI 데모")
st.caption("가상 품목제조보고 데이터 + OpenAI 실제 트렌드 분석")

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
    st.session_state.ai_result = None

# --- 실행 ---
if run:
    records = generate_fake_products(months)
    top5 = calculate_top5_flavors(records)

    with st.spinner("AI가 플레이버 트렌드를 분석 중입니다..."):
        try:
            ai_result = analyze_with_openai(top5)
        except Exception as e:
            st.error("AI 분석 실패. 잠시 후 다시 시도하세요.")
            st.stop()

    st.session_state.records = records
    st.session_state.top5 = top5
    st.session_state.ai_result = ai_result


# =========================
# Dashboard
# =========================

if st.session_state.records:
    records = st.session_state.records
    top5 = st.session_state.top5
    ai = st.session_state.ai_result

    st.subheader("📊 실행 요약")
    st.write(f"총 **{len(records)}건** 생성됨 · 최근 **{months}개월**")

    st.divider()

    # --- AI 요약 ---
    st.subheader("🧠 AI 플레이버 트렌드 요약")
    st.info(ai["summary"])

    st.divider()

    # --- Top5 ---
    st.subheader("🔥 Top5 플레이버")

    for t in top5:
        f = t["flavor"]
        info = ai["flavors"][f]
        st.write(
            f"{t['rank']}위 **{f}** – {t['count']}건 ({t['share']}%) · {info['level']}"
        )

    st.divider()

    # --- 카드 영역 ---
    st.subheader("🧃 플레이버별 대표 제품 (AI 분석 반영)")

    cols = st.columns(5)

    for col, t in zip(cols, top5):
        f = t["flavor"]
        info = ai["flavors"][f]

        with col:
            st.markdown(
                f"""
                <div style="
                    border:1px solid #e5e7eb;
                    border-radius:8px;
                    padding:12px;
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
                    <strong>{f} 스퀴지 주스</strong><br/>
                    <span style="font-size:13px;">rPET 350mL</span><br/>
                    <span style="color:#2563eb;font-size:12px;">
                        {info['market_comment']}
                    </span>
                    <hr/>
                    <span style="font-size:12px;">
                        {info['taste_description']}
                    </span>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.divider()

    st.subheader("📋 가상 품목제조보고 테이블")
    st.dataframe(records, use_container_width=True)

else:
    st.info("좌측에서 조건을 선택한 후 **검색 / 분석 실행**을 눌러주세요.")
