import streamlit as st

def render_top5_cards(top5):
    st.subheader("🔥 시장 트렌드: Top5 플레이버")
    cols = st.columns(5)
    for i, t in enumerate(top5):
        with cols[i]:
            flavor = t['flavor']
            st.image(f"https://picsum.photos/seed/{flavor}/480/480", use_container_width=True)
            st.markdown(f"**{flavor}** ({t['share']}%)")
            if st.button(f"{flavor} 기획 시작", key=f"btn_{flavor}", use_container_width=True):
                st.session_state.selected_flavor = flavor
                st.rerun()

def render_marketing_report(report):
    st.markdown("#### 🧠 AI 시니어 연구원 전략 보고")
    for cat, items in report.items():
        if "근거" not in cat: # 근거 섹션은 하단에 따로 표시
            with st.expander(f"📍 {cat}", expanded=True):
                for item in items: st.write(f"- {item}")
