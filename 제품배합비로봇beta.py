"""
ABC 제품개발 교육용 Streamlit 앱 (안정화 + 레이아웃 개편 + 제조공정 미션 포함)
요구사항 반영:
1) 메인영역 출력 순서: (4)테이블 → (1)Top5 카드 → (2)좌/우 분할(컨셉/배합비) → (3)신입 미션(제조공정 포함)
2) (2) 우측: AI 추천 음료 배합비 테이블
   - 원재료 10개 이상
   - 백분율 배합비(합계 100)
   - 헤더: 기존배합비 / AI 제안(A) / AI 제안(B)
   - A/B는 트렌드 기반 맛 차별화 포인트를 제목/설명에 반영
3) 국내 포장형태/음료제조회사 컬럼 추가(포장은 기존컬럼 사용, 회사는 맨 우측)
4) 이미지: Unsplash 대신 picsum(Cloud/Android 안정)
5) OpenAI 텍스트 분석 정상 동작(OPENAI_API_KEY는 Streamlit secrets 환경변수로 설정되어 있다고 가정)
   - OpenAI 패키지 미설치/키 누락/요청 실패 시 로컬 fallback
6) API 과호출 방지: 해시 기반 캐시(Top5/선택플레이버)
"""

from __future__ import annotations

import json
import random
import time
import hashlib
from collections import Counter
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import streamlit as st


# =========================
# 기본 설정
# =========================
st.set_page_config(page_title="ABC 제품개발 교육 시뮬레이터", layout="wide")


# =========================
# 상수: 포장 형태 / 제조사 / 플레이버
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

# Top5가 자연스럽게 나오도록 가중치
FLAVOR_WEIGHTS = {
    "오렌지": 0.18,
    "사과": 0.14,
    "포도": 0.12,
    "망고": 0.10,
    "레몬": 0.08,
}
DEFAULT_WEIGHT = 0.38 / (len(FLAVORS) - 5)


# =========================
# 세션 상태 초기화 (AttributeError 방지)
# =========================
def init_state() -> None:
    defaults = {
        "records": None,
        "top5": None,
        "selected_flavor": None,

        # AI 결과 캐시
        "ai_top5_cache": {},       # key: top5_hash -> dict
        "ai_concept_cache": {},     # key: flavor_hash -> str
        "ai_formula_cache": {},     # key: flavor_hash -> dict

        "ai_error": None,
        "seed": 0,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


init_state()


# =========================
# 유틸: 해시/JSON 파싱/이미지
# =========================
def _sha(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:16]


def hash_top5(top5: List[Dict[str, Any]]) -> str:
    payload = [{"f": t["flavor"], "share": t["share"]} for t in top5]
    return _sha(json.dumps(payload, ensure_ascii=False, sort_keys=True))


def hash_flavor(flavor: str, top5: List[Dict[str, Any]]) -> str:
    # 선택 맛 + 현재 top5 맥락까지 포함해 캐시
    ctx = {"flavor": flavor, "top5": [{"f": t["flavor"], "s": t["share"]} for t in top5]}
    return _sha(json.dumps(ctx, ensure_ascii=False, sort_keys=True))


def safe_json_loads(text: str) -> Optional[Dict[str, Any]]:
    if not text:
        return None
    try:
        return json.loads(text)
    except Exception:
        # JSON만 출력하라고 해도 앞뒤로 설명이 붙는 경우가 있어 보정
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            return None
        try:
            return json.loads(text[start:end + 1])
        except Exception:
            return None


def get_demo_image(flavor_kr: str) -> str:
    # Streamlit Cloud에서 안정적인 데모 이미지
    seed = FLAVOR_EN_MAP.get(flavor_kr, "fruit juice").replace(" ", "-")
    return f"https://picsum.photos/seed/{seed}/480/480"


# =========================
# 가상 데이터 생성/집계
# =========================
def weighted_flavor_choice(rng: random.Random) -> str:
    pool: List[str] = []
    for f in FLAVORS:
        w = FLAVOR_WEIGHTS.get(f, DEFAULT_WEIGHT)
        pool.extend([f] * max(1, int(w * 100)))
    return rng.choice(pool)


def generate_fake_products(months: int, seed: int) -> List[Dict[str, Any]]:
    """
    - 월별 300건 가상 품목제조보고 생성
    - 포장: 기존 컬럼(포장)에 랜덤 포장형태 부여
    - 음료제조회사: 테이블 맨 우측 컬럼으로 추가
    """
    rng = random.Random(seed)
    records: List[Dict[str, Any]] = []
    today = datetime.today()

    for _ in range(months):
        for _ in range(300):
            flavor = weighted_flavor_choice(rng)
            report_date = today - timedelta(days=rng.randint(0, 30))
            records.append({
                "보고일자": report_date.strftime("%Y-%m-%d"),
                "제품명": f"FRESHLAB {flavor} 스퀴지 주스",
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
    """
    제조사별 Top 플레이버(요청 2번: 제조사별 랭킹)
    - 상위 제조사(top_n_companies): 총 건수 기준
    - 각 제조사별 top_k_flavors 반환
    """
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
# AI: 로컬 폴백(텍스트/배합)
# =========================
def local_top5_analysis(top5: List[Dict[str, Any]]) -> Dict[str, Any]:
    # 최소 UX 확보용(오프라인/오류 시)
    summary = "상위 플레이버는 상큼함/데일리 음용성 중심으로 수렴합니다. 친숙한 과일 기반이 강세입니다."
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
            "market_comment": "대중성/재구매 관점의 설계가 유리합니다.",
            "taste_description": f"{f} 기반의 산미-단맛 밸런스를 강화하고, 깔끔한 피니시를 강조합니다."
        }
    return {"summary": summary, "flavors": flavors}


def local_formula(flavor: str) -> Dict[str, Any]:
    """
    10개 이상 원재료, 100% 합계 보장
    """
    # 간단한 기본 레시피(예시)
    base = [
        ("정제수", 83.20),
        (f"NFC {flavor} 과즙", 10.00),
        ("설탕", 4.80),
        ("구연산", 0.25),
        ("구연산삼나트륨", 0.18),
        ("천연향료", 0.35),
        ("비타민C", 0.05),
        ("펙틴", 0.10),
        ("CMC", 0.05),
        ("소금", 0.02),
        ("베타카로틴(색소)", 0.03),
        ("천연클라우드", 1.00),
    ]
    # 합계 보정(부동소수 오차)
    total = sum(v for _, v in base)
    diff = round(100.0 - total, 2)
    base = [(k, v) for k, v in base]
    # 정제수에 차이 반영
    base = [(k, (v + diff) if k == "정제수" else v) for k, v in base]

    def to_rows(pairs):
        return [{"원재료": k, "배합(%)": round(v, 2)} for k, v in pairs]

    # A: 트렌드(저당/클린) → 설탕 일부를 에리스리톨로 치환
    A = []
    for k, v in base:
        if k == "설탕":
            A.append(("설탕", round(v * 0.55, 2)))
            A.append(("에리스리톨", round(v * 0.45, 2)))
        else:
            A.append((k, v))
    # B: 맛 차별화(과즙감/바디) → 과즙/클라우드 강화, 설탕 약간 감소
    B = []
    for k, v in base:
        if "과즙" in k:
            B.append((k, v + 1.20))
        elif k == "정제수":
            B.append((k, v - 1.50))
        elif k == "설탕":
            B.append((k, max(0.0, v - 0.20)))
        elif k == "천연클라우드":
            B.append((k, v + 0.50))
        else:
            B.append((k, v))

    # 합계 100 보정 함수
    def normalize(pairs):
        tot = sum(v for _, v in pairs)
        d = 100.0 - tot
        out = []
        for k, v in pairs:
            if k == "정제수":
                out.append((k, v + d))
            else:
                out.append((k, v))
        return out

    A = normalize(A)
    B = normalize(B)

    return {
        "title_a": "AI 제안(A): 저당·클린 트렌드 적용(설탕 일부 대체)",
        "title_b": "AI 제안(B): 과즙감·바디감 차별화(풍미 강화)",
        "rows": [x[0] for x in base],  # 원재료 리스트(표 정렬 기준)
        "기존배합비": {k: round(v, 2) for k, v in base},
        "AI제안A": {k: round(v, 2) for k, v in A},
        "AI제안B": {k: round(v, 2) for k, v in B},
    }


# =========================
# AI: OpenAI 호출(안전 래퍼)
# =========================
def openai_available() -> bool:
    try:
        import openai  # noqa
        return True
    except Exception:
        return False


def analyze_top5_with_openai(top5: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Top5 트렌드 분석(JSON)
    실패 시 로컬 폴백
    """
    try:
        from openai import OpenAI
        client = OpenAI()  # Streamlit secrets/env 사용

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

        resp = client.responses.create(model="o4-mini", input=prompt)
        data = safe_json_loads(resp.output_text)
        if not isinstance(data, dict) or "flavors" not in data:
            return local_top5_analysis(top5)
        return data
    except Exception as e:
        st.session_state.ai_error = str(e)
        return local_top5_analysis(top5)


def propose_concept_with_openai(selected_flavor: str, top5: List[Dict[str, Any]]) -> str:
    """
    (2) 좌측: 기존 내용(컨셉/마케팅 포인트) 생성
    실패 시 로컬 텍스트
    """
    try:
        from openai import OpenAI
        client = OpenAI()

        prompt = "\n".join([
            "너는 A(식품기획자)+B(마케터)+C(개발연구원) 관점을 통합한 시니어 제품개발 리드다.",
            f"선택 플레이버: {selected_flavor}",
            f"현재 Top5 맥락: {json.dumps([{'flavor':t['flavor'],'share':t['share']} for t in top5], ensure_ascii=False)}",
            "요구사항:",
            "- 신제품 컨셉(제품명 후보 2개 포함)",
            "- 핵심 USP 3개",
            "- 마케팅 포인트 3개(20대/30대 타깃 관점 혼합)",
            "- 제조/품질 리스크 포인트 2개와 대응",
            "출력은 한국어로, 불릿 구조로 간결히.",
        ])
        resp = client.responses.create(model="o4-mini", input=prompt)
        return resp.output_text.strip()
    except Exception as e:
        st.session_state.ai_error = str(e)
        return (
            f"- 제품 컨셉: {selected_flavor} 기반 상큼·데일리 포지션\n"
            "- USP: 클린 라벨 / 산미 밸런스 / 반복구매\n"
            "- 마케팅: 출근·운동 루틴 / 저당 강조 / 패키지 친환경\n"
            "- 리스크: 산도/클라우드 안정성, 향료 손실 → pH/공정조건 관리\n"
        )


def propose_formula_with_openai(selected_flavor: str) -> Dict[str, Any]:
    """
    (2) 우측: 배합비 테이블(JSON) 생성
    실패 시 로컬 폴백(10개 이상, 합계 100 보장)
    """
    try:
        from openai import OpenAI
        client = OpenAI()

        prompt = "\n".join([
            "너는 20년차 음료개발 연구원이다(관능/색상/상품성/차별화 중시).",
            f"타깃 플레이버: {selected_flavor}",
            "요구사항:",
            "- 음료 배합비를 3세트로 제안하라: 기존배합비, AI제안A, AI제안B",
            "- 각 세트는 '원재료 10개 이상'이고, 배합(%) 합계가 정확히 100이 되게 하라.",
            "- A는 트렌드(저당/클린/기능성) 기반의 맛 차별화",
            "- B는 관능(과즙감/바디/향 지속) 기반의 맛 차별화",
            "- 아래 JSON 스키마만 출력(추가 텍스트 금지):",
            "{",
            '  "title_a": "...",',
            '  "title_b": "...",',
            '  "ingredients": ["원재료1","원재료2", "... (10개 이상)"],',
            '  "기존배합비": {"원재료1": 0.0, ...},',
            '  "AI제안A": {"원재료1": 0.0, ...},',
            '  "AI제안B": {"원재료1": 0.0, ...}',
            "}",
        ])

        resp = client.responses.create(model="o4-mini", input=prompt)
        data = safe_json_loads(resp.output_text)
        if not isinstance(data, dict):
            return local_formula(selected_flavor)

        # 최소 검증
        ing = data.get("ingredients")
        base = data.get("기존배합비")
        a = data.get("AI제안A")
        b = data.get("AI제안B")
        if not (isinstance(ing, list) and len(ing) >= 10 and isinstance(base, dict) and isinstance(a, dict) and isinstance(b, dict)):
            return local_formula(selected_flavor)

        def sum100(d: Dict[str, Any]) -> bool:
            try:
                s = sum(float(d.get(k, 0.0)) for k in ing)
                return abs(s - 100.0) <= 0.5  # 모델 출력 오차 허용
            except Exception:
                return False

        if not (sum100(base) and sum100(a) and sum100(b)):
            return local_formula(selected_flavor)

        return {
            "title_a": str(data.get("title_a") or "AI 제안(A): 트렌드 적용(저당/클린)"),
            "title_b": str(data.get("title_b") or "AI 제안(B): 관능 차별화(바디/향 지속)"),
            "rows": ing,
            "기존배합비": {k: float(base.get(k, 0.0)) for k in ing},
            "AI제안A": {k: float(a.get(k, 0.0)) for k in ing},
            "AI제안B": {k: float(b.get(k, 0.0)) for k in ing},
        }
    except Exception as e:
        st.session_state.ai_error = str(e)
        return local_formula(selected_flavor)


# =========================
# 표 렌더링(배합비)
# =========================
def render_formula_table(formula: Dict[str, Any]) -> None:
    rows = formula["rows"]
    base = formula["기존배합비"]
    a = formula["AI제안A"]
    b = formula["AI제안B"]

    table = []
    for r in rows:
        table.append({
            "원재료": r,
            "기존배합비(%)": round(float(base.get(r, 0.0)), 2),
            "AI 제안(A)(%)": round(float(a.get(r, 0.0)), 2),
            "AI 제안(B)(%)": round(float(b.get(r, 0.0)), 2),
        })

    # 합계 행
    s_base = round(sum(x["기존배합비(%)"] for x in table), 2)
    s_a = round(sum(x["AI 제안(A)(%)"] for x in table), 2)
    s_b = round(sum(x["AI 제안(B)(%)"] for x in table), 2)
    table.append({
        "원재료": "합계",
        "기존배합비(%)": s_base,
        "AI 제안(A)(%)": s_a,
        "AI 제안(B)(%)": s_b,
    })

    st.caption(formula.get("title_a", ""))
    st.caption(formula.get("title_b", ""))
    st.dataframe(table, use_container_width=True, height=520)


# =========================
# UI: 사이드바(입력)
# =========================
st.title("🥤 ABC 제품개발 교육 시뮬레이터")
st.caption("데이터 → 트렌드 → 컨셉/배합 설계 → 제조공정 미션(교육용)")

st.sidebar.header("① 조건 설정")
months = st.sidebar.number_input("조회 개월 수", min_value=1, max_value=6, value=1, step=1)

col_s1, col_s2 = st.sidebar.columns(2)
with col_s1:
    if st.button("🔄 seed 변경", use_container_width=True):
        st.session_state.seed = random.randint(1, 9_999_999)
with col_s2:
    run = st.button("▶ 실행", use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.caption("OpenAI 사용: Streamlit secrets에 OPENAI_API_KEY가 설정되어 있어야 합니다.")


# =========================
# 실행(데이터 생성 + Top5 분석 캐시)
# =========================
if run:
    if not st.session_state.seed:
        st.session_state.seed = random.randint(1, 9_999_999)

    st.session_state.ai_error = None
    st.session_state.selected_flavor = None

    records = generate_fake_products(months=months, seed=int(st.session_state.seed))
    top5 = calculate_top5_flavors(records)

    # 캐시: Top5 분석
    key = hash_top5(top5)
    if key in st.session_state.ai_top5_cache:
        ai_top5 = st.session_state.ai_top5_cache[key]
    else:
        with st.spinner("AI가 Top5 트렌드를 분석 중입니다..."):
            ai_top5 = analyze_top5_with_openai(top5)
        st.session_state.ai_top5_cache[key] = ai_top5

    st.session_state.records = records
    st.session_state.top5 = top5
    st.session_state.ai_result = ai_top5


# =========================
# 메인 영역 출력 (요구 순서: 4 → 1 → 2 → 3)
# =========================
records = st.session_state.get("records")
top5 = st.session_state.get("top5")
ai_top5 = st.session_state.get("ai_result")

if records is None or top5 is None:
    st.info("좌측에서 조건을 설정하고 ▶ 실행을 눌러주세요.")
    st.stop()

# -------------------------
# (4) 가상 품목제조보고 테이블 (최상단)
# -------------------------
st.subheader("📋 (4) 가상 품목제조보고 (Raw Data)")
st.dataframe(records, use_container_width=True, height=380)

# 제조사별 Top 플레이버(요청 2번 이행)
with st.expander("🏭 제조사별 Top 플레이버 랭킹(상위 10개 제조사 · Top3)", expanded=False):
    rows = company_top_flavors(records, top_n_companies=10, top_k_flavors=3)
    st.dataframe(rows, use_container_width=True, height=360)

st.divider()

# -------------------------
# (1) Top5 플레이버 카드
# -------------------------
st.subheader("🔥 (1) Top5 플레이버 카드")
if ai_top5 and isinstance(ai_top5, dict):
    st.info(ai_top5.get("summary", ""))
cols = st.columns(5)

for col, t in zip(cols, top5):
    f = t["flavor"]
    info = (ai_top5 or {}).get("flavors", {}).get(f, {}) if isinstance(ai_top5, dict) else {}
    level = info.get("level", "")
    with col:
        st.image(get_demo_image(f), use_container_width=True)
        st.markdown(f"### {f}")
        st.caption(f"점유율 {t['share']}% · {level}".strip(" ·"))
        if st.button("이 맛으로 신제품 기획", key=f"pick_{f}"):
            st.session_state.selected_flavor = f

st.divider()

# -------------------------
# (2) 좌/우 분할: 컨셉(좌) + 배합비(우)
# -------------------------
st.subheader("🧠🧪 (2) AI 신규 제품 제안 & 배합비 설계 (좌/우 분할)")

if not st.session_state.selected_flavor:
    st.info("위 Top5 카드에서 **이 맛으로 신제품 기획**을 눌러주세요.")
else:
    f = st.session_state.selected_flavor
    flavor_key = hash_flavor(f, top5)

    left, right = st.columns(2)

    # (2) 왼쪽: 컨셉/마케팅/리스크
    with left:
        st.markdown(f"#### 🧠 컨셉/USP/마케팅 포인트 · 선택: **{f}**")
        if flavor_key in st.session_state.ai_concept_cache:
            concept_text = st.session_state.ai_concept_cache[flavor_key]
        else:
            with st.spinner("AI가 제품 컨셉을 구성 중입니다..."):
                concept_text = propose_concept_with_openai(f, top5)
            st.session_state.ai_concept_cache[flavor_key] = concept_text

        st.text_area("AI 컨셉 제안", value=concept_text, height=520)

    # (2) 오른쪽: 배합비 테이블(10개 이상, 100% 기반)
    with right:
        st.markdown("#### 🧪 AI 추천 음료 배합비 – 트렌드 적용을 통한 맛 차별화 제안")
        if flavor_key in st.session_state.ai_formula_cache:
            formula = st.session_state.ai_formula_cache[flavor_key]
        else:
            with st.spinner("AI가 배합비(기존/A/B)를 설계 중입니다..."):
                formula = propose_formula_with_openai(f)
            st.session_state.ai_formula_cache[flavor_key] = formula

        render_formula_table(formula)

st.divider()

# -------------------------
# (3) 신입사원 미션 (제조공정 포함)
# -------------------------
st.subheader("🎯 (3) 신입사원 미션 (기획·배합 + 제조공정 포함)")

tab_a, tab_b = st.tabs(["미션 A: 기획·배합 판단", "미션 B: 음료 제조공정 이해"])

with tab_a:
    st.markdown("**문제 A1**. 아래 중 *대량생산/재현성/리스크* 관점에서 가장 적합한 안을 고르세요.")
    options_a1 = ["기존 배합비", "AI 제안(A) (저당·클린)", "AI 제안(B) (풍미 강화)"]
    ans_a1 = st.radio("선택", options_a1, key="mission_a1")

    if st.button("정답 확인", key="check_a1"):
        # 교육용: 정답을 'A'로 두고, 해설 제공(고정)
        if ans_a1 == options_a1[1]:
            st.success("정답입니다. 저당·클린 설계는 반복구매/트렌드 적합성과 공정 안정성을 동시에 확보하기 쉽습니다.")
        else:
            st.error("오답입니다. 대량생산에서는 원가/공정/품질 리스크까지 함께 고려해야 합니다.")
        st.info("해설: A는 저당 트렌드와 라벨 설계를 반영하면서도, 과즙·산도·향 밸런스를 유지하는 방향이 핵심입니다.")

with tab_b:
    st.markdown("**문제 B1**. NFC 과즙 기반 음료(비탄산/탄산 공통)의 일반적인 공정 순서로 가장 타당한 것은?")
    options_b1 = [
        "원료계량 → 살균 → 혼합 → 충전",
        "원료계량 → 혼합 → 살균 → 충전",
        "혼합 → 원료계량 → 충전 → 살균",
    ]
    ans_b1 = st.radio("선택", options_b1, key="mission_b1")

    st.markdown("**문제 B2**. rPET 병을 사용할 때 공정에서 가장 유의해야 할 항목은?")
    options_b2 = [
        "원료 당도",
        "살균/충전 온도(Hot-fill 여부)",
        "향료 투입 시점",
        "교반 속도",
    ]
    ans_b2 = st.radio("선택", options_b2, key="mission_b2")

    st.markdown("**문제 B3**. 충전 후 혼탁(cloud break)이 발생했다. 가장 먼저 점검할 항목은?")
    options_b3 = [
        "당도",
        "산도(pH) 및 안정제(클라우드/펙틴) 설계",
        "라벨 디자인",
        "병 색상",
    ]
    ans_b3 = st.radio("선택", options_b3, key="mission_b3")

    if st.button("정답 확인", key="check_b"):
        score = 0
        if ans_b1 == options_b1[1]:
            score += 1
        if ans_b2 == options_b2[1]:
            score += 1
        if ans_b3 == options_b3[1]:
            score += 1

        if score == 3:
            st.success("3/3 정답. 공정 논리와 포장-공정 연계를 잘 이해하고 있습니다.")
        elif score == 2:
            st.warning("2/3 정답. 전반적으로 좋지만, 포장/품질 포인트를 한 번 더 정리해보세요.")
        else:
            st.error("0~1/3 정답. 제조공정 기본 흐름(혼합→살균→충전)과 리스크 포인트를 복습하세요.")

        st.info(
            "해설 요약:\n"
            "- 공정 순서: 원료 계량 → 혼합(완전 용해/분산) → 살균(미생물/효소) → 충전(포장 적합 조건)\n"
            "- rPET: Hot-fill 시 내열/변형 리스크 관리(충전온도/냉각)\n"
            "- cloud break: pH/이온강도/안정제/열이력/전단 조건 점검"
        )

# =========================
# 하단: 오류(있으면 표시)
# =========================
if st.session_state.get("ai_error"):
    with st.expander("⚠️ AI/시스템 오류 로그(참고)", expanded=False):
        st.write(st.session_state.ai_error)
