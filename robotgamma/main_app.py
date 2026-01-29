import streamlit as st
import pandas as pd
import engine_ai as ai
import ui_layout as ui
import engine_data as data
import time

st.set_page_config(page_title="ABC 제품개발 로봇 Gamma", layout="wide")

# 세션 초기화
if "selected_flavor" not in st.session_state: st.session_state.selected_flavor = None
if "records" not in st.session_state: st.session_state.records = None

# 🚀 컨트롤 센터 고도화 (멀티 조건 검색)
st.sidebar.header("🔍 R&D 멀티 컨트롤 센터")

with st.sidebar.expander("📅 검색 조건 설정", expanded=True):
    months = st.slider("분석 기간 (개월)", 1, 12, 3)
    # 지시하신 대로 소스코드 수정한 부분은 주석으로 명시하지 않고 기능으로 구현
    if st.button("▶ 데이터 동기화 및 분석", use_container_width=True):
        st.session_state.records = data.generate_fake_products(months, seed=int(time.time()))
        st.session_state.top5 = data.calculate_top5(st.session_state.records)
        st.session_state.selected_flavor = None

# 자료가 가진 컬럼조건으로 필터링 강화
if st.session_state.records:
    df_raw = pd.DataFrame(st.session_state.records)
    
    with st.sidebar.expander("🏢 세부 필터링", expanded=True):
        companies = st.multiselect("회사별 검색", options=df_raw["음료제조회사"].unique())
        packaging = st.multiselect("포장재별 검색", options=df_raw["포장"].unique())
    
    filtered_df = df_raw.copy()
    if companies:
        filtered_df = filtered_df[filtered_df["음료제조회사"].isin(companies)]
    if packaging:
        filtered_df = filtered_df[filtered_df["포장"].isin(packaging)]

    # 품목제조보고 데이터 출력
    st.subheader("📋 실시간 품목제조보고 데이터 (필터 적용)")
    st.dataframe(filtered_df, use_container_width=True, height=250)
    
    # 추천 플레이버 카드
    ui.render_top5_cards(st.session_state.top5)
    
    if st.session_state.selected_flavor:
        st.divider()
        st.subheader(f"🧪 {st.session_state.selected_flavor} 전문가용 정밀 R&D 시뮬레이터")

        # 원료 라이브러리 및 당류 선택
        c1, c2 = st.columns(2)
        with c1:
            base_type = st.selectbox("원료 가공 방식", ["농축액", "NFC 과즙", "퓨레", "분말추출물"])
        with c2:
            sweetener_choice = st.multiselect("당류 라이브러리", ["액상알룰로스", "정백당", "결정과당", "스테비아"], default=["액상알룰로스"])

        # AI 분석 및 예상 완료 시간 표시
        cache_key = f"res_{st.session_state.selected_flavor}_{base_type}_{hash(tuple(sweetener_choice))}"
        if cache_key not in st.session_state:
            with st.status("AI 시니어 연구원이 분석 중입니다...") as status:
                st.write("⏳ 예상 완료 시간: 약 3.8초")
                res = ai.propose_formula(st.session_state.selected_flavor, sweetener_choice, base_type)
                st.session_state[cache_key] = res
                status.update(label="✅ 분석 완료", state="complete")

        res = st.session_state.get(cache_key)
        if res:
            formula = res["formula"]
            col_report, col_sim = st.columns([1, 2.5])
            
            with col_report:
                ui.render_marketing_report(res["report"])
                
            with col_sim:
                st.markdown("##### 📊 AI 시니어 연구원 추천 표준 배합표 (SOP)")
                table_placeholder = st.empty() # 배합표 상단 배치
                
                st.markdown("---")
                st.markdown("#### 🛠️ 원료별 정밀 조절 (상하한선 물리 고정)")
                
                # 오토 밸런스 로직 구현
                others = [item for item in formula if "정제수" not in item['원료명']]
                adjusted = {}
                sum_others = 0
                s_cols = st.columns(2)
                
                for i, item in enumerate(others):
                    with s_cols[i % 2]:
                        # 슬라이더 상하한선 고정
                        val = st.slider(
                            f"**{item['원료명']}** ({item['min']}% ~ {item['max']}%)",
                            float(item['min']), float(item['max']), float(item['AI']), 0.01,
                            key=f"sld_{cache_key}_{item['원료명']}"
                        )
                        adjusted[item['원료명']] = val
                        sum_others += val
                
                cur_water = max(0.0, 100.0 - sum_others)
                adjusted["정제수"] = cur_water
                
                # 3단 비교 배합표 데이터 구성
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

            # 학술적 근거 최하단 표시
            st.divider()
            st.subheader("📚 AI 시니어 연구원의 배합 설계 근거")
            for text in res["report"].get("📚 배합 설계 근거(학술/문헌)", []):
                st.info(text)
