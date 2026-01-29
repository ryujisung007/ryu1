import streamlit as st
import engine_data as data
import engine_ai as ai
import ui_layout as ui
import pandas as pd
import time

st.set_page_config(page_title="ABC 제품개발 로봇 Gamma", layout="wide")

if "selected_flavor" not in st.session_state: st.session_state.selected_flavor = None
if "records" not in st.session_state: st.session_state.records = None

# 사이드바
st.sidebar.header("🚀 R&D 컨트롤 센터")
months = st.sidebar.slider("분석 기간(개월)", 1, 6, 1)
if st.sidebar.button("▶ 시뮬레이션 가동"):
    st.session_state.records = data.generate_fake_products(months, seed=int(time.time()))
    st.session_state.top5 = data.calculate_top5(st.session_state.records)
    st.session_state.ai_top5 = ai.analyze_trends(st.session_state.top5)

if st.session_state.records:
    st.subheader("📋 실시간 음료류 품목제조보고 현황")
    st.dataframe(st.session_state.records, use_container_width=True, height=200)
    ui.render_top5_cards(st.session_state.top5, st.session_state.ai_top5)
    
    if st.session_state.selected_flavor:
        # AI 연구원이 관여하여 전략과 배합비를 생성
        with st.spinner("AI 시니어 연구원이 배합비를 설계 중입니다..."):
            strategy, ingredients = ai.propose_formula(st.session_state.selected_flavor)
        
        st.divider()
        st.subheader(f"🧪 {st.session_state.selected_flavor} 제품 정밀 R&D 보고서")
        
        col_left, col_right = st.columns([1, 1.5])
        
        with col_left:
            ui.render_marketing_report(strategy)
            
        with col_right:
            # 1. 상단: AI 추천 배합표 출력 (목적 명시)
            st.markdown("#### 📊 AI 시니어 연구원 추천 배합표")
            if ingredients:
                table_placeholder = st.empty() # 실시간 업데이트용
                
                # 2. 하단: 배합비 정밀 조절 패널 (슬라이더)
                st.markdown("---")
                st.markdown("#### 🛠️ 배합비 정밀 조절 패널 (SOP 미세조정)")
                
                user_values = {}
                s_cols = st.columns(2)
                for i, ing in enumerate(ingredients):
                    with s_cols[i % 2]:
                        # AI가 정해준 min, max 내에서만 움직이도록 제한
                        user_values[ing['원재료']] = st.slider(
                            f"{ing['원재료']} ({ing['role']})",
                            min_value=float(ing['min']), 
                            max_value=float(ing['max']), 
                            value=float(ing['AI']),
                            step=0.01, key=f"slide_{ing['원재료']}"
                        )
                
                # 슬라이더 값을 상단 표에 실시간 반영
                total_sum = sum(user_values.values())
                summary_data = []
                for k, v in user_values.items():
                    role = next(x['role'] for x in ingredients if x['원재료'] == k)
                    summary_data.append({"원재료명": k, "배합비(%)": f"{v:.2f}%", "사용 목적(용도/용법)": role})
                
                with table_placeholder:
                    st.table(pd.DataFrame(summary_data))
                    if abs(total_sum - 100.0) < 0.01:
                        st.success(f"✅ 합계 100% 충족 (Total: {total_sum:.2f}%)")
                    else:
                        st.warning(f"⚠️ 합계 오차 발생: 현재 {total_sum:.2f}%")
            else:
                st.error("배합 데이터를 불러올 수 없습니다.")

    ui.render_mission_section()
