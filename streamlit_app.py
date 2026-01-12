import streamlit as st
import pandas as pd

# 1. 페이지 설정
st.set_page_config(page_title="정밀 PPM 계산기 Safety Pro", page_icon="🧪", layout="wide")

# 2. 화학 성분 데이터 및 안전 정보 정의
if 'chem_data' not in st.session_state:
    st.session_state.chem_data = [
        {"성분명": "Water", "분자량": 18.015, "밀도": 1.000, "순도": 100.0, "GHS": "✅ 안전", "주의사항": "특이사항 없음", "MSDS_ID": "water"},
        {"성분명": "Ethanol", "분자량": 46.070, "밀도": 0.789, "순도": 95.0, "GHS": "🔥 인화성, ⚠️ 자극성", "주의사항": "화기 주의, 흡입 시 어지러움 유발", "MSDS_ID": "ethanol"},
        {"성분명": "THF", "분자량": 72.110, "밀도": 0.890, "순도": 99.5, "GHS": "🔥 인화성, ⚠️ 자극성, ☣️ 발암성 의심", "주의사항": "유기용제 전용 마스크 착용, 장기 노출 금지", "MSDS_ID": "tetrahydrofuran"},
        {"성분명": "Toluene", "분자량": 92.140, "밀도": 0.870, "순도": 99.5, "GHS": "🔥 인화성, 💀 독성, ⚠️ 자극성", "주의사항": "생식독성 주의, 환기 필수, 보호장구 착용", "MSDS_ID": "toluene"},
        {"성분명": "n-Hexane", "분자량": 86.180, "밀도": 0.660, "순도": 95.0, "GHS": "🔥 인화성, 💀 독성, 🌳 환경유해성", "주의사항": "중추신경계 손상 주의, 대량 흡입 금지", "MSDS_ID": "n-hexane"}
    ]

st.title("🧪 정밀 가스 농도 계산기 & 안전 가이드")

# 3. 환경 설정 사이드바
with st.sidebar:
    st.header("⚙️ 환경 설정")
    temp = st.slider("실험실 온도 (°C)", min_value=0.0, max_value=40.0, value=25.0, step=0.1)
    molar_volume = 22.4 * (273.15 + temp) / 273.15
    st.write(f"현재 온도 몰부피: **{molar_volume:.3f} L/mol**")
    st.divider()
    st.write("📍 **사용 도구**")
    st.write("- 10 μL 마이크로 실린지")
    st.write("- 100 μL 마이크로 피펫")

# 4. 데이터 관리 (성분 추가/수정)
with st.expander("📝 성분 리스트 및 데이터 관리"):
    df = pd.DataFrame(st.session_state.chem_data)
    edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)
    st.session_state.chem_data = edited_df.to_dict('records')

st.divider()

# 5. 주입 조건 및 계산
st.subheader("1. 실험 조건 및 계산")
c1, c2, c3 = st.columns(3)

with c1:
    target_chem = st.selectbox("분석할 성분 선택", edited_df["성분명"].tolist())
with c2:
    air_vol = st.number_input("공기(Air) 주입량 (L)", value=12.0)
with c3:
    target_ppm = st.number_input("목표 농도 (PPM)", value=1000.0)

# 선택된 성분 정보
row = edited_df[edited_df["성분명"] == target_chem].iloc[0]
mw, density, purity = row["분자량"], row["밀도"], row["순도"] / 100

# 계산
required_ul = (target_ppm * mw * air_vol) / (molar_volume * density * purity * 1000)

# 결과 출력
res_col, safety_col = st.columns([1, 1.2])

with res_col:
    st.markdown("### 📊 계산 결과")
    st.markdown(f"""
    <div style="background-color:#f0f2f6; padding:20px; border-radius:10px; border-left: 5px solid #ff4b4b;">
        <p style="margin:0;">필요한 <b>{target_chem}</b> 주입량</p>
        <h1 style="color:#ff4b4b; margin-top:0;">{required_ul:.2f} μL</h1>
    </div>
    """, unsafe_allow_html=True)
    
    # 도구 추천
    if required_ul <= 10:
        st.warning("📍 **추천 도구:** 마이크로 실린지 (10μL)")
    else:
        st.success(f"📍 **추천 도구:** 마이크로 피펫 (다이얼: **{required_ul:.1f}**)")

with safety_col:
    st.markdown("### ⚠️ 안전 정보 (GHS)")
    # 안전 정보 표시
    safety_box_color = "#fff3cd" if "🔥" in str(row["GHS"]) or "💀" in str(row["GHS"]) else "#d4edda"
    
    st.markdown(f"""
    <div style="background-color:{safety_box_color}; padding:15px; border-radius:10px; border: 1px solid #ffeeba;">
        <p style="margin:0; font-weight:bold;">유해성 구분:</p>
        <p style="font-size:18px; margin:5px 0;">{row["GHS"]}</p>
        <hr style="margin:10px 0; border:0; border-top:1px solid #eee;">
        <p style="margin:0; font-weight:bold;">실험 시 주의사항:</p>
        <p style="margin:5px 0;">{row["주의사항"]}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # MSDS 외부 링크 (PubChem 활용)
    search_url = f"https://pubchem.ncbi.nlm.nih.gov/#query={target_chem}"
    st.link_button(f"🌐 {target_chem} MSDS 상세 정보 확인", search_url)

st.divider()
st.caption("본 앱의 안전 정보는 참고용이며, 실제 실험 전 반드시 소속 기관의 MSDS 원본을 확인하시기 바랍니다.")