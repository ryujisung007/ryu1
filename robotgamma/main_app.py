import streamlit as st
import pandas as pd
import engine_ai as ai
import ui_layout as ui
import engine_data as data
import time
from datetime import datetime

st.set_page_config(page_title="ABC 제품개발 로봇 Gamma", layout="wide")

# 세션 초기화
if "selected_flavor" not in st.session_state: st.session_state.selected_flavor = None
if "records" not in st.session_state: st.session_state.records = None

# 🚀 3. 컨트롤 센터 고도화 (사이드바 검색 필터)
st.sidebar.header("🔍 R&D 멀티 컨트롤 센터")

with st.sidebar.expander("📅 기간 및 규모 설정", expanded=True):
    months = st.slider("분석 기간 (개월)", 1, 12, 3)
    target_count = st.number_input("조회 데이터 수", 100, 5000, 1000, step=100)

if st.sidebar.button("▶ 데이터 분석 및 동기화", use_container_width=True, type="primary"):
    st.session_state.records = data.generate_fake_products(months, seed=int(time.time()))
    st.session_state.top5 = data.calculate_top5(st.session_state.records)
    st.session_state.selected_flavor = None

# 데이터가 로드된 경우 필터링 옵션 활성화
if st.session_state.records:
    df_raw = pd.DataFrame(st.session_state.records)
    
    with st.sidebar.expander("🏢 기업 및 조건 필터", expanded=True):
        search_company = st.multiselect("제조회사 필터", options=df_raw["음료제조회사"].unique())
        search_pack = st.multiselect("포장재 필터", options=df_raw["포장"].unique())
    
    # 필터링 적용
    filtered_df = df_raw.copy()
    if search_company:
        filtered_df = filtered_df[filtered_df["음료제조회사"].isin(search_company)]
    if search_pack:
        filtered_df = filtered_df[filtered_df["포장"].isin(search_pack)]

    # 메인 화면: 품목제조보고 출력
    st.subheader("📋 실시간 음료류 품목제조보고 현황 (필터 적용)")
    st.dataframe(filtered_df, use_container_width=True, height=250)
    
    # 추천 카드 UI
    ui.render_top5_cards(st.session_state.top5)
    
    if st.session_state.selected_flavor:
        st.divider()
        st.subheader(f"🧪 {st.session_state.selected_flavor} 전문가용 정밀 R&D 시뮬레이터")

        # 원료 라이브러리 조건 설정
        c1, c2 = st.columns(2)
        with c1:
            base_type = st.selectbox("원료 가공 방식", ["농축액(72Brix)", "NFC 과즙", "퓨레", "분말추출물"])
        with c2:
            sweetener_choice = st.multiselect("당류 라이브러리", ["액상알룰로스", "정백당", "결정과당", "스테비아"], default=["액상알룰로스"])

        # AI 호출 및 예상 대기 시간 표시
        cache_key = f"res_{st.session_state.selected_flavor}_{base_type}_{hash(tuple(sweetener_choice))}"
        if cache_key not in st.session_state:
            with st.status("AI 시니어 연구원이 문헌 데이터를 분석 중입니다...") as status:
                st.write("⏳ 예상 완료 시간: 약 3.8초")
                # [오류 수정]: engine_ai.py의 인자 개수와 일치시킴
                res = ai.propose_formula(st.session_state.selected_flavor, sweetener_choice, base_type)
                st.session_state[cache_key] = res
                status.update(label="✅ 배합 설계 완료", state="complete")

        res = st.session_state.get(cache_key)
        if res:
            formula = res["formula"]
            col_report, col_sim = st.columns([1, 2.5])
            
            with col_report:
                ui.render_marketing_report(res["report"])
                
            with col_sim:
                st.markdown("##### 📊 AI 시니어 연구원 추천 표준 배합표 (SOP)")
                table_placeholder = st.empty()
                
                st.markdown("---")
                st.markdown("#### 🛠️ 원료별 정밀 조절 (물리적 상하한선 고정)")
                
                others = [item for item in formula if "정제수" not in item['원료명']]
                adjusted = {}
                sum_others = 0
                s_cols = st.columns(2)
                
                for i, item in enumerate(others):
                    with s_cols[i % 2]:
                        val = st.slider(
                            f"**{item['원료명']}** ({item['min']}%~{item['max']}%)",
                            float(item['min']), float(item['max']), float(item['AI']), 0.01,
                            key=f"sld_{cache_key}_{item['원료명']}"
                        )
                        adjusted[item['원료명']] = val
                        sum_others += val
                
                cur_water = max(0.0, 100.0 - sum_others)
                adjusted["정제수"] = cur_water
                
                # 3단 비교 데이터 구성
                display_list = []
                for item in formula:
                    name = item['원료명']
                    recom = item['AI']
                    curr = adjusted.get(name, cur_water)
                    display_list.append({
                        "원료명": name, "추천(%)": f"{recom:.2f}", "개선(%)": f"{curr:.2f}",
                        "Delta": f"{curr - recom:+.2f}", "목적": item['사용목적'], "주의사항": item['주의사항']
                    })
                
                with table_placeholder:
                    st.table(pd.DataFrame(display_list))
                    st.success(f"✅ 합계 100.00% 자동 유지 중 (정제수: {cur_water:.2f}%)")

            # 최하단 근거 섹션
            st.divider()
            st.subheader("📚 AI 시니어 연구원의 배합 설계 근거")
            for text in res["report"].get("📚 배합 설계 근거(학술/문헌)", []):
                st.info(text)
