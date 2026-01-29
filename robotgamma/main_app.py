import streamlit as st
import pandas as pd
import engine_ai as ai
import ui_layout as ui
import engine_data as data
import time

st.set_page_config(page_title="ABC 제품개발 로봇 Gamma", layout="wide")

if "selected_flavor" not in st.session_state: st.session_state.selected_flavor = None

# 사이드바 컨트롤 센터
st.sidebar.header("🔍 R&D 멀티 컨트롤 센터")
with st.sidebar.expander("📅 검색 조건 설정", expanded=True):
    months = st.slider("분석 기간", 1, 12, 3)
    if st.sidebar.button("▶ 데이터 분석 및 동기화", use_container_width=True):
        st.session_state.records = data.generate_fake_products(months, seed=int(time.time()))
        st.session_state.top5 = data.calculate_top5(st.session_state.records)
        st.session_state.selected_flavor = None

if st.session_state.get("records"):
    df_raw = pd.DataFrame(st.session_state.records)
    st.subheader("📋 실시간 품목제조보고 데이터 현황")
    st.dataframe(df_raw, use_container_width=True, height=200)
    ui.render_top5_cards(st.session_state.top5)
    
    if st.session_state.selected_flavor:
        st.divider()
        st.subheader(f"🧪 {st.session_state.selected_flavor} 전문가용 정밀 시뮬레이터")

        col_opt1, col_opt2 = st.columns(2)
        with col_opt1: b_type = st.selectbox("가공 방식", ["농축액", "NFC 과즙", "퓨레", "분말추출물"])
        with col_opt2: s_choice = st.multiselect("당류 라이브러리", ["액상알룰로스", "정백당", "스테비아", "에리스리톨"], default=["액상알룰로스"])

        # AI 호출 및 무결성 캐싱
        ckey = f"final_v4_{st.session_state.selected_flavor}_{b_type}_{hash(tuple(s_choice))}"
        if ckey not in st.session_state:
            with st.status("AI 시니어 연구원이 정밀 설계 중...") as s:
                st.session_state[ckey] = ai.propose_formula(st.session_state.selected_flavor, s_choice, b_type)
                s.update(label="✅ 설계 완료", state="complete")

        res = st.session_state[ckey]
        if res:
            col_rep, col_sim = st.columns([1, 2.5])
            with col_rep: ui.render_marketing_report(res["report"])
            
            with col_sim:
                # 1. 추천배합표 강제 출력 (상단 고정)
                table_placeholder = st.empty()
                
                st.markdown("---")
                st.markdown("#### 🛠️ 원료별 정밀 조절 (상하한선 물리 고정)")
                
                formula = res["formula"]
                others = [i for i in formula if "정제수" not in i['원료명']]
                water_cfg = next(i for i in formula if "정제수" in i['원료명'])
                
                adj = {}
                sum_others = 0.0
                scols = st.columns(2)
                
                for i, item in enumerate(others):
                    with scols[i % 2]:
                        # [핵심 수정] 슬라이더 min/max/value를 float로 강제 변환 및 물리적 범위 고정
                        # 단위 폭주 방지를 위해 1,000배수 연산은 내부 식별용으로만 사용
                        val = st.slider(
                            f"**{item['원료명']}** ({item['min']}% ~ {item['max']}%)",
                            min_value=float(item['min']), 
                            max_value=float(item['max']), 
                            value=float(item['AI']),
                            step=0.01,
                            key=f"sld_v4_{ckey}_{item['원료명']}"
                        )
                        adj[item['원료명']] = val
                        sum_others += val
                
                # [오토 밸런스] 합계 100.00% 유지 로직
                cur_w = max(0.0, 100.0 - sum_others)
                adj["정제수"] = cur_w
                
                # 3단 데이터 구성 (추천/개선/Delta)
                d_list = []
                for item in formula:
                    name = item['원료명']
                    re_v = item['AI']
                    cu_v = adj.get(name, cur_w)
                    d_list.append({
                        "원료명": name, "추천(%)": f"{re_v:.2f}", "개선(%)": f"{cu_v:.2f}",
                        "Delta": f"{cu_v - re_v:+.2f}", "목적": item['사용목적'], "주의사항": item['주의사항']
                    })
                
                # 상단 배합표 실시간 렌더링
                with table_placeholder:
                    st.table(pd.DataFrame(d_list))
                    if cur_w < water_cfg['min']:
                        st.error(f"⚠️ 정제수 한계 미달: {cur_w:.2f}% (최소 {water_cfg['min']}% 필요)")
                    else:
                        st.success(f"✅ 합계 100.00% 자동 유지 중 (정제수: {cur_w:.2f}%)")

            # 하단 학술 근거
            st.divider()
            st.subheader("📚 AI 시니어 연구원의 배합 설계 근거 및 문헌")
            for ev in res["report"]["📚 배합 설계 근거 및 문헌"]:
                st.info(f"**{ev['title']}**\n\n{ev['desc']}\n\n[🔗 관련 문헌 검색]({ev['url']})")
