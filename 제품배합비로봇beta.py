from __future__ import annotations  # 최상단으로 이동 (에러 해결 핵심)

"""
ABC 제품개발 교육용 Streamlit 앱 (통합 완성본)
- 에러 수정: from __future__ 구문을 코드 최상단으로 배치
- 레이아웃: (4)테이블 → (1)Top5 → (2)A/B/C 탭 → (3)미션
"""

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
# 상수
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

FLAVOR_COLOR = {
    "오렌지": "#FDBA74", "사과": "#86EFAC", "포도": "#C4B5FD",
    "망고": "#FACC15", "레몬": "#FDE047", "자몽": "#FB7185",
    "복숭아": "#FDA4AF", "파인애플": "#FCD34D", "딸기": "#F87171",
    "블루베리": "#818CF8", "유자": "#FDE68A", "배": "#A7F3D0",
}

PRODUCT_PREFIX = ["FRESHLAB", "VITAPOP", "NATURA", "JUICY+", "FRESHWAY"]
PRODUCT_STYLE = [
    "데일리 주스", "저당 클
