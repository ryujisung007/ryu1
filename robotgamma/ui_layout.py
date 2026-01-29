import streamlit as st
import pandas as pd

def render_top5_cards(top5, ai_result):
    """Top5 플레이버 카드 UI"""
    st.subheader("🔥 시장 트렌드: Top5 플레이버")
    if ai_result:
        st.info(ai_result.get("summary", "분석이 완료되었습니다."))
        
    cols = st.columns(5)
    for i, t in enumerate(top5):
        with cols[i]:
            flavor = t['flavor']
            # picsum 이미지 사용
            st.image(f"https://picsum.photos/seed/{flavor}/480/480", use_container_width=True)
            st.markdown(f"**{flavor}** ({t['share']}%)")
            if st.button(f"{flavor} 기획 시작", key=f"btn_{flavor}", use_container_width=True):
                st.session_state.selected_flavor = flavor
                st.rerun()

def render_formula_section(flavor, formula_data):
    """배합비 및 컨셉 상세 레이아웃 (좌/우 분할)"""
    st.divider()
    st.subheader(f"🧪 {flavor} AI 추천 배합비 설계")
    
    # AttributeError 방지: 데이터가 딕셔너리인지 확인
    if not isinstance(formula_data, dict) or not formula_data:
        st.warning("상세 배합 데이터를 불러오는 중입니다...")
        return

    left, right = st.columns([1, 1.2])
    
    with left:
        st.markdown("#### 🧠 제품 컨셉 및 전략")
        st.info(formula_data.get("concept", "컨셉 정보가 존재하지 않습니다."))
        
    with right:
        st.markdown("#### 📊 배합비 비교 (기존 vs AI 제안)")
        table_data = formula_data.get("table", [])
        if table_data:
            df = pd.DataFrame(table_data)
            st.dataframe(df, use_container_width=True, height=400)
        else:
            st.caption("표시할 배합 데이터가 없습니다.")

def render_mission_section():
    """신입사원 교육용 미션 섹션"""
    st.divider()
    st.subheader("🎯 신입사원 리스크 해결 미션")
    with st.expander("오늘의 제조공정 미션 확인하기", expanded=True):
        st.write("**Q. rPET 용기를 사용하는 고온 충전(Hot-fill) 공정에서 가장 주의 깊게 관리해야 할 변수는?**")
        ans = st.radio("항목 선택", ["원료의 당도 수준", "충전 및 냉각 온도 프로파일", "라벨 부착기의 압력"])
        if st.button("미션 제출"):
            if "온도" in ans:
                st.success("정답입니다! rPET의 열변형 특성을 고려한 정밀한 온도 제어는 품질 관리의 핵심입니다.")
                st.balloons() # 완료 신호
            else:
                st.error("오답입니다. 포장재의 물성과 공정 온도의 상관관계를 다시 검토해보세요.")
