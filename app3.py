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
