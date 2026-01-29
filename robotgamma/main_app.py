import streamlit as st
import engine_ai as ai
import pandas as pd
import ui_layout as ui

# (중략: 데이터 로드 및 카드 렌더링 부분은 기존 유지)

if st.session_state.selected_flavor:
    # 1. AI 시니어 연구원 협의 결과 데이터 호출
    with st.spinner(f"AI 연구원이 '{st.session_state.selected_flavor}' 표준 배합비를 설계 중입니다..."):
        report, formula_list = ai.propose_formula(st.session_state.selected_flavor)

    if formula_list:
        st.divider()
        st.subheader(f"🥤 {st.session_state.selected_flavor} 표준 배합 및 전략 보고서")
        
        col1, col2 = st.columns([1, 1.8])
        
        with col1:
            # AI 마케팅/관능 보고서 출력
            ui.render_marketing_report(report)
            
        with col2:
            # [시각적 레이아웃 핵심] 표를 먼저 출력하기 위한 Placeholder
            table_area = st.empty()
            
            st.markdown("---")
            st.markdown("#### 🛠️ 배합비 정밀 조절 패널 (SOP)")
            
            # 슬라이더에서 조절된 값을 저장할 딕셔너리
            adjusted_values = {}
            s_cols = st.columns(2)
            
            # AI가 제안한 min/max 범위를 엄격히 적용한 슬라이더 생성
            for i, item in enumerate(formula_list):
                with s_cols[i % 2]:
                    adjusted_values[item['원료명']] = st.slider(
                        f"{item['원료명']} ({item['사용목적']})",
                        min_value=float(item['min']),
                        max_value=float(item['max']),
                        value=float(item['AI']),
                        step=0.01,
                        key=f"slide_{item['원료명']}"
                    )
            
            # 실시간 업데이트 로직: 슬라이더 값이 변경되면 상단 표의 수치만 변경됨
            updated_df = pd.DataFrame(formula_list)
            updated_df['AI'] = updated_df['원료명'].map(adjusted_values) # 실시간 수치 반영
            
            # 최종 배합표 렌더링 (상단 위치)
            with table_area:
                st.markdown("##### 📊 AI 시니어 연구원 추천 표준 배합표")
                st.dataframe(updated_df[['원료명', 'AI', '사용목적', '용도', '용법', '사용주의사항']], 
                             use_container_width=True, hide_index=True)
                
                total_sum = sum(adjusted_values.values())
                if abs(total_sum - 100.0) < 0.01:
                    st.success(f"✅ 합계: {total_sum:.2f}% (배합 표준 충족)")
                else:
                    st.warning(f"⚠️ 합계: {total_sum:.2f}% (100%를 맞춰주세요)")
