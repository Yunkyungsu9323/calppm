import streamlit as st
import pandas as pd

# 1. 페이지 설정
st.set_page_config(page_title="정밀 PPM 계산기", page_icon="🧪", layout="wide")

# 2. 기본 화학 데이터
default_data = [
    {"성분명": "Water", "분자량": 18.015, "밀도": 1.000, "순도": 100.0},
    {"성분명": "Ethanol", "분자량": 46.070, "밀도": 0.789, "순도": 95.0},
    {"성분명": "THF", "분자량": 72.110, "밀도": 0.890, "순도": 99.5},
    {"성분명": "Toluene", "분자량": 92.140, "밀도": 0.870, "순도": 99.5},
    {"성분명": "n-Hexane", "분자량": 86.180, "밀도": 0.660, "순도": 95.0}
]

st.title("🧪 정밀 가스 농도 계산기")
st.info("💡 엑셀 수치(52.5)와 맞추려면 왼쪽 사이드바에서 온도를 **23.5°C**로 설정해 보세요.")

# 3. 환경 설정 사이드바
with st.sidebar:
    st.header("⚙️ 환경 설정")
    temp = st.slider("실험실 온도 (°C)", min_value=0.0, max_value=40.0, value=25.0, step=0.1)
    molar_volume = 22.4 * (273.15 + temp) / 273.15
    st.write(f"현재 온도 몰부피: **{molar_volume:.3f} L/mol**")
    st.divider()
    st.write("📍 **도구 사양**")
    st.write("- 마이크로 실린지: Max 10 μL")
    st.write("- 마이크로 피펫: Max 100 μL")

st.divider()

# 4. 데이터 편집 섹션
st.subheader("1. 성분 데이터 확인")
df_raw = pd.DataFrame(default_data)
edited_df = st.data_editor(df_raw, num_rows="dynamic", use_container_width=True)

st.divider()

# 5. 계산 섹션
st.subheader("2. 주입 조건 입력")
col1, col2, col3 = st.columns(3)

with col1:
    target_chem = st.selectbox("분석할 성분 선택", edited_df["성분명"].tolist())
with col2:
    air_vol = st.number_input("공기(Air) 주입량 (L)", value=12.0, step=0.1)
with col3:
    target_ppm = st.number_input("목표 농도 (PPM)", value=1000.0, step=10.0)

row = edited_df[edited_df["성분명"] == target_chem].iloc[0]
mw = row["분자량"]
density = row["밀도"]
purity_val = row["순도"] / 100

# 계산 로직
required_ul = (target_ppm * mw * air_vol) / (molar_volume * density * purity_val * 1000)

# 6. 최종 결과 및 도구 추천 출력
st.divider()
c1, c2 = st.columns([1, 1])

with c1:
    st.markdown("### 📊 계산 결과")
    st.markdown(f"""
    <div style="background-color:#f0f2f6; padding:20px; border-radius:10px; border-left: 5px solid #ff4b4b;">
        <p style="font-size:16px; margin-bottom:5px;">필요한 <b>{target_chem}</b> 주입량</p>
        <h1 style="color:#ff4b4b; margin-top:0;">{required_ul:.2f} μL</h1>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("### 🛠️ 추천 도구 및 세팅")
    if required_ul <= 10:
        st.warning("📍 **추천 도구: 마이크로 실린지 (10 μL)**")
        st.write(f"**실린지 눈금 확인:** {required_ul:.2f} 단위를 확인하여 흡입하세요.")
    else:
        st.success("📍 **추천 도구: 마이크로 피펫 (100 μL)**")
        st.markdown(f"""
        <div style="background-color:#e8f4ea; padding:15px; border-radius:10px; border: 1px solid #28a745;">
            <p style="margin:0; font-weight:bold; color:#1e7e34;">피펫 다이얼 세팅 값:</p>
            <h2 style="margin:5px 0; color:#1e7e34;">{required_ul:.1f}</h2>
            <p style="margin:0; font-size:14px;">(100μL 피펫의 숫자창을 위와 같이 맞추세요)</p>
        </div>
        """, unsafe_allow_html=True)

st.divider()
st.info(f"✅ **실험 가이드:** {temp}°C 환경에서 {air_vol}L의 Air에 시약을 주입하고 완전히 기화시키면 {target_ppm} PPM이 됩니다.")

with st.expander("사용한 계산 공식 보기"):
    st.latex(r"V_{liq}(\mu L) = \frac{PPM \times MW(g/mol) \times V_{air}(L)}{V_m(L/mol) \times \rho(g/mL) \times (Purity/100) \times 1000}")