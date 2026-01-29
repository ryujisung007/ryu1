"""
ABC 제품개발 Streamlit GUI 데모
- 가상 품목제조보고 데이터
- Top5 플레이버 분석
- AI 기반 플레이버 트렌드 해석 (로컬 AI)
- AI 기반 맛 설명 적용
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
        share = round(count / total * 100, 1)
        result.append({
            "rank": rank,
            "flavor": flavor,
            "count": count,
            "share": share
        })
    return result


# =========================
# AI 해석 로직 (로컬)
# =========================

def analyze_flavor_trend_ai(top5):
    """
    AI 역할:
    - 플레이버 분포를 해석해 트렌드 문장 생성
    - 각 플레이버별 시장 포지션 해석
    """

    summary_lines = []
    flavor_insight = {}

    dominant = top5[0]["share"]

    if dominant >= 18:
        summary_lines.append(
            "특정 메이저 플레이버 중심의 안정적 시장 구조가 형성되어 있습니다."
        )
    else:
        summary_lines.append(
            "플레이버가 다각화되며 소비자 선택 폭이 넓어지는 트렌드가 관찰됩니다."
        )

    summary_lines.append(
        "상위 플레이버들은 '상큼함·클린함·데일리 음용성'을 중심으로 공통점을 보입니다."
    )

    for t in top5:
        if t["share"] >= 15:
            level = "메인스트림"
            comment = "가장 대중적이며 실패 리스크가 낮은 핵심 플레이버"
        elif t["share"] >= 10:
            level = "성장형"
            comment = "차별화 설계에 따라 히트 가능성이 높은 플레이버"
        else:
            level = "니치"
            comment = "특정 타깃층 공략에 적합한 플레이버"

        flavor_insight[t["flavor"]] = {
            "level": level,
            "comment": comment
        }

    return {
        "summary": " ".join(summary_lines),
        "flavor_insight": flavor_insight
    }


def generate_taste_description_ai(flavor, level):
    """
    AI 맛 설명 생성 (플레이버 + 트렌드 레벨 기반)
    """

    base = {
        "오렌지": "밝고 직관적인 산미와 자연스러운 단맛",
        "사과": "부드러운 산미와 깔끔한 마무리",
        "포도": "농축된 과즙감과 달콤한 풍미",
        "망고": "열대과일 특유의 진한 바디감",
        "레몬": "샤프한 산미와 청량한 인상",
        "자몽": "쌉싸름한 산미와 어른스러운 풍미",
        "복숭아": "은은한 단향과 부드러운 질감",
        "파인애플": "톡 쏘는 산미와 달콤함의 균형",
        "딸기": "달콤한 향 중심의 부드러운 맛",
        "블루베리": "은은한 단맛과 깊은 풍미",
        "유자": "한국적 시트러스의 상큼한 향",
        "배": "깔끔하고 시원한 단맛"
    }

    if level == "메인스트림":
        suffix = "으로 누구나 부담 없이 즐길 수 있는 데일리 주스입니다."
    elif level == "성장형":
        suffix = "으로 트렌디한 이미지 연출에 적합한 플레이버입니다."
    else:
        suffix = "으로 개성 있는 소비자를 겨냥한 차별화 포인트를 가집니다."

    return base.get(flavor, "상큼한 과일 풍미") + suffix


# =========================
# UI
# =========================

st.title("🥤 ABC 제품개발 GUI 데모")
st.caption("가상 품목제조보고 데이터 기반 · AI 트렌드 해석 데모")

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
    st.session_state.ai_trend = None

# --- 실행 ---
if run:
    records = generate_fake_products(months)
    top5 = calculate_top5_flavors(records)
    ai_trend = analyze_flavor_trend_ai(top5)

    st.session_state.records = records
    st.session_state.top5 = top5
    st.session_state.ai_trend = ai_trend

# =========================
# Dashboard
# =========================

if st.session_state.records:
    records = st.session_state.records
    top5 = st.session_state.top5
    ai_trend = st.session_state.ai_trend

    st.subheader("📊 실행 요약")
    st.write(f"총 **{len(records)}건** 생성됨 · 최근 **{months}개월**")

    st.divider()

    # --- AI 트렌드 요약 ---
    st.subheader("🧠 AI 플레이버 트렌드 해석")
    st.info(ai_trend["summary"])

    st.divider()

    # --- Top5 ---
    st.subheader("🔥 Top5 플레이버")

    for t in top5:
        insight = ai_trend["flavor_insight"][t["flavor"]]
        st.write(
            f"{t['rank']}위 **{t['flavor']}** – "
            f"{t['count']}건 ({t['share']}%) · {insight['level']}"
        )

    st.divider()

    # --- 카드 영역 ---
    st.subheader("🧃 플레이버별 대표 제품 (AI 해석 반영)")

    cols = st.columns(5)

    for col, t in zip(cols, top5):
        insight = ai_trend["flavor_insight"][t["flavor"]]
        taste_desc = generate_taste_description_ai(t["flavor"], insight["level"])

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
                    <strong>{t['flavor']} 스퀴지 주스</strong><br/>
                    <span style="font-size:13px;">rPET 350mL</span><br/>
                    <span style="color:#2563eb;font-size:12px;">
                        {insight['comment']}
                    </span>
                    <hr/>
                    <span style="font-size:12px;">
                        {taste_desc}
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
