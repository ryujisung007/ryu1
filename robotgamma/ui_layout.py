import streamlit as st
import pandas as pd

# Top5 카드 렌더링
def render_top5_cards(top5, ai_result):
    st.subheader("🔥 시장 트렌드: Top5 플레이버")
    if ai_result:
        st.info(ai_result.get("summary", "데이터 분석 완료"))
        
    cols = st.columns(5)
    for i, t in enumerate(top5):
        with cols[i]:
            # 이미지 및 배지 UI
            flavor = t['flavor']
            st.image(f"https://picsum.photos/seed/{flavor}/480/480", use_container_width=True)
            st.markdown(f"**{flavor}** ({t['share']}%)")
            if st.button(f"{flavor} 기획", key=f"btn_{flavor}"):
                st.session_state.selected_flavor = flavor
                st.rerun()

# 배합비 비교 테이블 렌더링
def render_formula_section(flavor, formula_data):
    st.divider()
    st.subheader(f"🧪 {flavor} AI 추천 배합비 설계")
    
    left, right = st.columns([1, 1.2])
    
    with left:
        st.markdown("#### 🧠 제품 컨셉 및 전략")
        st.write(formula_data.get("concept", "컨셉 산출 중..."))
        
    with right:
        st.markdown("#### 📊 배합비 비교 (기존 vs AI)")
        # 표 데이터 구성 로직
        df = pd.DataFrame(formula_data.get("table", []))
        st.dataframe(df, use_container_width=True, height=400)

# 리스크 해결 미션 섹션
def render_mission_section():
    st.divider()
    st.subheader("🎯 신입사원 리스크 해결 미션")
    with st.expander("미션 확인하기", expanded=True):
        st.write("Q. rPET 용기 사용 시 충전 공정에서 가장 주의해야 할 점은?")
        ans = st.radio("선택", ["원료 당도", "살균/충전 온도", "라벨 디자인"])
        if st.button("제출"):
            if "온도" in ans: st.success("정답입니다! (포장기술사 관점)")
            else: st.error("다시 생각해보세요.")
