import streamlit as st

# 1. 페이지 설정 및 디자인
st.set_page_config(
    page_title="Gas PPM 계산기",
    page_icon="🧪",
    layout="centered"
)

# 2. 화학 성분 데이터베이스 (분자량, 밀도, 순도)
chemicals = {
    "Water (H2O)": {"mw": 18.015, "density": 1.00, "purity": 100.0},
    "Ethanol": {"mw": 46.07, "density": 0.789, "purity": 95.0},
    "THF": {"mw": 72.11, "density": 0.89, "purity": 99.5},
    "Toluene": {"mw": 92.14, "density": 0.87, "purity": 99.5},
    "n-Hexane": {"mw": 86.18, "density": 0.66, "purity": 95.0}
}

# 3. 메인 화면 타이틀
st.title("🧪 가스 농도 대비 액체 주입량 계산기")
st.markdown("""
실험 시 **먼저 주입한 공기(Air)의 양**을 기준으로, 목표 PPM을 맞추기 위해 필요한 **액체 시약의 부피**를 계산합니다.
""")

st.divider()

# 4. 사용자 입력 섹션
st.subheader("1. 실험 조건 입력")

# 성분 선택 (클릭 버튼형 셀렉트박스)
selected_name = st.selectbox("분석할 성분을 선택하세요", list(chemicals.keys()))
chem = chemicals[selected_name]

col1, col2 = st.columns(2)

with col1:
    # Air 주입량 입력 (사용자 요청: '전체 용량' 대신 'Air 양')
    air_volume = st.number_input(
        "공기(Air) 주입량 (L)", 
        min_value=0.0, 
        value=12.0, 
        step=0.1,
        help="용기에 먼저 채워 넣은 공기의 양을 입력하세요."
    )

with col2:
    # 목표 PPM 입력
    target_ppm = st.number_input(
        "목표 농도 (PPM)", 
        min_value=0.0, 
        value=1000.0, 
        step=10.0
    )

# 5. 계산 로직
# 상수: 25°C, 1기압 기준 기체 몰부피 (24.45 L/mol)
molar_volume = 24.45 
purity_decimal = chem['purity'] / 100

# 계산 공식: 
# 필요한 액체 부피(uL) = (PPM * 분자량 * Air량) / (몰부피 * 밀도 * 순도)
required_ul = (target_ppm * chem['mw'] * air_volume) / (molar_volume * chem['density'] * purity_decimal)

st.divider()

# 6. 결과 출력 섹션
st.subheader("2. 계산 결과")

# 강조 박스에 결과 표시
st.success(f"### 필요한 {selected_name} 주입량: **{required_ul:.2f} μL**")

# 상세 요약 정보
res_col1, res_col2, res_col3 = st.columns(3)
res_col1.metric("선택 성분", selected_name)
res_col2.metric("Air 주입량", f"{air_volume} L")
res_col3.metric("목표 농도", f"{target_ppm} PPM")

# 7. 참고 정보 (수식 및 물리량)
with st.expander("계산 수식 및 물리량 상세 정보 확인"):
    st.latex(r"Volume_{liq} (\mu L) = \frac{PPM \times MW \times V_{air}}{V_m \times \rho \times (Purity/100)}")
    st.write(f"**적용된 물리량:**")
    st.write(f"- 분자량($MW$): {chem['mw']} g/mol")
    st.write(f"- 밀도($\\rho$): {chem['density']} g/mL")
    st.write(f"- 시약 순도: {chem['purity']}%")
    st.write(f"- 기체 몰부피($V_m$): {molar_volume} L/mol (25°C 기준)")

st.info(f"💡 **실험 팁:** {air_volume}L의 Air가 담긴 용기에 위 시약을 **{required_ul:.2f} 마이크로리터** 주입 후, 시약이 완전히 기화될 때까지 기다리면 {target_ppm} PPM의 혼합 가스가 제조됩니다.")