import streamlit as st

def render_top5_cards(top5, ai_result):
    """시장 분석 결과를 카드 형태로 출력"""
    st.subheader("🔥 시장 트렌드: Top5 플레이버")
    if ai_result:
        st.info(ai_result.get("summary", ""))
        
    cols = st.columns(5)
    for i, t in enumerate(top5):
        with cols[i]:
            flavor = t['flavor']
            st.image(f"https://picsum.photos/seed/{flavor}/480/480", use_container_width=True)
            st.markdown(f"**{flavor}** ({t['share']}%)")
            if st.button(f"{flavor} 기획 시작", key=f"btn_{flavor}", use_container_width=True):
                st.session_state.selected_flavor = flavor
                st.rerun()

def render_marketing_report(strategy_dict):
    """마케팅 전략 요소를 개조식(Bullet point)으로 정리하여 출력"""
    st.markdown("#### 🧠 제품 개발 및 마케팅 세부 전략 보고")
    if not strategy_dict:
        st.warning("전략 데이터를 불러올 수 없습니다.")
        return

    for category, items in strategy_dict.items():
        with st.expander(f"📍 {category}", expanded=True):
            for item in items:
                st.write(f"- {item}")

def render_mission_section():
    """신입사원 교육용 미션 섹션"""
    st.divider()
    st.subheader("🎯 제조 리스크 해결 미션")
    with st.expander("미션 확인", expanded=True):
        st.write("**Q. rPET 용기를 사용하는 고온 충전(Hot-fill) 공정에서 용기 변형을 막기 위해 가장 주의 깊게 관리해야 할 변수는?**")
        ans = st.radio("항목 선택", ["원료의 당도 수준", "충전 및 냉각 온도 프로파일", "라벨 부착기의 압력"])
        if st.button("미션 제출"):
            if "온도" in ans:
                st.success("정답입니다! rPET의 열변형 온도를 고려한 정밀한 온도 제어가 핵심입니다.")
                st.balloons()
            else:
                st.error("오답입니다. 포장재 물성과 공정 온도(Tg)의 상관관계를 다시 검토하세요.")
