import streamlit as st
import pandas as pd
import engine_ai as ai
import ui_layout as ui
import engine_data as data # 기존 가상데이터 생성 파일
import time

# 1. 페이지 설정
st.set_page_config(page_title="ABC 제품개발 로봇 Gamma", layout="wide")

# 세션 상태 초기화
if "selected_flavor" not in st.session_state: st.session_state.selected_flavor = None
if "records" not in st.session_state: st.session_state.records = None

# 2. 사이드바 제어
st.sidebar.header("🚀 R&D 컨트롤 센터")
months = st.sidebar.slider("분석 기간(개월)", 1, 6, 1)

if st.sidebar.button("▶ 시뮬레이션 가동", use_container_width=True):
    st.session_state.records = data.generate_fake_products(months, seed=int(time.time()))
    st.session_state.top5 = data.calculate_top5(st.session_state.records)
    st.session_state.selected_flavor = None

# 3. 메인 화면 출력
if st.session_state.records:
    # (4) 실시간 데이터 테이블
    st.subheader("📋 실시간 음료류 품목제조보고 현황")
    st.dataframe(st.session_state.records, use_container_width=True, height=200)
    
    # (1) 플레이버 추천 카드
    ui.render_top5_cards(st.session_state.top5)
    
    if st.session_state.selected_flavor:
        st.divider()
        st.subheader(f"🧪 {st.session_state.selected_flavor} R&D 정밀 시뮬레이터")

        # --- [추가] 당류 선택권 부여 영역 ---
        st.markdown("#### 🍯 주사용 당류(Sweetener) 선택")
        sweetener_choice = st.multiselect(
            "배합에 포함할 당류를 선택하세요",
            ["액상알룰로스", "정백당", "결정과당", "에리스리톨", "효소처리스테비아", "나한과추출물", "수크랄로스"],
            default=["액상알룰로스"],
            key="sweetener_select"
        )

        # AI 데이터 호출 (플레이버 + 당류 선택 반영)
        # 선택이 바뀔 때마다 다시 계산하기 위해 세션 키에 당류 포함
        cache_key = f"data_{st.session_state.selected_flavor}_{hash(tuple(sweetener_choice))}"
        
        if cache_key not in st.session_state:
            with st.spinner("AI 시니어 연구원이 당류 특성을 고려하여 재설계 중..."):
                report, formula = ai.propose_formula(st.session_state.selected_flavor, sweetener_choice)
                st.session_state[cache_key] = (report, formula)
        
        report, formula = st.session_state[cache_key]

        col_report, col_sim = st.columns([1, 2.2])
        
        with col_report:
            ui.render_marketing_report(report)
            
        with col_sim:
            # 실시간 3단 배합표 (추천/개선/Delta) 위치
            table_placeholder = st.empty()
            
            st.markdown("---")
            st.markdown("#### 🛠️ 배합비 정밀 조절 (정제수 오토 밸런스 모드)")
            
            # 원료 구분 로직
            water_item = next(item for item in formula if "정제수" in item['원료명'])
            others = [item for item in formula if "정제수" not in item['원료명']]
            
            adjusted_values = {}
            total_others = 0
            
            s_cols = st.columns(2)
            for i, item in enumerate(others):
                with s_cols[i % 2]:
                    # 슬라이더 상하한선 물리적 고정 (AI 제안값 적용)
                    val = st.slider(
                        f"{item['원료명']} ({item['사용목적']})",
                        min_value=float(item['min']),
                        max_value=float(item['max']),
                        value=float(item['AI']),
                        step=0.01, key=f"slide_{st.session_state.selected_flavor}_{item['원료명']}"
                    )
                    adjusted_values[item['원료명']] = val
                    total_others += val
            
            # 정제수 자동 계산 (Auto-Balance)
            auto_water = max(0.0, 100.0 - total_others)
            adjusted_values["정제수"] = auto_water
            
            # 3단 표 구성 및 데이터 연산
            final_display = []
            for item in formula:
                name = item['원료명']
                recom = item['AI']
                current = adjusted_values[name]
                
                final_display.append({
                    "원료명": name,
                    "추천 배합비(%)": f"{recom:.2f}",
                    "개선 배합비(%)": f"{current:.2f}",
                    "차이(Delta)": f"{current - recom:+.2f}",
                    "사용목적": item['사용목적'],
                    "주의사항": item['주의사항']
                })
            
            with table_placeholder:
                st.table(pd.DataFrame(final_display))
                if auto_water < water_item['min']:
                    st.error(f"⚠️ 정제수 한계 미달: 현재 {auto_water:.2f}% (최소 {water_item['min']}% 권장)")
                else:
                    st.success(f"✅ 합계 100.00% 자동 유지 중 (정제수: {auto_water:.2f}%)")

        # 4. 하단 추천 근거 섹션
        st.divider()
        st.subheader("📚 AI 시니어 연구원의 배합 설계 근거 (학술/문헌)")
        evidence = report.get("📚 배합 설계 근거(학술/문헌)", [])
        ev_cols = st.columns(len(evidence)) if evidence else [st.container()]
        for idx, text in enumerate(evidence):
            with ev_cols[idx % len(ev_cols)]:
                st.info(text)
