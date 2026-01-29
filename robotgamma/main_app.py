import streamlit as st
import engine_data as data
import engine_ai as ai
import ui_layout as ui
import time

# 1. 초기 설정
st.set_page_config(page_title="ABC 제품개발 로봇", layout="wide")

if "selected_flavor" not in st.session_state:
    st.session_state.selected_flavor = None

# 2. 사이드바 제어
st.sidebar.header("🚀 제품개발 컨트롤러")
months = st.sidebar.slider("분석 기간 (개월)", 1, 6, 1)

if st.sidebar.button("▶ 시뮬레이션 실행"):
    # 진행도 표시 (st.status 활용)
    with st.status("데이터 엔진 구동 중...", expanded=True) as status:
        st.write("📊 품목제조보고 데이터 생성...")
        recs = data.generate_fake_products(months, seed=42)
        st.session_state.records = recs
        
        st.write("🔥 시장 점유율 계산...")
        st.session_state.top5 = data.calculate_top5(recs)
        
        st.write("🤖 AI 트렌드 분석...")
        st.session_state.ai_top5 = ai.analyze_trends(st.session_state.top5)
        
        status.update(label="✅ 분석 완료!", state="complete", expanded=False)
    st.toast("기획 준비가 완료되었습니다!", icon="🥤")

# 3. 메인 화면 출력 순서 (요구사항 반영)
if "records" in st.session_state:
    # (4) 데이터 테이블
    st.subheader("📋 실시간 품목제조보고")
    st.dataframe(st.session_state.records, use_container_width=True, height=250)
    
    # (1) Top5 카드
    ui.render_top5_cards(st.session_state.top5, st.session_state.ai_top5)
    
    # (2) 선택된 맛에 대한 상세 설계
    if st.session_state.selected_flavor:
        # AI로부터 상세 배합 데이터 수령 (캐시 적용)
        formula = ai.propose_formula(st.session_state.selected_flavor)
        ui.render_formula_section(st.session_state.selected_flavor, formula)
        
    # (3) 미션
    ui.render_mission_section()
