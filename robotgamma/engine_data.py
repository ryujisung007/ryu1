import streamlit as st
import engine_data as data
import engine_ai as ai
import ui_layout as ui
import pandas as pd
import time

# 1. 페이지 설정
st.set_page_config(page_title="ABC 제품개발 로봇 Gamma", layout="wide")

# 세션 상태 초기화
if "selected_flavor" not in st.session_state:
    st.session_state.selected_flavor = None
if "records" not in st.session_state:
    st.session_state.records = None

# 2. 사이드바 제어
st.sidebar.header("🚀 R&D 컨트롤 센터")
months = st.sidebar.slider("조회 기간(개월)", 1, 6, 1)

if st.sidebar.button("▶ 시뮬레이션 가동", use_container_width=True):
    with st.status("분석 엔진 작동 중...", expanded=True) as status:
        st.session_state.records = data.generate_fake_products(months, seed=int(time.time()))
        st.session_state.top5 = data.calculate_top5(st.session_state.records)
        st.session_state.ai_top5 = ai.analyze_trends(st.session_state.top5)
        status.update(label="✅ 분석 완료!", state="complete", expanded=False)
    st.toast("R&D 분석이 완료되었습니다.", icon="✅")

# 3. 메인 출력 영역
if st.session_state.records:
    # (4) 최상단 데이터 테이블
    st.subheader("📋 실시간 음료류 품목제조보고 현황")
    st.dataframe(st.session_state.records, use_container_width=True, height=200)
    
    # (1) Top5 카드 영역
    ui.render_top5_cards(st.session_state.top5, st.session_state.ai_top5)
    
    # (2) R&D 설계 영역 (표 상단 - 슬라이더 하단 수직 배치)
    if st.session_state.selected_flavor:
        # engine_ai에서 확장된 리스트를 가져옴
        strategy, full_ingredients = ai.propose_formula(st.session_state.selected_flavor)
        
        st.divider()
        st.subheader(f"🧪 {st.session_state.selected_flavor} 제품 정밀 배합 시뮬레이션")
        
        # 레이아웃 분할: 좌(전략) / 우(배합 시뮬레이터)
        col_left, col_right = st.columns([1, 1.5])
        
        with col_left:
            ui.render_marketing_report(strategy)
            
        with col_right:
            # 실시간 업데이트를 위한 Placeholder (표 상단 고정)
            table_placeholder = st.empty()
            
            st.markdown("---")
            st.markdown("#### 🛠️ 원료별 미세 조정 패널 (하단)")
            
            # 사용자 조절 값 저장
            user_values = {}
            # 시인성을 위해 2단 슬라이더 배치
            s_cols = st.columns(2)
            
            for i, ing in enumerate(full_ingredients):
                with s_cols[i % 2]:
                    user_values[ing['원재료']] = st.slider(
                        f"{ing['원재료']} ({ing['role']})",
                        float(ing['min']), float(ing['max']), float(ing['AI']),
                        step=0.01, key=f"slide_{ing['원재료']}"
                    )
            
            # 슬라이더 값이 변경될 때마다 상단의 표를 다시 그림
            summary_data = []
            total_sum = 0
            for k, v in user_values.items():
                role = next(x['role'] for x in full_ingredients if x['원재료'] == k)
                summary_data.append({"원재료명": k, "배합비(%)": f"{v:.2f}%", "역할": role})
                total_sum += v
            
            # 표 상단 렌더링
            with table_placeholder:
                st.markdown(f"##### 📊 현재 실시간 배합표 (Total: {total_sum:.2f}%)")
                st.table(pd.DataFrame(summary_data))
                
                if abs(total_sum - 100.0) < 0.01:
                    st.success("✅ 합계 100% 충족: 생산 SOP 확정 가능")
                else:
                    st.warning(f"⚠️ 합계 오차 발생: 현재 {total_sum:.2f}% (100%를 맞춰주세요)")

    # (3) 최하단 미션 영역
    ui.render_mission_section()
