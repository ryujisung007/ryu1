import streamlit as st
import engine_data as data
import engine_ai as ai
import ui_layout as ui
import time
import pandas as pd

st.set_page_config(page_title="ABC 제품개발 로봇", layout="wide")

if "selected_flavor" not in st.session_state:
    st.session_state.selected_flavor = None
if "records" not in st.session_state:
    st.session_state.records = None

# 사이드바 컨트롤러
st.sidebar.header("🚀 제품개발 컨트롤러")
months = st.sidebar.slider("분석 기간 설정 (개월)", 1, 6, 1)

if st.sidebar.button("▶ 시뮬레이션 실행", use_container_width=True):
    with st.status("분석 엔진 가동 중...", expanded=True) as status:
        st.write("📊 데이터 수집 및 정제...")
        st.session_state.records = data.generate_fake_products(months, seed=int(time.time()))
        st.write("🔥 시장 점유율 분석...")
        st.session_state.top5 = data.calculate_top5(st.session_state.records)
        st.write("🤖 AI 인사이트 도출...")
        st.session_state.ai_top5 = ai.analyze_trends(st.session_state.top5)
        status.update(label="✅ 분석 완료!", state="complete", expanded=False)
    st.toast("분석이 완료되었습니다.", icon="✅")

# 메인 레이아웃 (4 -> 1 -> 2 -> 3)
if st.session_state.records:
    # (4) 데이터 테이블
    st.subheader("📋 실시간 음료류 품목제조보고 현황")
    st.dataframe(st.session_state.records, use_container_width=True, height=250)
    
    # (1) Top5 카드
    ui.render_top5_cards(st.session_state.top5, st.session_state.ai_top5)
    
    # (2) 상세 설계 영역
    if st.session_state.selected_flavor:
        formula_data = ai.propose_formula(st.session_state.selected_flavor)
        
        st.divider()
        st.subheader(f"🧪 {st.session_state.selected_flavor} 제품 상세 설계")
        
        col_report, col_slider = st.columns([1, 1.2])
        
        with col_report:
            # 개조식 마케팅 전략 보고
            ui.render_marketing_report(formula_data.get("marketing_strategy", {}))
            
        with col_slider:
            st.markdown("#### 🛠️ 연구원 전용 배합비 시뮬레이터")
            st.caption("AI 제안을 바탕으로 원재료 비중을 직접 조정하세요. (Total 100% 준수)")
            
            user_adjustments = {}
            current_table = formula_data.get("table", [])
            
            for item in current_table:
                ing_name = item["원재료"]
                ai_val = item["AI"]
                # 각 원재료별 슬라이더 생성
                user_adjustments[ing_name] = st.slider(
                    f"{ing_name} (%)", 0.0, 100.0, float(ai_val), step=0.01, key=f"slide_{ing_name}"
                )
            
            total_sum = sum(user_adjustments.values())
            st.markdown(f"### 현재 배합 합계: `{total_sum:.2f}%`")
            
            if abs(total_sum - 100.0) > 0.01:
                st.warning("⚠️ 모든 배합비의 합계가 100%가 되어야 합니다.")
            else:
                st.success("✅ 배합비 합계가 100%입니다. 생산 공정으로 전송 가능합니다.")
                if st.button("최종 배합비 확정 및 보고서 저장"):
                    st.write("최종 배합표:", user_adjustments)
                    st.toast("저장되었습니다!", icon="💾")

    # (3) 미션 영역
    ui.render_mission_section()
else:
    st.info("사이드바 버튼을 눌러 시뮬레이션을 시작하세요.")
