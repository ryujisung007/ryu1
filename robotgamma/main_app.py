import streamlit as st
import pandas as pd
import engine_ai as ai
import ui_layout as ui
import engine_data as data
import time

st.set_page_config(page_title="ABC 제품개발 로봇 Gamma", layout="wide")

if "selected_flavor" not in st.session_state: st.session_state.selected_flavor = None
if "records" not in st.session_state: st.session_state.records = None

st.sidebar.header("🚀 R&D 컨트롤 센터")
months = st.sidebar.slider("분석 기간(개월)", 1, 6, 1)

if st.sidebar.button("▶ 시뮬레이션 가동", use_container_width=True):
    st.session_state.records = data.generate_fake_products(months, seed=int(time.time()))
    st.session_state.top5 = data.calculate_top5(st.session_state.records)
    st.session_state.selected_flavor = None

if st.session_state.records:
    st.subheader("📋 실시간 음료류 품목제조보고 현황")
    st.dataframe(st.session_state.records, use_container_width=True, height=200)
    ui.render_top5_cards(st.session_state.top5)
    
    if st.session_state.selected_flavor:
        st.divider()
        st.subheader(f"🧪 {st.session_state.selected_flavor} R&D 정밀 시뮬레이터")

        st.markdown("#### 🍯 주사용 당류(Sweetener) 선택")
        sweetener_choice = st.multiselect(
            "배합에 포함할 당류를 선택하세요",
            ["액상알룰로스", "정백당", "결정과당", "에리스리톨", "효소처리스테비아", "나한과추출물"],
            default=["액상알룰로스"]
        )

        # --- [수정] AI 작동 중 예상 시간 및 프로그레스 바 표시 ---
        cache_key = f"res_{st.session_state.selected_flavor}_{hash(tuple(sweetener_choice))}"
        
        if cache_key not in st.session_state:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # gpt-4o-mini 평균 응답 속도 기준 약 3~5초 시뮬레이션
            for percent_complete in range(100):
                time.sleep(0.03) # 예상 대기 시간 3초
                progress_bar.progress(percent_complete + 1)
                remaining = (100 - percent_complete) * 0.03
                status_text.markdown(f"⏳ **AI 시니어 연구원이 분석 중... (예상 완료까지 약 {remaining:.1f}초)**")
            
            res = ai.propose_formula(st.session_state.selected_flavor, sweetener_choice)
            if res:
                st.session_state[cache_key] = res
            progress_bar.empty()
            status_text.empty()

        if cache_key in st.session_state:
            res_data = st.session_state[cache_key]
            report = res_data["report"]
            formula = res_data["formula"]

            col_report, col_sim = st.columns([1, 2.2])
            
            with col_report:
                ui.render_marketing_report(report)
                
            with col_sim:
                # [중요] 추천배합표가 반드시 보이도록 레이아웃 고정
                st.markdown("##### 📊 AI 시니어 연구원 추천 표준 배합표")
                table_placeholder = st.empty()
                
                st.markdown("---")
                st.markdown("#### 🛠️ 배합비 정밀 조절 (정제수 오토 밸런스)")
                
                # 원료 분류 및 슬라이더
                water_item = next(item for item in formula if "정제수" in item['원료명'])
                others = [item for item in formula if "정제수" not in item['원료명']]
                
                adjusted_values = {}
                total_others = 0
                s_cols = st.columns(2)
                
                for i, item in enumerate(others):
                    with s_cols[i % 2]:
                        val = st.slider(
                            f"{item['원료명']} ({item['사용목적']})",
                            min_value=float(item['min']),
                            max_value=float(item['max']),
                            value=float(item['AI']),
                            step=0.01, key=f"s_{cache_key}_{item['원료명']}"
                        )
                        adjusted_values[item['원료명']] = val
                        total_others += val
                
                auto_water = max(0.0, 100.0 - total_others)
                adjusted_values["정제수"] = auto_water
                
                # 3단 표 생성 및 출력
                display_list = []
                for item in formula:
                    name = item['원료명']
                    recom = item['AI']
                    curr = adjusted_values[name]
                    display_list.append({
                        "원료명": name,
                        "추천 배합비(%)": f"{recom:.2f}",
                        "개선 배합비(%)": f"{curr:.2f}",
                        "차이(Delta)": f"{curr - recom:+.2f}",
                        "사용목적": item['사용목적'],
                        "주의사항": item['주의사항']
                    })
                
                with table_placeholder:
                    st.table(pd.DataFrame(display_list)) # table로 강제 출력
                    if auto_water < water_item['min']:
                        st.error(f"⚠️ 정제수 부족: {auto_water:.2f}% (최소 {water_item['min']}% 권장)")
                    else:
                        st.success(f"✅ 합계 100.00% 유지 (정제수: {auto_water:.2f}%)")

            # 하단 근거 섹션
            st.divider()
            st.subheader("📚 AI 시니어 연구원의 배합 설계 근거")
            evidence = report.get("📚 배합 설계 근거(학술/문헌)", [])
            if evidence:
                ev_cols = st.columns(len(evidence))
                for idx, text in enumerate(evidence):
                    with ev_cols[idx]:
                        st.info(text)
