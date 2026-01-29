import streamlit as st
import engine_data as data
import engine_ai as ai
import ui_layout as ui
import pandas as pd
import time

# 1. 초기 설정
st.set_page_config(page_title="ABC 제품개발 로봇 Gamma", layout="wide")

if "selected_flavor" not in st.session_state: st.session_state.selected_flavor = None
if "records" not in st.session_state: st.session_state.records = None

# 2. 사이드바 컨트롤
st.sidebar.header("🚀 R&D 컨트롤 센터")
months = st.sidebar.slider("분석 기간(개월)", 1, 6, 1)

if st.sidebar.button("▶ 시뮬레이션 실행", use_container_width=True):
    with st.status("분석 엔진 가동 중...", expanded=True) as status:
        st.session_state.records = data.generate_fake_products(months, seed=int(time.time()))
        st.session_state.top5 = data.calculate_top5(st.session_state.records)
        st.session_state.ai_top5 = ai.analyze_trends(st.session_state.top5)
        status.update(label="✅ 분석 완료!", state="complete", expanded=False)
    st.toast("데이터 로드 완료", icon="✅")

# 3. 메인 출력 레이아웃
if st.session_state.records:
    # (4) 품목제조보고 테이블
    st.subheader("📋 실시간 음료류 품목제조보고 데이터")
    st.dataframe(st.session_state.records, use_container_width=True, height=200)
    
    # (1) Top5 카드 영역
    ui.render_top5_cards(st.session_state.top5, st.session_state.ai_top5)
    
    # (2) R&D 설계 영역 (표 상단 - 슬라이더 하단)
    if st.session_state.selected_flavor:
        strategy, ingredients = ai.propose_formula(st.session_state.selected_flavor)
        st.divider()
        st.subheader(f"🧪 {st.session_state.selected_flavor} 제품 R&D 상세 설계 및 시뮬레이션")
        
        col_strat, col_formula = st.columns([1, 1.5])
        
        with col_strat:
            ui.render_marketing_report(strategy)
            
        with col_formula:
            # 2-1. 실시간 표 Placeholder (최상단 고정)
            table_spot = st.empty()
            
            st.markdown("---")
            st.markdown("#### 🛠️ 배합비 정밀 조절 패널 (하단 슬라이더)")
            
            # 2-2. 슬라이더 생성 및 값 수집
            user_values = {}
            s_cols = st.columns(2)
            for i, ing in enumerate(ingredients):
                with s_cols[i % 2]:
                    user_values[ing['원재료']] = st.slider(
                        f"{ing['원재료']} ({ing['role']})",
                        float(ing['min']), float(ing['max']), float(ing['AI']),
                        step=0.01, key=f"slide_{ing['원재료']}"
                    )
            
            # 2-3. 실시간 배합표 업데이트 (위쪽 Placeholder에 출력)
            total_sum = sum(user_values.values())
            summary_df = pd.DataFrame([
                {"원재료명": k, "배합비(%)": f"{v:.2f}%", "역할": next(x['role'] for x in ingredients if x['원재료'] == k)}
                for k, v in user_values.items()
            ])
            
            with table_spot:
                st.markdown(f"##### 📊 실시간 배합 현황 (Total: **{total_sum:.2f}%**)")
                st.table(summary_df)
                if abs(total_sum - 100.0) < 0.01:
                    st.success("✅ 합계 100% 충족: 생산 SOP 확정 가능")
                else:
                    st.warning(f"⚠️ 합계 오류: 현재 {total_sum:.2f}% (100.00%를 맞춰주세요)")

    # (3) 미션 영역
    ui.render_mission_section()
