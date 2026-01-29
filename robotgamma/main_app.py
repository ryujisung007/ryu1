import streamlit as st
import engine_data as data
import engine_ai as ai
import ui_layout as ui
import time

# 1. 페이지 초기 설정
st.set_page_config(page_title="ABC 제품개발 로봇", layout="wide")

# 세션 상태 관리
if "selected_flavor" not in st.session_state:
    st.session_state.selected_flavor = None
if "records" not in st.session_state:
    st.session_state.records = None

# 2. 사이드바 컨트롤러
st.sidebar.header("🚀 제품개발 컨트롤러")
months = st.sidebar.slider("분석 기간 설정 (개월)", 1, 6, 1)

if st.sidebar.button("▶ 시뮬레이션 실행", use_container_width=True):
    # 진행도 표시 (작업 단계별 안내)
    with st.status("데이터 분석 엔진 가동 중...", expanded=True) as status:
        st.write("📊 전국 품목제조보고 데이터 수집 및 정제 중...")
        recs = data.generate_fake_products(months, seed=int(time.time()))
        st.session_state.records = recs
        time.sleep(0.6)
        
        st.write("🔥 플레이버별 시장 점유율 분석 중...")
        st.session_state.top5 = data.calculate_top5(recs)
        time.sleep(0.6)
        
        st.write("🤖 AI 트렌드 인사이트 도출 중...")
        st.session_state.ai_top5 = ai.analyze_trends(st.session_state.top5)
        
        # 완료 신호 업데이트
        status.update(label="✅ 모든 데이터 분석 및 로드 완료!", state="complete", expanded=False)
    
    st.toast("제품 기획 분석이 완료되었습니다.", icon="✅")

# 3. 메인 레이아웃 순차 출력 (요구사항: 4 -> 1 -> 2 -> 3)
if st.session_state.records:
    # (4) 데이터 테이블 영역 (최상단)
    st.subheader("📋 실시간 음료류 품목제조보고 현황")
    st.dataframe(st.session_state.records, use_container_width=True, height=250)
    
    # (1) Top5 카드 영역
    ui.render_top5_cards(st.session_state.top5, st.session_state.ai_top5)
    
    # (2) 상세 설계 영역 (맛 선택 시 노출)
    if st.session_state.selected_flavor:
        # 안전한 데이터 호출 (engine_ai에서 에러 핸들링 완료)
        formula = ai.propose_formula(st.session_state.selected_flavor)
        ui.render_formula_section(st.session_state.selected_flavor, formula)
        
    # (3) 미션 영역 (최하단)
    ui.render_mission_section()
else:
    st.info("사이드바의 버튼을 눌러 시뮬레이션을 시작해주세요.")
