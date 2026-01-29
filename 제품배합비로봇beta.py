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

# =========================
# 기본 설정
# =========================
st.set_page_config(page_title="ABC 제품개발 교육 시뮬레이터", layout="wide")

# =========================
# 상수 (에러 수정 완료)
# =========================
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

FLAVOR_EN_MAP: Dict[str, str] = {
    "오렌지": "orange juice", "사과": "apple juice", "포도": "grape juice",
    "망고": "mango juice", "레몬": "lemon citrus drink", "자몽": "grapefruit citrus drink",
    "복숭아": "peach juice", "파인애플": "pineapple juice", "딸기": "strawberry juice",
    "블루베리": "blueberry juice", "유자": "yuzu citrus drink", "배": "pear juice"
}

FLAVOR_COLOR = {
    "오렌지": "#FDBA74", "사과":
