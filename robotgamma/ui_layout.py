import streamlit as st

def render_top5_cards(top5, ai_result):
    st.subheader("🔥 시장 트렌드: Top5 플레이버")
    cols = st.columns(5)
    for i, t in enumerate(top5):
        with cols[i]:
            flavor = t['flavor']
            st.image(f"https://picsum.photos/seed/{flavor}/480/480", use_container_width=True)
            st.markdown(f"**{flavor}** ({t['share']}%)")
            if st.button(f"{flavor} 기획 시작", key=f"btn_{flavor}"):
                st.session_state.selected_flavor = flavor
                st.rerun()

def render_marketing_report(strategy_dict):
    st.markdown("#### 🧠 관능 전문가 세부 전략")
    for category, items in strategy_dict.items():
        with st.expander(f"📍 {category}", expanded=True):
            for item in items: st.write(item)

def render_mission_section():
    st.divider()
    st.subheader("🎯 현장 리스크 해결 미션")
    with st.expander("미션 확인", expanded=True):
        st.write("**Q. rPET 용기를 사용하는 고온 충전(Hot-fill) 공정에서 변형을 막기 위한 핵심 관리 포인트는?**")
        ans = st.radio("선택", ["원료 당도", "정밀한 온도 및 냉각 프로파일 제어", "라벨 압력"])
        if st.button("제출"):
            if "온도" in ans: st.success("정답입니다!"); st.balloons()
            else: st.error("오답입니다.")
