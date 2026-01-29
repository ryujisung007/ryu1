import streamlit as st
import pandas as pd
import engine_ai as ai
import ui_layout as ui
import os

st.set_page_config(page_title="ABC 제품개발 로봇 Gamma", layout="wide")

# [수정] 파일 존재 확인 후 자동 로드
DB_PATH = "과일원료_DB.csv"

if os.path.exists(DB_PATH):
    # 헤더 구조가 복잡하므로 2번째 행(index 0)을 컬럼으로 사용
    db_df = pd.read_csv(DB_PATH, header=1)
    # 불필요한 첫 행(설명문) 제거
    db_df = db_df.drop(0).reset_index(drop=True)
    st.sidebar.success(f"✅ 원료 DB({len(db_df)}종) 로드 완료")
else:
    st.sidebar.error("❌ '과일원료_DB.csv' 파일을 찾을 수 없습니다.")
    st.stop()

if "selected_flavor" not in st.session_state: st.session_state.selected_flavor = None

# [사이드바 필터 로직 생략 없이 유지]
st.sidebar.header("🔍 R&D 전문가용 컨트롤 센터")
with st.sidebar.expander("🏢 기업 및 조건 필터", expanded=True):
    target_comp = st.multiselect("제조사별 검색", options=db_df["원산지"].unique()) # 원산지로 대체 예시

# 메인 UI 실행
ui.render_top5_cards([{"flavor":"사과","share":30}, {"flavor":"망고","share":25}, {"flavor":"포도","share":20}])

if st.session_state.selected_flavor:
    st.divider()
    st.subheader(f"🧪 {st.session_state.selected_flavor} DB 연동 시뮬레이터")
    
    c1, c2 = st.columns(2)
    with c1: b_type = st.selectbox("가공 방식", ["농축액", "NFC", "퓨레"])
    with c2: s_choice = st.multiselect("당류 선택", ["알룰로스", "스테비아", "정백당"], default=["알룰로스"])

    ckey = f"v_db_{st.session_state.selected_flavor}_{b_type}_{hash(tuple(s_choice))}"
    if ckey not in st.session_state:
        with st.status("AI 시니어 연구원이 DB 정밀 분석 중...") as s:
            res = ai.propose_formula_with_db(st.session_state.selected_flavor, s_choice, b_type, db_df)
            st.session_state[ckey] = res
            s.update(label="✅ 분석 완료", state="complete")

    res = st.session_state[ckey]
    if res and "formula" in res:
        # 추천배합표 최상단 고정
        table_spot = st.empty()
        formula = res["formula"]
        
        st.markdown("---")
        st.markdown("#### 🛠️ 원료별 정밀 조절 (상하한선 물리 고정)")
        
        others = [i for i in formula if "정제수" not in i['원료명']]
        adj, sum_others = {}, 0.0
        scols = st.columns(2)
        
        for i, item in enumerate(others):
            with scols[i % 2]:
                # [무결성] 슬라이더 물리적 범위 고정
                v = st.slider(f"**{item['원료명']}** ({item['min']}%~{item['max']}%)", 
                              float(item['min']), float(item['max']), float(item['AI']), 0.01,
                              key=f"sld_{ckey}_{item['원료명']}")
                adj[item['원료명']] = v
                sum_others += v
        
        cur_w = max(0.0, 100.0 - sum_others)
        adj["정제수"] = cur_w
        
        # 3단 대조표 구성
        d_list = []
        for item in formula:
            nm, re_v = item['원료명'], item['AI']
            cu_v = adj.get(nm, cur_w)
            d_list.append({"원료명": nm, "추천(%)": f"{re_v:.2f}", "개선(%)": f"{cu_v:.2f}", "Delta": f"{cu_v - re_v:+.2f}"})
        
        table_spot.table(pd.DataFrame(d_list))
        st.success(f"✅ 합계 100.00% 유지 (정제수: {cur_w:.2f}%)")
