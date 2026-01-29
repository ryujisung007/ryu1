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
months = st.sidebar.slider("분석 기간 (개월)", 1, 6, 1)

if st.sidebar.button("▶ 시뮬레이션 실행", use_container_width=True):
    with st.status("분석 엔진 가동 중...", expanded=True) as status:
        st.write("📊 전국 품목제조보고 데이터 정제 중...")
        st.session_state.records = data.generate_fake_products(months, seed=int(time.time()))
        st.write("🔥 플레이버 점유율 분석 중...")
        st.session_state.top5 = data.calculate_top5(st.session_state.records)
        st.write("🤖 AI 인사이트 도출 중...")
        st.session_state.ai_top5 = ai.analyze_trends(st.session_state.top5)
        status.update(label="✅ 모든 데이터 분석 완료!", state="complete", expanded=False)
    st.toast("분석이 성공적으로 끝났습니다.", icon="✅")

# 3. 메인 출력 (순서: 4 -> 1 -> 2 -> 3)
if st.session_state.records:
    # (4) 데이터 테이블
    st.subheader("📋 실시간 음료류 품목제조보고 현황")
    st.dataframe(st.session_state.records, use_container_width=True, height=250)
    
    # (1) Top5 카드 영역
    ui.render_top5_cards(st.session_state.top5, st.session_state.ai_top5)
    
    # (2) 제품 상세 설계 영역
    if st.session_state.selected_flavor:
        # AI 전략 및 배합 제안 데이터 수령
        formula_data = ai.propose_formula(st.session_state.selected_flavor)
        
        st.divider()
        st.subheader(f"🥤 {st.session_state.selected_flavor} 제품 R&D 상세 설계")
        
        col_report, col_slider = st.columns([1, 1.2])
        
        with col_report:
            # 개조식 마케팅 전략 보고서 출력
            ui.render_marketing_report(formula_data.get("marketing_strategy", {}))
            
        with col_slider:
            st.markdown("#### 🛠️ 연구원 전용 배합비 시뮬레이터")
            st.caption("AI 제안값을 베이스로 실제 제조 배합비를 직접 조정하십시오. (Total 100%)")
            
            user_adjustments = {}
            current_table = formula_data.get("table", [])
            
            # 슬라이더 생성 루프
            for item in current_table:
                ing_name = item["원재료"]
                ai_val = item["AI"]
                user_adjustments[ing_name] = st.slider(
                    f"{ing_name} (%)", 0.0, 100.0, float(ai_val), step=0.01, key=f"slide_{ing_name}"
                )
            
            # 실시간 합계 검증
            total_sum = sum(user_adjustments.values())
            st.markdown(f"### 📊 현재 배합 합계: `{total_sum:.2f}%`")
            
            if abs(total_sum - 100.0) > 0.01:
                st.warning("⚠️ 합계가 100%가 되어야 생산 공정으로 전송할 수 있습니다.")
            else:
                st.success("✅ 완벽한 배합비입니다. 공정 표준서(SOP)를 생성할 수 있습니다.")
                if st.button("최종 배합비 확정 및 보고서 저장"):
                    st.balloons()
                    st.toast("저장 완료!", icon="💾")

    # (3) 미션 영역
    ui.render_mission_section()
else:
    st.info("사이드바 버튼을 눌러 시뮬레이션을 시작하세요.")
