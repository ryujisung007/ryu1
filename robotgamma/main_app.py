import streamlit as st
import pandas as pd
import engine_ai as ai
import ui_layout as ui
import engine_data as data
import time

st.set_page_config(page_title="ABC 제품개발 로봇 Gamma", layout="wide")

# 세션 관리
if "selected_flavor" not in st.session_state: st.session_state.selected_flavor = None

# 사이드바: 멀티 필터 컨트롤 센터
st.sidebar.header("🔍 R&D 멀티 컨트롤 센터")
with st.sidebar.expander("📅 검색 조건", expanded=True):
    months = st.slider("분석 기간", 1, 12, 3)
    if st.sidebar.button("▶ 데이터 동기화 및 분석", use_container_width=True):
        st.session_state.records = data.generate_fake_products(months, seed=int(time.time()))
        st.session_state.top5 = data.calculate_top5(st.session_state.records)
        st.session_state.selected_flavor = None

if st.session_state.get("records"):
    df_raw = pd.DataFrame(st.session_state.records)
    # 회사별, 포장재별 필터 적용
    companies = st.sidebar.multiselect("회사별 필터", options=df_raw["음료제조회사"].unique())
    f_df = df_raw[df_raw["음료제조회사"].isin(companies)] if companies else df_raw
    
    st.subheader("📋 실시간 품목제조보고 데이터 현황")
    st.dataframe(f_df, use_container_width=True, height=200)
    ui.render_top5_cards(st.session_state.top5)
    
    if st.session_state.selected_flavor:
        st.divider()
        st.subheader(f"🧪 {st.session_state.selected_flavor} 전문가용 정밀 시뮬레이터")

        # 원료 라이브러리 설정
        c1, c2 = st.columns(2)
        with c1: b_type = st.selectbox("가공 방식", ["농축액", "NFC 과즙", "퓨레"])
        with c2: s_choice = st.multiselect("당류 선택", ["액상알룰로스", "정백당", "스테비아"], default=["액상알룰로스"])

        # AI 호출 및 예상 시간
        ckey = f"final_{st.session_state.selected_flavor}_{b_type}_{hash(tuple(s_choice))}"
        if ckey not in st.session_state:
            with st.status("AI 시니어 연구원이 정밀 설계 중...") as s:
                st.write("⏳ 예상 완료 시간: 약 3.8초")
                st.session_state[ckey] = ai.propose_formula(st.session_state.selected_flavor, s_choice, b_type)
                s.update(label="✅ 설계 완료", state="complete")

        res = st.session_state[ckey]
        if res:
            col_rep, col_sim = st.columns([1, 2.5])
            with col_rep: ui.render_marketing_report(res["report"])
            
            with col_sim:
                # 1. 추천배합표 출력 보장 (상단 배치)
                st.markdown("##### 📊 AI 시니어 연구원 표준/개선 배합표 (SOP)")
                table_spot = st.empty()
                
                st.markdown("---")
                st.markdown("#### 🛠️ 원료별 정밀 조절 (상하한선 물리 고정)")
                
                # 오토 밸런스 로직 (정제수 제외)
                formula = res["formula"]
                others = [i for i in formula if "정제수" not in i['원료명']]
                water_cfg = next(i for i in formula if "정제수" in i['원료명'])
                
                adj = {}
                sum_others = 0
                scols = st.columns(2)
                for i, item in enumerate(others):
                    with scols[i % 2]:
                        # [무결성 2] 물리적 상하한선 강제 고정
                        v = st.slider(f"**{item['원료명']}** ({item['min']}%~{item['max']}%)", 
                                      float(item['min']), float(item['max']), float(item['AI']), 0.01,
                                      key=f"sld_{ckey}_{item['원료명']}")
                        adj[item['원료명']] = v
                        sum_others += v
                
                # [무결성 2] 합계 100% 오토 밸런스
                cur_w = max(0.0, 100.0 - sum_others)
                adj["정제수"] = cur_w
                
                # 3단 데이터 구성
                d_list = []
                for item in formula:
                    name = item['원료명']
                    re = item['AI']
                    cu = adj.get(name, cur_w)
                    d_list.append({
                        "원료명": name, "추천(%)": f"{re:.2f}", "개선(%)": f"{cu:.2f}",
                        "Delta": f"{cu - re:+.2f}", "목적": item['사용목적'], "주의사항": item['주의사항']
                    })
                
                with table_spot:
                    st.table(pd.DataFrame(d_list))
                    st.success(f"✅ 합계 100.00% 자동 유지 중 (정제수: {cur_w:.2f}%)")

            # [무결성 1] 하단 학술 근거 및 외부 링크
            st.divider()
            st.subheader("📚 AI 시니어 연구원의 배합 설계 근거 및 문헌")
            ev_cols = st.columns(len(res["report"]["📚 배합 설계 근거 및 문헌"]))
            for idx, ev in enumerate(res["report"]["📚 배합 설계 근거 및 문헌"]):
                with ev_cols[idx]:
                    st.info(f"**{ev['title']}**\n\n{ev['desc']}")
                    st.markdown(f"[🔗 관련 문헌/사이트 검색]({ev['url']})")
