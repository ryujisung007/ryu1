import streamlit as st
import pandas as pd
import engine_ai as ai
import ui_layout as ui
import engine_data as data
import time

st.set_page_config(page_title="ABC 제품개발 로봇 Gamma", layout="wide")

if "selected_flavor" not in st.session_state: st.session_state.selected_flavor = None

# 사이드바 컨트롤 센터 (검색 다각화)
st.sidebar.header("🔍 R&D 전문가용 컨트롤 센터")
with st.sidebar.expander("📅 검색 및 데이터 동기화", expanded=True):
    months = st.slider("분석 기간", 1, 12, 3)
    if st.sidebar.button("▶ 데이터 동기화", use_container_width=True):
        st.session_state.records = data.generate_fake_products(months, seed=int(time.time()))
        st.session_state.top5 = data.calculate_top5(st.session_state.records)
        st.session_state.selected_flavor = None

if st.session_state.get("records"):
    df_raw = pd.DataFrame(st.session_state.records)
    
    # 지시하신 회사별, 기간별 검색 필터
    with st.sidebar.expander("🏢 세부 필터링"):
        comps = st.multiselect("회사 선택", options=df_raw["음료제조회사"].unique())
        packs = st.multiselect("포장재 선택", options=df_raw["포장"].unique())
    
    f_df = df_raw.copy()
    if comps: f_df = f_df[f_df["음료제조회사"].isin(comps)]
    if packs: f_df = f_df[f_df["포장"].isin(packs)]

    st.subheader("📋 품목제조보고 데이터 현황 (필터 적용)")
    st.dataframe(f_df, use_container_width=True, height=200)
    ui.render_top5_cards(st.session_state.top5)
    
    if st.session_state.selected_flavor:
        st.divider()
        st.subheader(f"🧪 {st.session_state.selected_flavor} 전문가용 정밀 시뮬레이터")

        # 원료 라이브러리 및 당류 선택
        c1, c2 = st.columns(2)
        with c1: b_type = st.selectbox("원료 가공 방식", ["농축액", "NFC 과즙", "퓨레"])
        with c2: s_choice = st.multiselect("당류 선택", ["액상알룰로스", "정백당", "스테비아"], default=["액상알룰로스"])

        # AI 호출 및 데이터 무결성 체크
        ckey = f"final_v6_{st.session_state.selected_flavor}_{b_type}_{hash(tuple(s_choice))}"
        if ckey not in st.session_state:
            with st.status("AI 시니어 연구원이 1,000포인트 라이브러리 분석 중...") as s:
                st.write("⏳ 예상 완료 시간: 약 3.8초")
                res = ai.propose_formula(st.session_state.selected_flavor, s_choice, b_type)
                if res and "formula" in res:
                    st.session_state[ckey] = res
                    s.update(label="✅ 설계 완료", state="complete")
                else:
                    st.stop()

        res = st.session_state[ckey]
        formula = res["formula"]

        col_rep, col_sim = st.columns([1, 2.5])
        with col_rep: ui.render_marketing_report(res["report"])
        
        with col_sim:
            # 1. 추천배합표 최상단 고정
            table_spot = st.empty()
            
            st.markdown("---")
            st.markdown("#### 🛠️ 원료별 정밀 조절 (상하한선 물리 고정)")
            
            # 오토 밸런싱 로직 (정제수 제외)
            others = [i for i in formula if "정제수" not in i['원료명']]
            water_cfg = next((i for i in formula if "정제수" in i['원료명']), {"min": 50.0, "AI": 80.0})
            
            adj = {}
            sum_others = 0.0
            scols = st.columns(2)
            for i, item in enumerate(others):
                with scols[i % 2]:
                    # [무결성] 물리적 상하한선 고정 및 이탈 방지
                    v = st.slider(f"**{item['원료명']}** ({item['min']}%~{item['max']}%)", 
                                  float(item['min']), float(item['max']), float(item['AI']), 0.01,
                                  key=f"sld_v6_{ckey}_{item['원료명']}")
                    adj[item['원료명']] = v
                    sum_others += v
            
            # [무결성] 합계 100% 오토 밸런스
            cur_w = max(0.0, 100.0 - sum_others)
            adj["정제수"] = cur_w
            
            # 3단 비교 데이터 구성 (추천/개선/Delta)
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

        # 📚 하단 DBpia 등 국내외 학술 근거 섹션
        st.divider()
        st.subheader("📚 AI 시니어 연구원의 배합 설계 근거 및 학술 문헌")
        ev_list = res["report"].get("📚 배합 설계 근거 및 문헌", [])
        if ev_list:
            ev_cols = st.columns(len(ev_list))
            for idx, ev in enumerate(ev_list):
                with ev_cols[idx]:
                    st.info(f"**{ev.get('title')}**\n\n{ev.get('desc')}")
                    st.markdown(f"[🔍 DBpia 검색](https://www.dbpia.co.kr/search/topSearch?query={ev.get('title')})")
                    st.markdown(f"[🔍 RISS 검색](http://www.riss.kr/search/Search.do?query={ev.get('title')})")
