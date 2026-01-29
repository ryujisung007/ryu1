"""
ABC 제품개발 교육용 Streamlit 앱 (통합 완성본)
- st.stop() 제거: 어떤 상태에서도 레이아웃 붕괴 없음
- 레이아웃 고정: (4)테이블 → (1)Top5 → (2)A/B/C 탭(좌/우 분할 포함) → (3)미션
- Stepper가 실제로 작동(진행 상태를 제어/표시)
- 직무 선택(A/B/C/통합) 후 해당 직무 출력 중심으로 동작
- (2) 디테일 복원: A(기획)·B(마케팅 검증)·C(연구/관능/배합/공정)
- AI 호출 최소화 + 캐시 + 실패 시 폴백
- 이미지: picsum(안정) + 플레이버 컬러 배지로 의미 보완
"""

from __future__ import annotations

import json
import random
import hashlib
import time
from collections import Counter
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import streamlit as st

# 표/차트용(외부 설치 없이)
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
    "오렌지": "#FDBA74",
    "사과": "#86EFAC",
    "포도": "#C4B5FD",
    "망고": "#FACC15",
    "레몬": "#FDE047",
    "자몽": "#FB7185",
    "복숭아": "#FDA4AF",
    "파인애플": "#FCD34D",
    "딸기": "#F87171",
    "블루베리": "#818CF8",
    "유자": "#FDE68A",
    "배": "#A7F3D0",
}

PRODUCT_PREFIX = ["FRESHLAB", "VITAPOP", "NATURA", "JUICY+", "FRESHWAY"]
PRODUCT_STYLE = [
    "데일리 주스",
    "저당 클린 드링크",
    "비타민 부스트",
    "리프레시 음료",
    "클린 주스",
    "이뮨 부스트",
    "모닝 루틴 드링크",
    "애프터짐 리커버리",
]

# Top5가 자연스럽게 나오도록 가중치
FLAVOR_WEIGHTS = {
    "오렌지": 0.18,
    "사과": 0.14,
    "포도": 0.12,
    "망고": 0.10,
    "레몬": 0.08,
}
DEFAULT_WEIGHT = 0.38 / (len(FLAVORS) - 5)

# B 평가 가중치(요청 템플릿)
B_SCORE_ITEMS = [
    ("Company 적합성", "자사 제조/브랜드/채널 적합성", 0.20),
    ("원가 안정성", "원재료/공정 기준 원가 리스크", 0.20),
    ("제조 난이도", "기존 설비 기준 생산 용이성", 0.15),
    ("Customer 수용성", "기존 고객층과의 정합성", 0.15),
    ("반복구매 가능성", "루틴화/재구매 가능성", 0.20),
    ("차별화/확장성", "라인업/시즌/콜라보 확장", 0.10),
]

ROLE_OPTIONS = ["통합(ABC)", "A: 기획", "B: 마케팅", "C: 연구/개발"]


# =========================
# 세션 상태 초기화
# =========================
def init_state() -> None:
    defaults = {
        "seed": 0,
        "months": 1,
        "records": None,
        "top5": None,
        "selected_flavor": None,

        # stepper(출력/안내 기준)
        "step": 0,  # 0 미실행, 1 데이터, 2 플레이버선택, 3 AI 산출, 4 미션제출

        # 직무 모드
        "role": "통합(ABC)",

        # AI 캐시
        "ai_top5_cache": {},       # key: top5_hash -> dict
        "ai_a_cache": {},          # key: flavor_ctx_hash -> dict
        "ai_b_cache": {},          # key: flavor_ctx_hash -> dict
        "ai_c_cache": {},          # key: flavor_ctx_hash -> dict

        "ai_error": None,

        # 미션 점수
        "mission_submitted": False,
        "mission_score": 0,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


init_state()


# =========================
# 유틸: 해시/JSON 파싱/이미지/제품명
# =========================
def _sha(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:16]


def hash_top5(top5: List[Dict[str, Any]]) -> str:
    payload = [{"f": t["flavor"], "share": t["share"]} for t in top5]
    return _sha(json.dumps(payload, ensure_ascii=False, sort_keys=True))


def hash_flavor_ctx(flavor: str, top5: List[Dict[str, Any]]) -> str:
    ctx = {"flavor": flavor, "top5": [{"f": t["flavor"], "s": t["share"]} for t in top5]}
    return _sha(json.dumps(ctx, ensure_ascii=False, sort_keys=True))


def safe_json_loads(text: str) -> Optional[Dict[str, Any]]:
    if not text:
        return None
    try:
        return json.loads(text)
    except Exception:
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            return None
        try:
            return json.loads(text[start:end + 1])
        except Exception:
            return None


def get_demo_image(flavor_kr: str) -> str:
    # Cloud/Android 안정 우선: picsum
    seed = FLAVOR_EN_MAP.get(flavor_kr, "fruit juice").replace(" ", "-")
    return f"https://picsum.photos/seed/{seed}/480/480"


def random_product_name(rng: random.Random, flavor: str) -> str:
    brand = rng.choice(PRODUCT_PREFIX)
    style = rng.choice(PRODUCT_STYLE)

    # 35% 확률로 블렌드
    if rng.random() < 0.35:
        other = rng.choice([f for f in FLAVORS if f != flavor])
        name = f"{flavor}·{other}"
    else:
        name = flavor

    # 25% 확률로 기능 키워드 추가
    tag = ""
    if rng.random() < 0.25:
        tag = rng.choice(["제로슈가", "저당", "비타민C", "이뮨", "에너지", "콜라겐", "식이섬유"])
        tag = f" {tag}"

    return f"{brand} {name} {style}{tag}".strip()


# =========================
# 데이터 생성/집계
# =========================
def weighted_flavor_choice(rng: random.Random) -> str:
    pool: List[str] = []
    for f in FLAVORS:
        w = FLAVOR_WEIGHTS.get(f, DEFAULT_WEIGHT)
        pool.extend([f] * max(1, int(w * 100)))
    return rng.choice(pool)


def generate_fake_products(months: int, seed: int) -> List[Dict[str, Any]]:
    rng = random.Random(seed)
    today = datetime.today()
    records: List[Dict[str, Any]] = []

    for _ in range(months):
        for _ in range(300):
            flavor = weighted_flavor_choice(rng)
            report_date = today - timedelta(days=rng.randint(0, 30))
            records.append({
                "보고일자": report_date.strftime("%Y-%m-%d"),
                "제품명": random_product_name(rng, flavor),
                "플레이버": flavor,
                "제품유형": "주스류",
                "포장": rng.choice(PACKAGING_TYPES),
                "음료제조회사": rng.choice(BEVERAGE_COMPANIES),
            })
    return records


def calculate_top5_flavors(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    counter = Counter(r["플레이버"] for r in records)
    total = sum(counter.values()) or 1
    top5 = counter.most_common(5)

    out = []
    for i, (flavor, cnt) in enumerate(top5, start=1):
        out.append({
            "rank": i,
            "flavor": flavor,
            "count": cnt,
            "share": round(cnt / total * 100, 1),
        })
    return out


def company_top_flavors(records: List[Dict[str, Any]], top_n_companies: int = 10, top_k_flavors: int = 3) -> List[Dict[str, Any]]:
    by_company: Dict[str, List[str]] = {}
    for r in records:
        by_company.setdefault(r["음료제조회사"], []).append(r["플레이버"])

    company_counts = sorted(((c, len(v)) for c, v in by_company.items()), key=lambda x: x[1], reverse=True)
    company_counts = company_counts[:top_n_companies]

    rows = []
    for company, total in company_counts:
        c = Counter(by_company[company])
        for rank, (flavor, cnt) in enumerate(c.most_common(top_k_flavors), start=1):
            rows.append({
                "음료제조회사": company,
                "총건수": total,
                "플레이버순위": rank,
                "플레이버": flavor,
                "건수": cnt,
                "비중(%)": round(cnt / total * 100, 1),
            })
    return rows


# =========================
# AI 폴백 (A/B/C)
# =========================
def local_top5_analysis(top5: List[Dict[str, Any]]) -> Dict[str, Any]:
    summary = (
        "상위 플레이버는 '상큼함·데일리·친숙함' 축으로 수렴합니다. "
        "신규성은 '블렌드/저당/기능성' 조합에서 확보하는 전략이 유효합니다."
    )
    flavors = {}
    for t in top5:
        f = t["flavor"]
        share = t["share"]
        if share >= 15:
            level = "메인스트림"
        elif share >= 10:
            level = "성장형"
        else:
            level = "니치"
        flavors[f] = {
            "level": level,
            "market_comment": "대중성 기반(가격/채널/재구매)을 우선 확보하고, 기능/블렌드로 차별화합니다.",
            "taste_description": f"{f} 산미-단맛 밸런스를 '깔끔한 피니시' 중심으로 설계합니다."
        }
    return {"summary": summary, "flavors": flavors}


def local_A(selected_flavor: str, top5: List[Dict[str, Any]], top5_ai: Dict[str, Any]) -> Dict[str, Any]:
    concept_names = [
        f"{selected_flavor} 루틴-리프레시",
        f"{selected_flavor} 클린-스퀴지",
        f"{selected_flavor} 저당 부스트",
    ]
    return {
        "one_liner": f"{selected_flavor} 기반의 '데일리 상큼+클린' 포지션으로 20·30대 루틴 시장 공략",
        "opportunity": [
            "상위권 플레이버의 재구매 강점 + 저당/기능성으로 신규성 확보",
            "블렌드(시트러스/베리)로 '뉴니스'를 만들되 대중성 유지",
            "친환경 포장 메시지와 결합 시 브랜드 호감도 상승"
        ],
        "concept_names": concept_names,
        "risk_and_mitigation": [
            "산도 과다 → pH 목표 설정/완충염 설계",
            "향 손실 → 향료 투입/열이력 최적화",
            "클라우드 브레이크 → 안정제/이온강도/전단 관리"
        ],
        "proposed_blends": [
            f"{selected_flavor}+자몽(쓴맛 관리)",
            f"{selected_flavor}+레몬(산미 강조)",
            f"{selected_flavor}+블루베리(색/뉴니스)"
        ]
    }


def local_B(selected_flavor: str, a_concept: Dict[str, Any]) -> Dict[str, Any]:
    # 단순한 룰 기반 점수
    base_scores = {
        "Company 적합성": 4,
        "원가 안정성": 3,
        "제조 난이도": 4,
        "Customer 수용성": 4,
        "반복구매 가능성": 4,
        "차별화/확장성": 3,
    }
    # 트렌드 강조(저당/기능)면 차별화↑, 원가 리스크↑
    if "저당" in " ".join(a_concept.get("concept_names", [])):
        base_scores["차별화/확장성"] = min(5, base_scores["차별화/확장성"] + 1)
        base_scores["원가 안정성"] = max(1, base_scores["원가 안정성"] - 1)

    total = 0.0
    rows = []
    for k, desc, w in B_SCORE_ITEMS:
        s = float(base_scores.get(k, 3))
        total += s * w
        rows.append({"평가항목": k, "설명": desc, "점수(1~5)": s, "가중치": w, "가중점수": round(s * w, 3)})

    return {
        "score_table": rows,
        "total_score": round(total, 3),
        "positioning": [
            "20대 여성(운동/초년생): 가볍고 상큼·저당/클린 라벨",
            "30대 남성(여행/건강지출): 기능성(비타민/이뮨) + 프리미엄 패키지 인지"
        ],
        "channel_message": [
            "편의점/온라인: 루틴·저당 키워드",
            "헬스/짐 제휴: 운동 후 리커버리 메시지",
            "여행/아웃도어: 리프레시·수분 보충"
        ],
        "go_no_go": "Go (교육용 폴백 판단: 3.6 이상이면 Go 권장)"
    }


def local_C(selected_flavor: str) -> Dict[str, Any]:
    # 관능 목표(0~10 스케일)
    sensory = {
        "색 강도": 7.5,
        "과즙감": 7.0,
        "산미": 6.5,
        "단맛": 5.5,
        "바디": 5.0,
        "향 지속": 6.0,
        "청량감": 6.5,
    }

    # 10개 이상, 합계 100 보장(기존/A/B) + 연구원 배합(초기=기존)
    base = [
        ("정제수", 81.70),
        (f"NFC {selected_flavor} 과즙", 10.00),
        ("설탕", 4.20),
        ("구연산", 0.25),
        ("구연산삼나트륨", 0.18),
        ("천연향료", 0.45),
        ("비타민C", 0.05),
        ("펙틴", 0.12),
        ("CMC", 0.06),
        ("천연클라우드", 2.80),
        ("소금", 0.02),
        ("색소(베타카로틴)", 0.17),
    ]
    # 합계 보정(부동소수)
    total = sum(v for _, v in base)
    diff = round(100.0 - total, 2)
    base = [(k, (v + diff) if k == "정제수" else v) for k, v in base]

    # A: 저당/클린 - 설탕 일부 대체(에리스리톨), 산미 정리
    A = []
    for k, v in base:
        if k == "설탕":
            A.append(("설탕", round(v * 0.55, 2)))
            A.append(("에리스리톨", round(v * 0.45, 2)))
        elif k == "천연향료":
            A.append((k, round(v + 0.10, 2)))
        else:
            A.append((k, v))

    # B: 관능 차별화 - 과즙감/바디/향 지속
    B = []
    for k, v in base:
        if "과즙" in k:
            B.append((k, round(v + 1.20, 2)))
        elif k == "천연클라우드":
            B.append((k, round(v + 0.60, 2)))
        elif k == "정제수":
            B.append((k, round(v - 1.90, 2)))
        elif k == "천연향료":
            B.append((k, round(v + 0.15, 2)))
        else:
            B.append((k, v))

    def normalize(pairs: List[Tuple[str, float]]) -> List[Tuple[str, float]]:
        tot = sum(v for _, v in pairs)
        d = round(100.0 - tot, 2)
        out = []
        for k, v in pairs:
            if k == "정제수":
                out.append((k, round(v + d, 2)))
            else:
                out.append((k, v))
        return out

    A = normalize(A)
    B = normalize(B)

    ingredients = [k for k, _ in base]
    base_dict = {k: float(v) for k, v in base}
    a_dict = {k: float(v) for k, v in A}
    b_dict = {k: float(v) for k, v in B}

    return {
        "sensory_targets": sensory,
        "title_a": "AI 제안(A): 저당·클린 트렌드(설탕 일부 대체 + 깔끔한 피니시)",
        "title_b": "AI 제안(B): 관능 차별화(과즙감/바디/향 지속 강화)",
        "ingredients": ingredients,
        "기존배합비": base_dict,
        "AI제안A": a_dict,
        "AI제안B": b_dict,
        "연구원배합비": dict(base_dict),  # 초기값
        "process_notes": [
            "혼합(용해/분산) → 살균(열이력 최소화) → 냉각 → 향료 후첨(가능 시) → 충전",
            "rPET/Hot-fill 조건이면 충전온도/냉각 프로파일 최적화 필요",
            "cloud break 발생 시 pH·이온강도·안정제·전단·열이력 순으로 점검"
        ]
    }


# =========================
# OpenAI 호출(안전 래퍼 + 최소 호출 + 캐시)
# =========================
def call_openai_json_once(model: str, prompt: str, retries: int = 2, backoff: float = 1.2) -> Optional[Dict[str, Any]]:
    """
    - temperature 등 모델 비지원 파라미터 사용 금지
    - 실패 시 None
    - 재시도 제한(과호출 방지)
    """
    try:
        from openai import OpenAI
    except Exception:
        return None

    last_err = None
    for i in range(retries + 1):
        try:
            client = OpenAI()  # env/secrets 사용
            resp = client.responses.create(model=model, input=prompt)
            data = safe_json_loads(resp.output_text)
            if isinstance(data, dict):
                return data
            return None
        except Exception as e:
            last_err = e
            time.sleep(backoff * (i + 1))
    st.session_state.ai_error = str(last_err)
    return None


def ai_top5_analysis(top5: List[Dict[str, Any]]) -> Dict[str, Any]:
    key = hash_top5(top5)
    if key in st.session_state.ai_top5_cache:
        return st.session_state.ai_top5_cache[key]

    flavor_stats = [{"flavor": t["flavor"], "share": t["share"]} for t in top5]
    prompt = "\n".join([
        "너는 20년 경력의 식품음료 트렌드 분석 전문가다.",
        "아래 플레이버 점유율 데이터를 해석해 JSON만 출력하라(추가 텍스트 금지).",
        f"입력 데이터: {json.dumps(flavor_stats, ensure_ascii=False)}",
        "출력 스키마:",
        "{",
        '  "summary": "전체 트렌드 요약(2~3문장)",',
        '  "flavors": {',
        '    "플레이버명": {',
        '      "level": "메인스트림/성장형/니치",',
        '      "market_comment": "시장 해석(1문장)",',
        '      "taste_description": "소비자 관점 맛 설명(1~2문장)"',
        "    }",
        "  }",
        "}",
    ])

    with st.spinner("AI가 Top5 트렌드를 분석 중입니다..."):
        data = call_openai_json_once("o4-mini", prompt)

    if not data or "flavors" not in data:
        data = local_top5_analysis(top5)

    st.session_state.ai_top5_cache[key] = data
    return data


def ai_A(selected_flavor: str, top5: List[Dict[str, Any]], top5_ai: Dict[str, Any]) -> Dict[str, Any]:
    ctx_key = hash_flavor_ctx(selected_flavor, top5)
    if ctx_key in st.session_state.ai_a_cache:
        return st.session_state.ai_a_cache[ctx_key]

    prompt = "\n".join([
        "너는 식품기획자(A)다. 목표는 '떠오르는 신규 시장'에 진입할 신제품 컨셉 도출이다.",
        f"선택 플레이버: {selected_flavor}",
        f"Top5 맥락: {json.dumps([{'flavor':t['flavor'],'share':t['share']} for t in top5], ensure_ascii=False)}",
        f"Top5 AI 요약: {top5_ai.get('summary','')}",
        "요구사항: 아래 JSON만 출력(추가 텍스트 금지).",
        "{",
        '  "one_liner": "한 줄 컨셉",',
        '  "opportunity": ["기회 1","기회 2","기회 3"],',
        '  "concept_names": ["제품명 후보1","제품명 후보2","제품명 후보3"],',
        '  "proposed_blends": ["블렌드 조합1","블렌드 조합2","블렌드 조합3"],',
        '  "risk_and_mitigation": ["리스크/대응1","리스크/대응2","리스크/대응3"]',
        "}",
    ])

    with st.spinner("A(기획)가 컨셉을 도출 중입니다..."):
        data = call_openai_json_once("o4-mini", prompt)

    if not data:
        data = local_A(selected_flavor, top5, top5_ai)

    st.session_state.ai_a_cache[ctx_key] = data
    return data


def ai_B(selected_flavor: str, top5: List[Dict[str, Any]], a_data: Dict[str, Any], top5_ai: Dict[str, Any]) -> Dict[str, Any]:
    ctx_key = hash_flavor_ctx(selected_flavor, top5)
    if ctx_key in st.session_state.ai_b_cache:
        return st.session_state.ai_b_cache[ctx_key]

    prompt = "\n".join([
        "너는 식품음료 마케터(B)다. A의 컨셉안을 자사 관점 3C·SWOT으로 평가하고 점수화한다.",
        f"선택 플레이버: {selected_flavor}",
        f"A 컨셉(요약): {a_data.get('one_liner','')}",
        f"A 제품명 후보: {a_data.get('concept_names',[])}",
        f"Top5 AI 요약: {top5_ai.get('summary','')}",
        "평가항목(1~5):",
        "- Company 적합성(0.2), 원가 안정성(0.2), 제조 난이도(0.15), Customer 수용성(0.15), 반복구매 가능성(0.2), 차별화/확장성(0.1)",
        "요구사항: 아래 JSON만 출력(추가 텍스트 금지).",
        "{",
        '  "score_table": [',
        '    {"평가항목":"...","설명":"...","점수(1~5)":0,"가중치":0.0,"가중점수":0.0},',
        "    ...",
        "  ],",
        '  "total_score": 0.0,',
        '  "positioning": ["타깃/포지셔닝 1","2"],',
        '  "channel_message": ["채널/메시지 1","2","3"],',
        '  "go_no_go": "Go/No-Go 및 이유(1문장)"',
        "}",
    ])

    with st.spinner("B(마케팅)가 3C·SWOT 기반 평가 중입니다..."):
        data = call_openai_json_once("o4-mini", prompt)

    if not data or "score_table" not in data:
        data = local_B(selected_flavor, a_data)

    st.session_state.ai_b_cache[ctx_key] = data
    return data


def ai_C(selected_flavor: str, top5: List[Dict[str, Any]], a_data: Dict[str, Any], b_data: Dict[str, Any]) -> Dict[str, Any]:
    ctx_key = hash_flavor_ctx(selected_flavor, top5)
    if ctx_key in st.session_state.ai_c_cache:
        return st.session_state.ai_c_cache[ctx_key]

    prompt = "\n".join([
        "너는 20년차 음료개발 연구원(C)이다(관능/색상/상품성/차별화 최우선).",
        f"선택 플레이버: {selected_flavor}",
        f"A 컨셉: {a_data.get('one_liner','')}",
        f"B 마케팅 평가 총점: {b_data.get('total_score','')}",
        "요구사항:",
        "- 관능 목표 스펙(0~10): 색 강도, 과즙감, 산미, 단맛, 바디, 향 지속, 청량감",
        "- 배합비 3세트: 기존배합비, AI제안A(저당/클린), AI제안B(관능 차별화)",
        "- 원재료 10개 이상, 각 세트 합계=100(±0.3 허용)",
        "- 공정/품질 리스크 노트 3개",
        "아래 JSON만 출력(추가 텍스트 금지).",
        "{",
        '  "sensory_targets": {"색 강도":0,"과즙감":0,"산미":0,"단맛":0,"바디":0,"향 지속":0,"청량감":0},',
        '  "title_a": "...",',
        '  "title_b": "...",',
        '  "ingredients": ["원재료1","원재료2","...(10개 이상)"],',
        '  "기존배합비": {"원재료1":0.0, ...},',
        '  "AI제안A": {"원재료1":0.0, ...},',
        '  "AI제안B": {"원재료1":0.0, ...},',
        '  "process_notes": ["노트1","노트2","노트3"]',
        "}",
    ])

    with st.spinner("C(연구/개발)가 관능/배합/공정을 설계 중입니다..."):
        data = call_openai_json_once("o4-mini", prompt)

    # 최소 검증 + 폴백
    if not data or "ingredients" not in data or "기존배합비" not in data:
        data = local_C(selected_flavor)

    # 연구원배합비 초기화
    if "연구원배합비" not in data:
        data["연구원배합비"] = dict(data.get("기존배합비", {}))

    st.session_state.ai_c_cache[ctx_key] = data
    return data


# =========================
# Stepper 계산(실제 작동)
# =========================
def compute_step() -> int:
    step = 0
    if st.session_state.records is not None and st.session_state.top5 is not None:
        step = 1
    if step >= 1 and st.session_state.selected_flavor:
        step = 2
    # AI 산출물이 준비되었으면 step=3
    if step >= 2:
        top5 = st.session_state.top5 or []
        f = st.session_state.selected_flavor
        if f and top5:
            ctx_key = hash_flavor_ctx(f, top5)
            # A/B/C 중 하나라도 있으면 3 (교육용: 출력 가능 상태)
            if (ctx_key in st.session_state.ai_a_cache) or (ctx_key in st.session_state.ai_b_cache) or (ctx_key in st.session_state.ai_c_cache):
                step = 3
    if st.session_state.mission_submitted:
        step = 4
    return step


# =========================
# 차트(Top5, 관능 레이다)
# =========================
def plot_top5_bar(top5: List[Dict[str, Any]]) -> None:
    flavors = [t["flavor"] for t in top5]
    shares = [t["share"] for t in top5]
    fig = plt.figure()
    plt.bar(flavors, shares)
    plt.ylabel("Share (%)")
    plt.title("Top5 Flavor Share")
    st.pyplot(fig, clear_figure=True)


def plot_sensory_radar(sensory: Dict[str, float]) -> None:
    # 레이다 차트(간단 구현)
    labels = list(sensory.keys())
    values = [float(sensory[k]) for k in labels]
    values += values[:1]
    n = len(labels)

    import math
    angles = [2 * math.pi * i / n for i in range(n)]
    angles += angles[:1]

    fig = plt.figure()
    ax = plt.subplot(111, polar=True)
    ax.plot(angles, values)
    ax.fill(angles, values, alpha=0.15)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)
    ax.set_yticklabels([])
    ax.set_title("Sensory Target Radar (0~10)")
    st.pyplot(fig, clear_figure=True)


# =========================
# 배합비 표 + Δ + 연구원 슬라이더
# =========================
def sum_by_ingredients(ingredients: List[str], d: Dict[str, Any]) -> float:
    s = 0.0
    for k in ingredients:
        try:
            s += float(d.get(k, 0.0))
        except Exception:
            s += 0.0
    return float(round(s, 2))


def build_formula_table(c_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    ingredients = c_data.get("ingredients", [])
    base = c_data.get("기존배합비", {})
    a = c_data.get("AI제안A", {})
    b = c_data.get("AI제안B", {})
    r = c_data.get("연구원배합비", {})

    rows = []
    for ing in ingredients:
        base_v = float(base.get(ing, 0.0))
        a_v = float(a.get(ing, 0.0))
        b_v = float(b.get(ing, 0.0))
        r_v = float(r.get(ing, 0.0))
        rows.append({
            "원재료": ing,
            "기존(%)": round(base_v, 2),
            "AI A(%)": round(a_v, 2),
            "AI B(%)": round(b_v, 2),
            "연구원(%)": round(r_v, 2),
            "Δ(A-기존)": round(a_v - base_v, 2),
            "Δ(B-기존)": round(b_v - base_v, 2),
            "Δ(연구원-기존)": round(r_v - base_v, 2),
        })

    # 합계 행
    rows.append({
        "원재료": "합계",
        "기존(%)": sum_by_ingredients(ingredients, base),
        "AI A(%)": sum_by_ingredients(ingredients, a),
        "AI B(%)": sum_by_ingredients(ingredients, b),
        "연구원(%)": sum_by_ingredients(ingredients, r),
        "Δ(A-기존)": "",
        "Δ(B-기존)": "",
        "Δ(연구원-기존)": "",
    })
    return rows


def adjust_researcher_formula(c_data: Dict[str, Any], changed: Dict[str, float]) -> None:
    """
    연구원 슬라이더 변경분 반영 후, '정제수'를 자동 보정해 합계 100 유지.
    - 정제수 항목이 없으면 첫 원재료를 보정 대상으로 사용.
    """
    ingredients = c_data.get("ingredients", [])
    if not ingredients:
        return
    r = c_data.get("연구원배합비", {})
    if not isinstance(r, dict):
        r = {}

    # 반영
    for k, v in changed.items():
        r[k] = float(v)

    # 보정 타깃
    water_key = "정제수" if "정제수" in ingredients else ingredients[0]

    # 합계 계산(보정 전 water 제외)
    s = 0.0
    for k in ingredients:
        if k == water_key:
            continue
        s += float(r.get(k, 0.0))

    # water = 100 - sum(others)
    new_water = 100.0 - s
    if new_water < 0:
        new_water = 0.0
    r[water_key] = float(round(new_water, 2))

    c_data["연구원배합비"] = r


# =========================
# UI: Sidebar (직무 선택 + 실행)
# =========================
st.title("🥤 ABC 제품개발 교육 시뮬레이터")
st.caption("테이블 → Top5 → A/B/C(디테일) → 제조공정 미션")

st.sidebar.header("설정")

st.session_state.role = st.sidebar.radio("직무 모드", ROLE_OPTIONS, index=ROLE_OPTIONS.index(st.session_state.role))
months = st.sidebar.number_input("조회 개월 수", min_value=1, max_value=6, value=int(st.session_state.months), step=1)
st.session_state.months = int(months)

col_s1, col_s2 = st.sidebar.columns(2)
with col_s1:
    if st.button("🔄 seed 변경", use_container_width=True):
        st.session_state.seed = random.randint(1, 9_999_999)
with col_s2:
    run = st.button("▶ 실행", use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.caption("OpenAI 사용: Streamlit secrets/env에 OPENAI_API_KEY 설정 필요 (실패 시 자동 폴백)")


# =========================
# 실행: 데이터 생성 + Top5 AI 분석(캐시)
# =========================
if run:
    if not st.session_state.seed:
        st.session_state.seed = random.randint(1, 9_999_999)
    st.session_state.ai_error = None
    st.session_state.selected_flavor = None
    st.session_state.mission_submitted = False
    st.session_state.mission_score = 0

    records = generate_fake_products(months=st.session_state.months, seed=int(st.session_state.seed))
    top5 = calculate_top5_flavors(records)

    st.session_state.records = records
    st.session_state.top5 = top5

    # Top5 AI 분석(최소 호출)
    _ = ai_top5_analysis(top5)


# =========================
# Stepper(실제 진행)
# =========================
st.session_state.step = compute_step()
steps = ["① 데이터 생성", "② Top5 확인", "③ 직무별 분석(A/B/C)", "④ 미션 완료"]
cols = st.columns(4)
for i, label in enumerate(steps, start=1):
    with cols[i - 1]:
        if st.session_state.step >= i:
            st.success(label)
        else:
            st.info(label)

st.divider()


# =========================
# 메인 레이아웃 고정: (4) 테이블 → (1) Top5 → (2) A/B/C → (3) 미션
# =========================
records = st.session_state.get("records")
top5 = st.session_state.get("top5") or []
top5_ai = None

# ---------- (4) 테이블 ----------
st.subheader("📋 음료류 품목제조보고")
if records:
    st.dataframe(records, use_container_width=True, height=380)
    with st.expander("🏭 제조사별 Top 플레이버 랭킹(상위 10개 제조사 · Top3)", expanded=False):
        rows = company_top_flavors(records, top_n_companies=10, top_k_flavors=3)
        st.dataframe(rows, use_container_width=True, height=360)
else:
    st.info("좌측에서 ▶ 실행을 누르면 가상 데이터가 생성됩니다.")

st.divider()

# ---------- (1) Top5 ----------
st.subheader("🔥 Top5 플레이버")
if not records or not top5:
    st.info("데이터 생성 후 Top5가 표시됩니다.")
else:
    top5_ai = ai_top5_analysis(top5)
    st.info(top5_ai.get("summary", ""))

    # Top5 바 차트
    with st.expander("📈 Top5 점유율 차트", expanded=False):
        plot_top5_bar(top5)

    cols = st.columns(5)
    for col, t in zip(cols, top5):
        f = t["flavor"]
        selected = (st.session_state.selected_flavor == f)
        info = (top5_ai.get("flavors", {}) or {}).get(f, {})
        level = info.get("level", "")

        with col:
            # 카드 컨테이너
            st.markdown(
                f"""
                <div style="
                    border:3px solid {'#2563eb' if selected else '#e5e7eb'};
                    border-radius:14px;
                    padding:10px;
                    background:white;
                ">
                """,
                unsafe_allow_html=True
            )

            st.image(get_demo_image(f), use_container_width=True)

            st.markdown(
                f"""
                <div style="
                    background:{FLAVOR_COLOR.get(f, '#e5e7eb')};
                    color:#111827;
                    padding:4px 10px;
                    border-radius:999px;
                    font-size:12px;
                    display:inline-block;
                    margin-top:6px;
                    margin-bottom:6px;
                ">
                    {f}
                </div>
                """,
                unsafe_allow_html=True
            )

            st.markdown(f"**점유율 {t['share']}%**" + (f" · {level}" if level else ""))
            if info.get("taste_description"):
                st.caption(info.get("taste_description"))

            if selected:
                st.success("선택됨")
            else:
                if st.button("이 맛으로 기획", key=f"pick_{f}"):
                    st.session_state.selected_flavor = f
                    st.session_state.step = compute_step()

            st.markdown("</div>", unsafe_allow_html=True)

st.divider()

# ---------- (2) A/B/C 탭 + (좌/우 분할 포함) ----------
st.subheader("🧠🧪 직무별 출력 (A/B/C) + C 배합비(좌/우)")

if not records or not top5:
    st.info("Top5까지 생성되면 직무별 출력이 활성화됩니다.")
else:
    if not st.session_state.selected_flavor:
        st.info("Top5 카드에서 **이 맛으로 기획**을 눌러 선택하면 (2) 영역이 상세 출력됩니다.")
    else:
        f = st.session_state.selected_flavor
        # 기본 탭 포커스: 직무 선택 반영
        if st.session_state.role == "A: 기획":
            default_tab = 0
        elif st.session_state.role == "B: 마케팅":
            default_tab = 1
        elif st.session_state.role == "C: 연구/개발":
            default_tab = 2
        else:
            default_tab = 0

        tabA, tabB, tabC = st.tabs(["A: 식품기획", "B: 마케팅 검증", "C: 연구/개발(관능·배합·공정)"])

        # --- A ---
        with tabA:
            st.markdown(f"### A(기획) · 선택 플레이버: **{f}**")
            top5_ai = top5_ai or ai_top5_analysis(top5)
            a_data = ai_A(f, top5, top5_ai)

            st.markdown("#### 1) 한 줄 컨셉")
            st.info(a_data.get("one_liner", ""))

            c1, c2 = st.columns([1, 1])
            with c1:
                st.markdown("#### 2) 기회(Opportunity)")
                for x in a_data.get("opportunity", [])[:6]:
                    st.write(f"- {x}")
                st.markdown("#### 3) 블렌드 제안")
                for x in a_data.get("proposed_blends", [])[:6]:
                    st.write(f"- {x}")
            with c2:
                st.markdown("#### 4) 제품명 후보(자동 입력용)")
                for x in a_data.get("concept_names", [])[:6]:
                    st.write(f"- {x}")
                st.markdown("#### 5) 리스크 & 대응")
                for x in a_data.get("risk_and_mitigation", [])[:6]:
                    st.write(f"- {x}")

        # --- B ---
        with tabB:
            st.markdown(f"### B(마케팅) · 선택 플레이버: **{f}**")
            top5_ai = top5_ai or ai_top5_analysis(top5)
            a_data = ai_A(f, top5, top5_ai)
            b_data = ai_B(f, top5, a_data, top5_ai)

            st.markdown("#### 1) 3C·SWOT 기반 평가표(가중치/총점)")
            score_table = b_data.get("score_table", [])
            if isinstance(score_table, list) and score_table:
                st.dataframe(score_table, use_container_width=True, height=320)
            st.metric("종합점수(가중)", float(b_data.get("total_score", 0.0)))

            c1, c2 = st.columns([1, 1])
            with c1:
                st.markdown("#### 2) 타깃 포지셔닝")
                for x in b_data.get("positioning", [])[:6]:
                    st.write(f"- {x}")
                st.markdown("#### 3) Go/No-Go")
                st.info(b_data.get("go_no_go", ""))
            with c2:
                st.markdown("#### 4) 채널/메시지")
                for x in b_data.get("channel_message", [])[:8]:
                    st.write(f"- {x}")

        # --- C ---
        with tabC:
            st.markdown(f"### C(연구/개발) · 선택 플레이버: **{f}**")
            top5_ai = top5_ai or ai_top5_analysis(top5)
            a_data = ai_A(f, top5, top5_ai)
            b_data = ai_B(f, top5, a_data, top5_ai)
            c_data = ai_C(f, top5, a_data, b_data)

            # 관능 레이다
            st.markdown("#### 1) 목표 관능 스펙(0~10)")
            sensory = c_data.get("sensory_targets", {})
            if isinstance(sensory, dict) and sensory:
                c1, c2 = st.columns([1, 1])
                with c1:
                    st.dataframe([{"항목": k, "목표값(0~10)": float(v)} for k, v in sensory.items()], use_container_width=True)
                with c2:
                    plot_sensory_radar({k: float(v) for k, v in sensory.items()})

            st.markdown("#### 2) 배합비(10+ 원료 / 100% / Δ 포함) + 연구원 배합 슬라이더")
            st.caption(c_data.get("title_a", ""))
            st.caption(c_data.get("title_b", ""))

            left, right = st.columns([1, 1])

            # 좌: 연구원 슬라이더(정제수 자동 보정)
            with left:
                st.markdown("##### 2-A) 연구원 배합비(슬라이더)")
                ingredients = c_data.get("ingredients", [])
                base = c_data.get("기존배합비", {})
                if not ingredients:
                    st.warning("배합비 원재료가 없습니다(폴백 점검).")
                else:
                    st.caption("가이드: 몇 개 원재료만 조정해도 '정제수'가 자동 보정되어 합계 100을 유지합니다.")
                    changed = {}
                    # 핵심 원료만 슬라이더로 노출(전부 노출하면 너무 길어서 교육 UX 저하)
                    # 기준: 과즙/설탕/산/향/클라우드 + (있으면) 대체감미료
                    priority = []
                    for k in ingredients:
                        if ("과즙" in k) or (k in ["설탕", "구연산", "천연향료", "천연클라우드", "에리스리톨", "비타민C"]):
                            priority.append(k)
                    # 그래도 6개 미만이면 앞에서 채우기
                    for k in ingredients:
                        if k not in priority:
                            priority.append(k)
                        if len(priority) >= 8:
                            break

                    for ing in priority:
                        base_v = float(c_data.get("연구원배합비", {}).get(ing, base.get(ing, 0.0)))
                        changed[ing] = st.slider(
                            f"{ing} (%)",
                            min_value=0.0,
                            max_value=30.0 if ("과즙" in ing or ing == "정제수") else 15.0,
                            value=float(round(base_v, 2)),
                            step=0.05,
                            key=f"sl_{f}_{ing}"
                        )

                    if st.button("연구원 배합 적용(정제수 자동보정)", key=f"apply_research_{f}"):
                        adjust_researcher_formula(c_data, changed)
                        # 캐시에 업데이트(유지)
                        ctx_key = hash_flavor_ctx(f, top5)
                        st.session_state.ai_c_cache[ctx_key] = c_data
                        st.success("연구원 배합비가 적용되었습니다(정제수 자동 보정).")

            # 우: 비교 표 + Δ
            with right:
                st.markdown("##### 2-B) 배합비 비교표(기존 / AI A / AI B / 연구원) + Δ")
                table = build_formula_table(c_data)
                st.dataframe(table, use_container_width=True, height=560)

            st.markdown("#### 3) 공정/품질 리스크 노트")
            for x in c_data.get("process_notes", [])[:8]:
                st.write(f"- {x}")

        # step 갱신
        st.session_state.step = compute_step()

st.divider()

# ---------- (3) 미션 ----------
st.subheader("🎯 신입사원 미션(제조공정 포함)")

# 미션은 항상 보이되, 데이터/선택에 따라 난이도 안내
if not records:
    st.info("먼저 ▶ 실행으로 데이터를 만든 다음 미션을 진행하세요.")
else:
    st.markdown("### 미션 A: 기획·배합 판단")
    options_a1 = ["기존 배합비", "AI 제안(A) (저당·클린)", "AI 제안(B) (풍미 강화)"]
    ans_a1 = st.radio("A1) 대량생산/재현성/리스크 관점에서 가장 적합한 안은?", options_a1, key="mission_a1")

    st.markdown("### 미션 B: 제조공정 이해")
    options_b1 = [
        "원료계량 → 살균 → 혼합 → 충전",
        "원료계량 → 혼합 → 살균 → 충전",
        "혼합 → 원료계량 → 충전 → 살균",
    ]
    ans_b1 = st.radio("B1) NFC 과즙 기반 음료의 일반 공정 순서?", options_b1, key="mission_b1")

    options_b2 = ["원료 당도", "살균/충전 온도(Hot-fill 여부)", "향료 투입 시점", "교반 속도"]
    ans_b2 = st.radio("B2) rPET 병 사용 시 가장 유의해야 할 항목?", options_b2, key="mission_b2")

    options_b3 = ["당도", "산도(pH) 및 안정제(클라우드/펙틴) 설계", "라벨 디자인", "병 색상"]
    ans_b3 = st.radio("B3) 충전 후 혼탁(cloud break) 발생 시 1차 점검 항목?", options_b3, key="mission_b3")

    if st.button("미션 제출/채점", key="submit_mission"):
        score = 0
        # A1: 교육용 기본 정답(A)로 설정
        if ans_a1 == options_a1[1]:
            score += 1
        if ans_b1 == options_b1[1]:
            score += 1
        if ans_b2 == options_b2[1]:
            score += 1
        if ans_b3 == options_b3[1]:
            score += 1

        st.session_state.mission_submitted = True
        st.session_state.mission_score = score
        st.session_state.step = compute_step()

    if st.session_state.mission_submitted:
        st.metric("미션 점수(총 4점)", st.session_state.mission_score)
        if st.session_state.mission_score == 4:
            st.success("수료 수준: 공정·리스크·포장 연계를 매우 잘 이해하고 있습니다.")
        elif st.session_state.mission_score >= 3:
            st.warning("양호: 대부분 이해했으나, 포장-공정 조건과 품질 트러블슈팅을 한 번 더 복습하세요.")
        else:
            st.error("보완 필요: 공정 흐름(혼합→살균→충전)과 품질 리스크 포인트를 다시 학습하세요.")

        st.info(
            "해설 요약:\n"
            "- 공정 순서: 원료 계량 → 혼합(완전 용해/분산) → 살균(미생물/효소) → 충전(포장 적합 조건)\n"
            "- rPET: Hot-fill 시 내열/변형 리스크(충전온도/냉각) 관리\n"
            "- cloud break: pH/이온강도/안정제/열이력/전단 조건 점검"
        )

# =========================
# 하단: 오류 로그(항상 렌더)
# =========================
with st.expander("⚠️ AI/시스템 오류 로그(참고)", expanded=False):
    if st.session_state.get("ai_error"):
        st.write(st.session_state.ai_error)
    else:
        st.caption("현재 오류 없음")
"""
ABC 제품개발 교육용 Streamlit 앱 (이미지 의미 개선 버전)
- 플레이버 연관 Unsplash 이미지 적용
- 제품명 다양화
- AI 신규 제품 제안 & 배합비 설계 (좌/우 분할)
"""

from __future__ import annotations

import random
import json
from collections import Counter
from datetime import datetime, timedelta
from typing import Dict, List

import streamlit as st


# =========================
# 기본 설정
# =========================
st.set_page_config(page_title="ABC 제품개발 교육 시뮬레이터", layout="wide")


# =========================
# 상수 정의
# =========================
PACKAGING_TYPES = [
    "PET 병", "유리병", "알루미늄 캔",
    "종이팩", "무균팩", "파우치", "리필 파우치"
]

BEVERAGE_COMPANIES = [
    "롯데칠성음료", "코카콜라음료", "웅진식품", "동아오츠카",
    "빙그레", "매일유업", "CJ제일제당", "풀무원",
    "광동제약", "하이트진로음료", "팔도", "일화",
    "대상웰라이프", "농심", "SPC삼립", "해태htb",
    "정식품", "샘표", "남양유업", "오뚜기"
]

FLAVORS = [
    "오렌지", "사과", "포도", "망고", "레몬",
    "자몽", "복숭아", "파인애플", "딸기",
    "블루베리", "유자", "배"
]

FLAVOR_EN = {
    "오렌지": "orange",
    "사과": "apple",
    "포도": "grape",
    "망고": "mango",
    "레몬": "lemon",
    "자몽": "grapefruit",
    "복숭아": "peach",
    "파인애플": "pineapple",
    "딸기": "strawberry",
    "블루베리": "blueberry",
    "유자": "yuzu",
    "배": "pear",
}

PRODUCT_PREFIX = ["FRESHLAB", "VITAPOP", "NATURA", "FRESHWAY", "JUICY+"]
PRODUCT_STYLE = ["데일리 주스", "저당 드링크", "비타민 부스트", "리프레시 음료", "클린 주스"]


# =========================
# 세션 상태 초기화
# =========================
def init_state():
    defaults = {
        "records": None,
        "top5": None,
        "selected_flavor": None,
        "ai_concept": None,
        "ai_formula": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


init_state()


# =========================
# 유틸 함수
# =========================
def random_product_name(flavor: str) -> str:
    prefix = random.choice(PRODUCT_PREFIX)
    style = random.choice(PRODUCT_STYLE)
    if random.random() < 0.35:
        other = random.choice([f for f in FLAVORS if f != flavor])
        name = f"{flavor}·{other}"
    else:
        name = flavor
    return f"{prefix} {name} {style}"


def get_flavor_image(flavor_kr: str) -> str:
    flavor_en = FLAVOR_EN.get(flavor_kr, "fruit")
    query = f"{flavor_en},juice,drink,beverage"
    return f"https://source.unsplash.com/featured/480x480/?{query}"


def generate_fake_products(months: int, seed: int) -> List[Dict]:
    rng = random.Random(seed)
    today = datetime.today()
    records = []

    for _ in range(months):
        for _ in range(300):
            flavor = rng.choice(FLAVORS)
            records.append({
                "보고일자": (today - timedelta(days=rng.randint(0, 30))).strftime("%Y-%m-%d"),
                "제품명": random_product_name(flavor),
                "플레이버": flavor,
                "제품유형": "주스류",
                "포장": rng.choice(PACKAGING_TYPES),
                "음료제조회사": rng.choice(BEVERAGE_COMPANIES),
            })
    return records


def calculate_top5(records):
    c = Counter(r["플레이버"] for r in records)
    total = sum(c.values())
    return [{"flavor": f, "share": round(cnt / total * 100, 1)} for f, cnt in c.most_common(5)]


# =========================
# UI
# =========================
st.title("🥤 ABC 제품개발 교육 시뮬레이터")
st.caption("플레이버 의미 기반 이미지 · AI 제품기획 · 배합비 설계")

st.sidebar.header("조건 설정")
months = st.sidebar.slider("조회 개월 수", 1, 6, 1)
run = st.sidebar.button("실행")

if run:
    seed = random.randint(1, 999999)
    records = generate_fake_products(months, seed)
    st.session_state.records = records
    st.session_state.top5 = calculate_top5(records)
    st.session_state.selected_flavor = None

records = st.session_state.records
top5 = st.session_state.top5

if not records:
    st.info("좌측에서 조건을 설정하고 실행하세요.")
    st.stop()

st.subheader("Top 플레이버 트렌드")

cols = st.columns(5)
for col, t in zip(cols, top5):
    with col:
        st.image(get_flavor_image(t["flavor"]), use_container_width=True)
        st.markdown(f"**{t['flavor']}**")
        st.caption(f"점유율 {t['share']}%")
