import random
from datetime import datetime, timedelta
from collections import Counter
from typing import Any, Dict, List

# 상수 관리
PACKAGING_TYPES = ["PET 병", "유리병", "알루미늄 캔", "종이팩", "파우치", "스틱 파우치", "무균팩"]
BEVERAGE_COMPANIES = ["롯데칠성음료", "코카콜라음료", "웅진식품", "동아오츠카", "빙그레", "매일유업", "남양유업"]
FLAVORS = ["오렌지", "사과", "포도", "망고", "레몬", "자몽", "복숭아", "파인애플", "딸기", "블루베리", "유자", "배"]
FLAVOR_WEIGHTS = {"오렌지": 0.18, "사과": 0.14, "포도": 0.12, "망고": 0.10, "레몬": 0.08}
DEFAULT_WEIGHT = 0.38 / (len(FLAVORS) - 5)

def generate_fake_products(months: int, seed: int) -> List[Dict[str, Any]]:
    """가상 품목제조보고 데이터 생성 함수"""
    rng = random.Random(seed)
    records = []
    today = datetime.today()
    for _ in range(months * 300):
        flavor = rng.choices(FLAVORS, weights=[FLAVOR_WEIGHTS.get(f, DEFAULT_WEIGHT) for f in FLAVORS])[0]
        records.append({
            "보고일자": (today - timedelta(days=rng.randint(0, 30))).strftime("%Y-%m-%d"),
            "제품명": f"FRESHLAB {flavor} 스퀴지",
            "플레이버": flavor,
            "포장": rng.choice(PACKAGING_TYPES),
            "음료제조회사": rng.choice(BEVERAGE_COMPANIES),
        })
    return records

def calculate_top5(records: List[Dict[str, Any]]):
    """시장 점유율 계산 함수"""
    counter = Counter(r["플레이버"] for r in records)
    total = sum(counter.values()) or 1
    return [{"rank": i, "flavor": f, "share": round(c/total*100, 1)} 
            for i, (f, c) in enumerate(counter.most_common(5), 1)]
