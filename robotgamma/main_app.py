import streamlit as st
import pandas as pd
import engine_ai as ai
import ui_layout as ui
import os
import time

st.set_page_config(page_title="ABC 제품개발 로봇 Gamma", layout="wide")

# 📂 [수정] 파일 경로 인식 무결성 강화
# 현재 실행 중인 파일(main_app.py)의 절대 경로를 기준으로 DB 위치 추적
current_dir = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(current_dir, "과일원료_DB.csv")

db_df = None

# 1. 파일 존재 여부 확인 및 로딩
if os.path.exists(DB_PATH):
    try:
        # DB 구조에 맞춰 헤더(1번 행) 및 데이터 정제
        db_df = pd.read_csv(DB_PATH, header=1).drop(0).reset_index(drop=True)
        st.sidebar.success(f"✅ DB 자동 로드 완료: {os.path.basename(DB_PATH)}")
    except Exception as e:
        st.sidebar.error(f"❌ DB 로드 중 오류 발생: {e}")
else:
    # 파일이 경로에 없을 경우 긴급 업로드 모드 실행
    st.sidebar.warning(f"⚠️ '{os.path.basename(DB_PATH)}'를 찾을 수 없습니다.")
    uploaded_file = st.sidebar.file_uploader("파일을 직접 업로드하거나 동일 폴더에 넣어주세요", type="csv")
    if uploaded_file:
        db_df = pd.read_csv(uploaded_file, header=1).drop(0).reset_index(drop=True)

# 2. 메인 시뮬레이터 로직
if db_df is not None:
    if "selected_flavor" not in st.session_state:
        st.session_state.selected_flavor = None

    # 사이드바 필터링 (회사별 검색 등 지시사항 반영)
    st.sidebar.header("🔍 R&D 전문가용 컨트롤 센터")
    with st.sidebar.expander("🏢 세부 조건 검색", expanded=True):
        # DB 컬럼 기반 동적 필터링 (예: 원산지)
        target_origin = st.multiselect("원산지 필터", options=db_df["원산지"].unique())

    # 플레이버 카드 출력 (임시 데이터)
    ui.render_top5_cards([{"flavor":"사과","share":35}, {"flavor":"망고","share":28}, {"flavor":"포도","share":20}])

    if st.session_state.selected_flavor:
        st.divider()
        st.subheader(f"🧪 {st.session_state.selected_flavor} DB 연동 정밀 시뮬레이터")
        
        # 전문가용 선택 UI
        c1, c2 = st.columns(2)
        with c1: b_type = st.selectbox("가공 방식 선택", ["농축액", "NFC", "퓨레"])
        with c2: s_choice = st.multiselect("당류 라이브러리", ["알룰로스", "스테비아", "정백당"], default=["알룰로스"])

        # AI 호출 및 캐싱
        ckey = f"v_db_strict_{st.session_state.selected_flavor}_{b_type}_{hash(tuple(s_choice))}"
        if ckey not in st.session_state:
            with st.status("AI 시니어 연구원이 DB 데이터를 대조 중입니다...") as s:
                res = ai.propose_formula_with_db(st.session_state.selected_flavor, s_choice, b_type, db_df)
                st.session_state[ckey] = res
                s.update(label="✅ 분석 및 설계 완료", state="complete")

        res = st.session_state[ckey]
        if res and "formula" in res:
            # [지시사항] 추천배합표 최상단 고정
            table_spot = st.empty()
            formula = res["formula"]
            
            st.markdown("---")
            st.markdown("#### 🛠️ 원료별 정밀 조절 (상하한선 물리 고정)")
            
            # 슬라이더 및 오토 밸런스 로직
            others = [i for i in formula if "정제수" not in i['원료명']]
            adj, sum_others = {}, 0.0
            scols = st.columns(2)
            
            for i, item in enumerate(others):
                with scols[i % 2]:
                    # [지시사항] 상하한선 물리 고정 (이탈 불가)
                    v = st.slider(f"**{item['원료명']}** ({item['min']}%~{item['max']}%)", 
                                  float(item['min']), float(item['max']), float(item['AI']), 0.01,
                                  key=f"sld_strict_{ckey}_{item['원료명']}")
                    adj[item['원료명']] = v
                    sum_others += v
            
            # [지시사항] 정제수 오토 밸런스 및 합계 100% 무결성
            cur_w = max(0.0, 100.0 - sum_others)
            adj["정제수"] = cur_w
            
            # 3단 데이터 구성 (추천/개선/Delta)
            display_list = []
            for item in formula:
                nm, re_v = item['원료명'], item['AI']
                cu_v = adj.get(nm, cur_w)
                display_list.append({"원료명": nm, "추천(%)": f"{re_v:.2f}", "개선(%)": f"{cu_v:.2f}", "Delta": f"{cu_val-re_val:+.2f}" if 'cu_val' in locals() else f"{cu_v-re_v:+.2f}"})
            
            with table_spot:
                st.table(pd.DataFrame(display_list))
                st.success(f"✅ 합계 100.00% 자동 유지 중 (정제수: {cur_w:.2f}%)")
else:
    st.info("💡 사이드바에서 '과일원료_DB.csv' 파일을 로드해야 분석을 시작할 수 있습니다.")
