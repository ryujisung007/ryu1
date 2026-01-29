import streamlit as st
import engine_ai as ai
import pandas as pd

# (생략) 데이터 로드 및 상단 레이아웃...

if st.session_state.selected_flavor:
    strategy, ingredients = ai.propose_formula(st.session_state.selected_flavor)
    
    st.divider()
    st.subheader(f"🧪 {st.session_state.selected_flavor} R&D 시뮬레이터")
    
    # 1. 상단: 마케팅 전략 (개조식)
    for cat, items in strategy.items():
        with st.expander(cat, expanded=True):
            for item in items: st.write(item)
            
    # 2. 중단: 실시간 배합표 (시인성 확보)
    table_spot = st.empty()
    
    # 3. 하단: 슬라이더 조절 패널
    st.markdown("#### 🛠️ 배합비 미세 조정")
    new_values = {}
    cols = st.columns(2)
    for i, ing in enumerate(ingredients):
        with cols[i % 2]:
            new_values[ing['name']] = st.slider(
                f"{ing['name']}", ing['min'], ing['max'], ing['val'], step=0.01
            )
            
    # 4. 실시간 표 업데이트 (하단 슬라이더를 움직이면 상단 표가 바뀜)
    df = pd.DataFrame(list(new_values.items()), columns=['원료명', '배합비(%)'])
    total = df['배합비(%)'].sum()
    table_spot.table(df) # 상단에 위치한 자리에 표 출력
    
    if abs(total - 100) < 0.01:
        st.success(f"✅ 합계: {total:.2f}% (완벽한 배합)")
    else:
        st.warning(f"⚠️ 합계: {total:.2f}% (100%를 맞춰주세요)")
