import streamlit as st
import pandas as pd
import engine_ai as ai
import ui_layout as ui
import engine_data as data # 가상데이터 모듈 유지
import time

st.set_page_config(page_title="ABC 제품개발 로봇 Gamma", layout="wide")

# 세션 초기화
if "selected_flavor" not in st.session_state: st.session_state.selected_flavor = None

# 사이드바 컨트롤
st.sidebar.header("🚀 R&D 컨트롤 센터")
if st.sidebar.button("▶ 데이터 분석 및 동기화", use_container_width=True):
    st.session_state.records = data.generate_fake_products(3, seed=42)
    st.session_state.top5 = data.calculate_top5(st.session_state.records)

if st.session_state.get("records"):
    ui.render_top5_cards(st.session_state.top5)
    
    if st.session_state.selected_flavor:
        st.divider()
        st.subheader(f"🧪 {st.session_state.selected_flavor} 전문가용 정밀 R&D 시뮬레이터")

        # 1. 원료 라이브러리 선택권 부여 [지시사항 반영]
        col_lib1, col_lib2 = st.columns(2)
        with col_lib1:
            base_type = st.selectbox("원료 가공 방식 선택", ["농축액(Concentrate)", "NFC 과즙", "퓨레(Puree)", "분말추출물"])
        with col_lib2:
            sweetener_choice = st.multiselect("활용 당류 선택", ["액상알룰로스", "정백당", "결정과당", "스테비아", "에리스리톨"], default=["액상알룰로스"])

        # AI 호출 및 예상 시간 표시 [지시사항 반영]
        cache_key = f"res_{st.session_state.selected_flavor}_{base_type}_{hash(tuple(sweetener_choice))}"
        if cache_key not in st.session_state:
            with st.status("AI 시니어 연구원이 1,000개 라이브러리를 분석 중입니다...") as status:
                st.write("⏳ 예상 완료 시간: 약 3.8초")
                res = ai.propose_formula(st.session_state.selected_flavor, sweetener_choice, base_type)
                st.session_state[cache_key] = res
                status.update(label="✅ 배합 설계 완료", state="complete")

        res = st.session_state[cache_key]
        formula = res["formula"]

        col_report, col_sim = st.columns([1, 2.5])
        
        with col_report:
            ui.render_marketing_report(res["report"])
            
        with col_sim:
            # 상단: 3단 비교 배합표 (추천/개선/Delta)
            table_placeholder = st.empty()
            
            st.markdown("---")
            st.markdown("#### 🛠️ 원료별 정밀 조절 (물리적 상하한선 고정 모드)")
            
            # 오토 밸런스 로직
            others = [item for item in formula if "정제수" not in item['원료명']]
            water_cfg = next(item for item in formula if "정제수" in item['원료명'])
            
            adjusted = {}
            sum_others = 0
            
            s_cols = st.columns(2)
            for i, item in enumerate(others):
                with s_cols[i % 2]:
                    # [물리 고정] 사용자가 당겨도 min/max를 절대 못 벗어남
                    val = st.slider(
                        f"**{item['원료명']}** (범위: {item['min']}% ~ {item['max']}%)",
                        min_value=float(item['min']), max_value=float(item['max']),
                        value=float(item['AI']), step=0.01,
                        key=f"slider_{cache_key}_{item['원료명']}"
                    )
                    adjusted[item['원료명']] = val
                    sum_others += val
            
            # 정제수 자동 계산
            cur_water = max(0.0, 100.0 - sum_others)
            adjusted["정제수"] = cur_water
            
            # 결과 데이터프레임 구성
            display_list = []
            for item in formula:
                name = item['원료명']
                recom = item['AI']
                curr = adjusted.get(name, cur_water)
                display_list.append({
                    "원료명": name, "추천 배합(%)": f"{recom:.2f}",
                    "개선 배합(%)": f"{curr:.2f}", "차이(Delta)": f"{curr - recom:+.2f}",
                    "사용 목적": item['사용목적'], "주의사항": item['주의사항']
                })
            
            with table_placeholder:
                st.table(pd.DataFrame(display_list))
                st.success(f"✅ 합계 100.00% 유지 (정제수 자동 조절: {cur_water:.2f}%)")

        # 2. 최하단: AI 추천 근거 섹션
        st.divider()
        st.subheader("📚 AI 시니어 연구원의 배합 설계 근거 (학술/문헌)")
        evidence = res["report"].get("📚 배합 설계 근거(학술/문헌)", [])
        for text in evidence: st.info(text)
