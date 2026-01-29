import streamlit as st
import pandas as pd
import engine_ai as ai
import ui_layout as ui
import time

st.set_page_config(page_title="ABC 제품개발 로봇 Gamma", layout="wide")

# 1. 사이드바: 전문가용 DB 업로드 및 컨트롤 센터
st.sidebar.header("📂 R&D 전용 데이터베이스")
uploaded_db = st.sidebar.file_uploader("원료 DB(CSV)를 업로드하세요", type="csv")

if uploaded_db:
    db_df = pd.read_csv(uploaded_db)
    st.sidebar.success("✅ 원료 DB 로드 완료")
    
    # [지시사항] 자료가 가진 컬럼조건으로 검색 다각화
    with st.sidebar.expander("🔍 DB 상세 검색"):
        search_cat = st.multiselect("원료 카테고리 필터", options=db_df["카테고리"].unique())
        if search_cat:
            st.dataframe(db_df[db_df["카테고리"].isin(search_cat)])

    # 메인 시뮬레이터 시작
    if st.session_state.get("selected_flavor"):
        st.subheader(f"🧪 {st.session_state.selected_flavor} DB 연동형 시뮬레이터")
        
        # 2단계 당류 선택 UI
        c1, c2, c3 = st.columns([1, 1.5, 1.5])
        with c1: b_type = st.selectbox("가공 방식", ["농축액", "NFC", "퓨레"])
        sweet_lib = {"천연 감미": ["정백당"], "저칼로리": ["알룰로스"], "제로": ["스테비아"]} # 예시
        with c2: s_cat = st.selectbox("🍬 당감미 특성", list(sweet_lib.keys()))
        with c3: s_choice = st.multiselect("📋 주요 사용당", sweet_lib[s_cat], default=[sweet_lib[s_cat][0]])

        # AI DB 분석 호출
        ckey = f"db_v1_{st.session_state.selected_flavor}_{b_type}_{hash(tuple(s_choice))}"
        if ckey not in st.session_state:
            with st.status("AI 시니어 연구원이 CSV DB 정밀 분석 중...") as s:
                res = ai.propose_formula_from_db(st.session_state.selected_flavor, s_choice, b_type, db_df)
                st.session_state[ckey] = res
                s.update(label="✅ DB 기반 설계 완료", state="complete")

        res = st.session_state[ckey]
        if res:
            # [무결성 보장] 상단 배합표 - 하단 물리 고정 슬라이더 레이아웃
            table_spot = st.empty()
            formula = res["formula"]
            
            others = [i for i in formula if "정제수" not in i['원료명']]
            adj, sum_others = {}, 0.0
            cols = st.columns(2)
            
            for i, item in enumerate(others):
                with cols[i % 2]:
                    # [지시사항] 물리적 상하한선 강제 고정
                    v = st.slider(f"**{item['원료명']}** ({item['min']}%~{item['max']}%)", 
                                  float(item['min']), float(item['max']), float(item['AI']), 0.01)
                    adj[item['원료명']] = v
                    sum_others += v
            
            # 정제수 오토 밸런스 및 합계 100% 검증
            cur_w = max(0.0, 100.0 - sum_others)
            adj["정제수"] = cur_w
            
            # 3단 대조 데이터 구성
            d_list = [{"원료명": k, "개선(%)": f"{v:.2f}"} for k, v in adj.items()]
            table_spot.table(pd.DataFrame(d_list)) # 상단 고정 출력
            
            # [지시사항] 하단 국내외 학술 근거 및 DBpia 링크
            st.divider()
            st.subheader("📚 학술 근거 및 국내외 논문 DB")
            for ev in res["report"].get("📚 배합 설계 근거 및 문헌", []):
                st.info(f"**{ev['title']}**\n{ev['desc']}")
                st.markdown(f"[🔍 DBpia 검색](https://www.dbpia.co.kr/search/topSearch?query={ev['title']})")
else:
    st.info("💡 사이드바에서 원료 데이터베이스(CSV)를 먼저 업로드해 주세요.")
