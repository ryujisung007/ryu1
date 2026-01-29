"""
ABC 제품개발 Streamlit GUI 데모 (교육용 완성본)
- 가상 품목제조보고 데이터
- Top5 플레이버 분석
- OpenAI 실제 호출 기반 트렌드 해석 및 맛 설명
- 안정적 데모 이미지(picsum) + CSS 라벨 오버레이
- 카드 클릭 → AI 신규 맛/원료 조합 제안
- 신입사원 미션 모드(선택형 과제 + 해설)

Author role:
- 20년 경력 AI 코딩 스택 전문가
- 교육·워크숍·Cloud·모바일 환경 최적화
- 가독성·안정성 최우선
"""

from __future__ import annotations

import streamlit as st
import random
from collections import Counter
from datetime import datetime, timedelta
import json
import time
from typing import Dict

# =========================
# 기본 설정
# =========================
st.set_page_config(page_title="ABC 제품개발 교육 데모", layout="wide")

# =========================
# 세션 상태 초기화
# =========================

def init_session_state():
    defaults = {
        "records": None,
        "top5": None,
        "ai_result": None,
        "ai_error": None,
        "selected_flavor": None,
        "mission_answer": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session_state()

# =========================
# 데이터 정의
# =========================

# 국내 음료 포장 형태 (예시)
PACKAGING_TYPES = [
    "PET 병", "유리병", "알루미늄 캔", "종이팩", "파우치",
    "스틱 파우치", "컵형", "대용량 PET", "무균팩", "리필 파우치"
]

# 국내 주요 음료 제조사 (예시)
BEVERAGE_COMPANIES = [
    "롯데칠성음료", "코카콜라음료", "웅진식품", "동아오츠카",
    "빙그레", "매일유업", "남양유업", "CJ제일제당",
    "풀무원", "오뚜기", "하이트진로음료", "일화",
    "해태htb", "팔도", "광동제약", "대상웰라이프",
    "정식품", "샘표", "농심", "SPC삼립"
]


FLAVORS = ["오렌지","사과","포도","망고","레몬","자몽","복숭아","파인애플","딸기","블루베리","유자","배"]

FLAVOR_EN_MAP: Dict[str, str] = {
    "오렌지": "orange juice",
    "사과": "apple juice",
    "포도": "grape juice",
    "망고": "mango juice",
    "레몬": "lemon citrus drink",
    "자몽": "grapefruit citrus drink",
    "복숭아": "peach juice",
    "파인애플": "pineapple juice",
    "딸기": "strawberry juice",
    "블루베리": "blueberry juice",
    "유자": "yuzu citrus drink",
    "배": "pear juice",
}

FLAVOR_WEIGHTS = {"오렌지":0.18,"사과":0.14,"포도":0.12,"망고":0.10,"레몬":0.08}
DEFAULT_WEIGHT = 0.38 / (len(FLAVORS) - 5)

# =========================
# 유틸 함수
# =========================

def weighted_flavor_choice():
    pool = []
    for f in FLAVORS:
        pool.extend([f] * int(FLAVOR_WEIGHTS.get(f, DEFAULT_WEIGHT) * 100))
    return random.choice(pool)


def generate_fake_products(months: int):
    """
    - 월별 300건 가상 품목제조보고 생성
    - 포장형태, 음료제조회사 랜덤 부여
    """
    records = []
    today = datetime.today()
    for _ in range(months):
        for _ in range(300):
            f = weighted_flavor_choice()
            records.append({
                "보고일자": (today - timedelta(days=random.randint(0,30))).strftime("%Y-%m-%d"),
                "제품명": f"FRESHLAB {f} 스퀴지 주스",
                "플레이버": f,
                "제품유형": "주스류",
                "포장": random.choice(PACKAGING_TYPES),
                "음료제조회사": random.choice(BEVERAGE_COMPANIES),
            })
    return records


def calculate_top5_flavors(records):
    c = Counter(r["플레이버"] for r in records)
    total = sum(c.values())
    return [{"rank":i+1,"flavor":f,"share":round(cnt/total*100,1)} for i,(f,cnt) in enumerate(c.most_common(5))]


def analyze_with_openai(top5):
    try:
        from openai import OpenAI
        client = OpenAI()
        prompt = f"너는 식품 트렌드 전문가다. 다음 플레이버 점유율을 분석해 요약과 맛 설명을 JSON으로 출력하라: {top5}"
        resp = client.responses.create(model="o4-mini", input=prompt)
        return json.loads(resp.output_text)
    except Exception as e:
        st.session_state.ai_error = str(e)
        return None


def get_demo_image(flavor: str) -> str:
    seed = FLAVOR_EN_MAP.get(flavor, "fruit").replace(" ", "-")
    return f"https://picsum.photos/seed/{seed}/400/400"

# =========================
# UI – 입력
# =========================

st.title("🥤 ABC 제품개발 교육 시뮬레이터")
st.caption("AI 기반 제품기획–마케팅–개발 사고 훈련용")

st.sidebar.header("① 조건 설정")
months = st.sidebar.number_input("조회 개월 수",1,6,1)
run = st.sidebar.button("데이터 생성 및 분석")

if run:
    records = generate_fake_products(months)
    top5 = calculate_top5_flavors(records)
    with st.spinner("AI 분석 중..."):
        ai = analyze_with_openai(top5)
    st.session_state.records = records
    st.session_state.top5 = top5
    st.session_state.ai_result = ai

# =========================
# UI – 출력
# =========================

records = st.session_state.records
top5 = st.session_state.top5
ai = st.session_state.ai_result

if not records:
    st.info("좌측에서 실행하세요")
    st.stop()

st.subheader("📊 Top5 플레이버")
cols = st.columns(5)

for col, t in zip(cols, top5):
    f = t["flavor"]
    with col:
        st.image(get_demo_image(f), use_container_width=True)
        st.markdown(f"### {f}")
        st.caption(f"점유율 {t['share']}%")
        if st.button(f"이 맛으로 신제품 기획", key=f):
            st.session_state.selected_flavor = f

# =========================
# ② 카드 클릭 → 신규 제품 제안
# =========================

if st.session_state.selected_flavor:
    f = st.session_state.selected_flavor
    st.divider()
    st.subheader(f"🧠 AI 신규 제품 제안 – {f}")
    try:
        from openai import OpenAI
        client = OpenAI()
        prompt = f"{f} 플레이버를 기반으로 20대 타깃 음료 신제품 컨셉과 원료 조합을 제안하라."
        resp = client.responses.create(model="o4-mini", input=prompt)
        st.success(resp.output_text)
    except Exception:
        st.warning("AI 제안 실패")

# =========================
# ③ 신입사원 미션 모드
# =========================

st.divider()
st.subheader("🎯 신입사원 미션")

question = "다음 중 오렌지 플레이버 음료의 성공 가능성을 가장 높이는 요소는?"
options = [
    "원가가 가장 싸다",
    "사계절 소비 가능 + 친숙한 맛",
    "색상이 가장 진하다",
]

answer = st.radio(question, options)

if st.button("정답 확인"):
    if answer == options[1]:
        st.success("정답입니다. 대중성과 반복구매성이 핵심입니다.")
    else:
        st.error("오답입니다. 다시 생각해보세요.")

st.divider()
st.subheader("📋 가상 품목제조보고")
st.dataframe(records, use_container_width=True)
