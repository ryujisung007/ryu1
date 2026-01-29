"""
ABC 제품개발 Streamlit GUI 데모 (안정화 + 이미지 생성 버전)
- 가상 품목제조보고 데이터
- Top5 플레이버 분석
- OpenAI 실제 호출 기반 트렌드 해석 및 맛 설명
- OpenAI 이미지 생성(플레이버별 1장) + 캐시
- 세션 상태 방어, AI 실패 fallback, 진행 상태 표시

Author role:
- 20년 경력 AI 코딩 스택 전문가
- Streamlit 재실행 모델을 고려한 방어적 설계
- 가독성·안정성 최우선
"""

from __future__ import annotations

import streamlit as st
import random
from collections import Counter
from datetime import datetime, timedelta
import json
import time
import hashlib
from typing import Dict, Any, Optional

# =========================
# 설정
# =========================
st.set_page_config(page_title="ABC 제품개발 데모", layout="wide")

# =========================
# 세션 상태 초기화 (항상 먼저)
# =========================

def init_session_state():
    defaults = {
        "records": None,
        "top5": None,
        "ai_result": None,
        "ai_error": None,
        "last_run": None,
        "image_cache": {},  # flavor -> image_url
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session_state()

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
    "레몬": 0.08,
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
                "포장": "rPET 350mL",
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
            "share": round(count / total * 100, 1),
        })
    return result

# =========================
# OpenAI 실제 분석 (안전 래퍼)
# =========================

def analyze_with_openai_safe(top5):
    try:
        from openai import OpenAI
        client = OpenAI(api_key=st.secrets.get("OPENAI_API_KEY"))

        flavor_stats = [{"flavor": t["flavor"], "share": t["share"]} for t in top5]

        prompt = "\n".join([
            "너는 20년 경력의 식품음료 트렌드 분석 전문가다.",
            "아래는 최근 주스류 제품의 플레이버 점유율 데이터다.",
            f"플레이버 데이터: {flavor_stats}",
            "이 데이터를 해석하여 JSON으로만 응답하라.",
            "{",
            '  "summary": "전체 트렌드 요약",',
            '  "flavors": {',
            '    "플레이버명": {',
            '      "level": "메인스트림/성장형/니치",',
            '      "market_comment": "시장 해석",',
            '      "taste_description": "소비자 관점 맛 설명"',
            '    }',
            '  }',
            "}",
        ])

        resp = client.responses.create(
            model="o4-mini",
            input=prompt,
        )
        return json.loads(resp.output_text)

    except Exception as e:
        st.session_state.ai_error = str(e)
        return None


# =========================
# OpenAI 이미지 생성 (플레이버별 1장, 캐시)
# =========================

def generate_image_for_flavor(flavor: str) -> Optional[str]:
    if flavor in st.session_state.image_cache:
        return st.session_state.image_cache[flavor]

    try:
        from openai import OpenAI
        client = OpenAI(api_key=st.secrets.get("OPENAI_API_KEY"))

        prompt = (
            f"A realistic product photo of a bottled juice drink, flavor {flavor}, "
            "clear rPET bottle, minimal modern Korean beverage design, studio lighting"
        )

        img = client.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            size="512x512",
        )

        url = img.data[0].url
        st.session_state.image_cache[flavor] = url
        return url

    except Exception:
        return None


# =========================
# UI
# =========================

st.title("🥤 ABC 제품개발 GUI 데모")
st.caption("가상 데이터 + OpenAI 실제 분석 + 이미지 생성")

# --- Sidebar ---
st.sidebar.header("🔍 검색 조건")

months = st.sidebar.number_input(
    "조회 개월 수",
    min_value=1,
    max_value=6,
    value=1,
    step=1,
)

run = st.sidebar.button("검색 / 분석 실행")

# --- 실행 로직 ---
if run:
    st.session_state.ai_error = None
    st.session_state.last_run = time.time()

    records = generate_fake_products(months)
    top5 = calculate_top5_flavors(records)

    progress = st.progress(0)
    progress.progress(30)

    with st.spinner("AI가 플레이버 트렌드를 분석 중입니다..."):
        ai_result = analyze_with_openai_safe(top5)
        progress.progress(70)

    st.session_state.records = records
    st.session_state.top5 = top5
    st.session_state.ai_result = ai_result

    progress.progress(100)

# =========================
# Dashboard (방어)
# =========================

records = st.session_state.get("records")
top5 = st.session_state.get("top5")
ai = st.session_state.get("ai_result")
ai_error = st.session_state.get("ai_error")

if records is None or top5 is None:
    st.info("좌측에서 조건을 선택한 후 **검색 / 분석 실행**을 눌러주세요.")
    st.stop()

st.subheader("📊 실행 요약")
st.write(f"총 **{len(records)}건** 생성됨 · 최근 **{months}개월**")

st.divider()

if ai is None:
    st.warning("AI 분석 결과를 불러오지 못했습니다.\n\n" + (ai_error or "알 수 없는 오류"))
    st.stop()

st.subheader("🧠 AI 플레이버 트렌드 요약")
st.info(ai.get("summary", "요약 없음"))

st.divider()

st.subheader("🔥 Top5 플레이버")
for t in top5:
    f = t["flavor"]
    info = ai.get("flavors", {}).get(f)
    if info:
        st.write(f"{t['rank']}위 **{f}** – {t['count']}건 ({t['share']}%) · {info['level']}")

st.divider()

st.subheader("🧃 플레이버별 대표 제품 (AI 분석 + 이미지)")

cols = st.columns(5)
for col, t in zip(cols, top5):
    f = t["flavor"]
    info = ai.get("flavors", {}).get(f)
    if not info:
        continue

    with col:
        img_url = generate_image_for_flavor(f)
        if img_url:
            st.image(img_url, use_container_width=True)
        else:
            st.markdown("<div style='height:200px;background:#eee;text-align:center;line-height:200px;'>이미지 없음</d>
