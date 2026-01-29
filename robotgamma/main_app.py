# [긴급 수정] 물리 제약 및 실시간 렌더링 보강 로직
with col_sim:
    # 1. 최상단 배합표 강제 출력 공간
    table_placeholder = st.empty() 
    
    st.markdown("---")
    st.subheader("🛠️ 원료별 정밀 조절 (상하한선 물리적 고정)")
    
    # 데이터 무결성 검증을 위한 변수 초기화
    adj_values = {}
    sum_others = 0.0
    
    # 슬라이더 렌더링 (데이터 형변환 및 범위 강제)
    scols = st.columns(2)
    for i, item in enumerate(others):
        with scols[i % 2]:
            # [수정 포인트] min_value, max_value를 AI 설계값으로 엄격히 제한
            # 슬라이더가 범위를 절대 벗어날 수 없도록 물리적 가드레일 설치
            val = st.slider(
                label=f"**{item['원료명']}** ({item['min']}% ~ {item['max']}%)",
                min_value=float(item['min']), 
                max_value=float(item['max']), 
                value=float(item['AI']),
                step=0.01,
                key=f"strict_sld_{item['원료명']}"
            )
            adj_values[item['원료명']] = val
            sum_others += val

    # 2. 정제수 오토 밸런싱 (100% 무결성 보장)
    water_val = max(0.0, 100.0 - sum_others)
    adj_values["정제수"] = water_val

    # 3. 배합표 데이터 생성 및 즉시 렌더링
    display_df = []
    for item in formula:
        nm = item['원료명']
        re = item['AI']
        cu = adj_values.get(nm, water_val)
        display_df.append({
            "원료명": nm, "추천(%)": f"{re:.2f}", "개선(%)": f"{cu:.2f}",
            "Delta": f"{cu - re:+.2f}", "사용목적": item['사용목적'], "주의사항": item['주의사항']
        })
    
    # 빈 공간에 표를 강제로 밀어넣음
    table_placeholder.table(pd.DataFrame(display_df))
    
    # 상단 상태바 업데이트
    if water_val < water_cfg['min']:
        st.error(f"⚠️ 합계 유지 중이나 정제수 부족: {water_val:.2f}% (최소 {water_cfg['min']}% 필요)")
    else:
        st.success(f"✅ 합계 100.00% 자동 유지 중 (정제수: {water_val:.2f}%)")
