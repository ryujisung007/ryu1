import streamlit as st
import pandas as pd
import engine_ai as ai
import ui_layout as ui
import time

st.set_page_config(page_title="ABC 제품개발 로봇 Gamma", layout="wide")

# 사이드바: DB 로드 및 다각도 검색 필터
st.sidebar.header("📂 R&D 원료 데이터베이스")
uploaded_file = st.sidebar.file_uploader("원료 DB(CSV) 업로드", type="csv")

if uploaded_file:
    db_df = pd.read_csv(uploaded_file)
    st.sidebar.success("✅ DB 로드 완료")
    
    # [지시사항] 회사별, 포장재별 등 검색 다각화
    with st.sidebar.expander("🔍 DB 정밀 검색"):
        comp_filter = st.multiselect("회사별", options=db_df.get("제조사", ["정보없음"]).unique())
        pack_filter = st.multiselect("포장재별", options=db_df.get("포장", ["정보없음"]).unique())

    # 메인 시뮬레이션 섹션
    if st.session_state.get("selected_flavor"):
        st.subheader(f"🧪 {st.session_state.selected_flavor} DB 연동 시뮬레이터")
        
        # 2단계 당류 선택 UI
        c1, c2, c3 = st.columns([1, 1.5, 1.5])
        with c1: b_type = st.selectbox("가공 방식", ["농축액", "NFC", "퓨레"])
        sweet_lib = {"천연 감미": ["정백당"], "저칼로리": ["알룰로스"], "제로": ["스테비아"]}
        with c2: s_cat = st.selectbox("🍬 당감미 특성", list(sweet_lib.keys()))
        with c3: s_choice = st.multiselect("📋 주요 사용당", sweet_lib[s_cat], default=[sweet_lib[s_cat][0]])

        # AI 호출 (DB 필터링 기반)
        ckey = f"v_db_{st.session_state.selected_flavor}_{b_type}_{hash(tuple(s_choice))}"
        if ckey not in st.session_state:
            with st.status("AI 시니어 연구원이 플레이버 맞춤형 DB 분석 중...") as s:
                res = ai.propose_formula_with_flavor_db(st.session_state.selected_flavor, s_choice, b_type, db_df)
                st.session_state[ckey] = res
                s.update(label="✅ 배합 설계 완료", state="complete")

        res = st.session_state[ckey]
        if res and "formula" in res:
            # 추천배합표 최상단 고정 출력
            table_spot = st.empty()
            formula = res["formula"]
            
            st.markdown("---")
            st.markdown("#### 🛠️ 원료별 정밀 조절 (상하한선 물리 고정)")
            
            others = [i for i in formula if "정제수" not in i['원료명']]
            adj, sum_others = {}, 0.0
            scols = st.columns(2)
            
            for i, item in enumerate(others):
                with scols[i % 2]:
                    # [지시사항] 물리적 상하한선 고정 (min/max 이탈 불가)
                    v = st.slider(f"**{item['원료명']}** ({item['min']}%~{item['max']}%)", 
                                  float(item['min']), float(item['max']), float(item['AI']), 0.01,
                                  key=f"sld_{ckey}_{item['원료명']}")
                    adj[item['원료명']] = v
                    sum_others += v
            
            # [지시사항] 정제수 오토 밸런스 및 합계 100% 무결성
            cur_w = max(0.0, 100.0 - sum_others)
            adj["정제수"] = cur_w
            
            # 3단 대조 데이터 구성
            d_list = []
            for item in formula:
                nm, re_v = item['원료명'], item['AI']
                cu_v = adj.get(nm, cur_w)
                d_list.append({
                    "원료명": nm, "추천(%)": f"{re_v:.2f}", "개선(%)": f"{cu_v:.2f}",
                    "Delta": f"{cu_v - re_v:+.2f}", "목적": item['사용목적'], "주의사항": item['주의사항']
                })
            
            with table_spot:
                st.table(pd.DataFrame(d_list))
                st.success(f"✅ 합계 100.00% 자동 유지 중 (정제수: {cur_w:.2f}%)")

            # 하단 국내외 학술 근거 (DBpia, RISS 연동)
            st.divider()
            st.subheader("📚 AI 시니어 연구원의 배합 설계 근거 및 학술 문헌")
            for ev in res["report"].get("📚 배합 설계 근거 및 문헌", []):
                st.info(f"**{ev.get('title')}**\n{ev.get('desc')}")
                st.markdown(f"[🔍 DBpia 검색](https://www.dbpia.co.kr/search/topSearch?query={ev.get('title')})")
else:
    st.info("💡 사이드바에서 원료 DB(CSV)를 업로드하면 플레이버 맞춤형 분석이 시작됩니다.")
