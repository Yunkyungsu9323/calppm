import streamlit as st
import pandas as pd

# 1. 페이지 설정
st.set_page_config(page_title="정밀 PPM 계산기 Safety Pro", page_icon="🧪", layout="wide")

# 기본 데이터 정의
default_list = [
    {"성분명": "Water", "분자량": 18.015, "밀도": 1.000, "순도": 100.0, "GHS": "✅ 안전", "주의사항": "특이사항 없음"},
    {"성분명": "Ethanol", "분자량": 46.070, "밀도": 0.789, "순도": 95.0, "GHS": "🔥 인화성", "주의사항": "화기 주의"},
    {"성분명": "THF", "분자량": 72.110, "밀도": 0.890, "순도": 99.5, "GHS": "🔥 인화성, ⚠️ 자극성", "주의사항": "환기 필수"},
    {"성분명": "Toluene", "분자량": 92.140, "밀도": 0.870, "순도": 99.5, "GHS": "🔥 인화성, 💀 독성", "주의사항": "보호구 착용"},
    {"성분명": "n-Hexane", "분자량": 86.180, "밀도": 0.660, "순도": 95.0, "GHS": "🔥 인화성, 💀 독성", "주의사항": "흡입 금지"}
]

# 2. 세션 상태 초기화 및 데이터 강제 업데이트
if 'chem_data' not in st.session_state or st.sidebar.button("🔄 데이터 초기화 (리셋)"):
    st.session_state.chem_data = default_list

st.title("🧪 정밀 가스 농도 계산기 & 안전 가이드")

# 3. 환경 설정 사이드바
with st.sidebar:
    st.header("⚙️ 환경 설정")
    temp = st.slider("실험실 온도 (°C)", min_value=0.0, max_value=40.0, value=25.0, step=0.1)
    molar_volume = 22.4 * (273.15 + temp) / 273.15
    st.write(f"현재 온도 몰부피: **{molar_volume:.3f} L/mol**")
    st.divider()
    st.info("📍 **도구 사양**\n- 실린지: ~10 μL\n- 피펫: 10~100 μL")

# 4. 데이터 관리 섹션
st.subheader("1. 성분 데이터 관리")
col_edit, col_add = st.columns([2, 1])

with col_add:
    with st.expander("➕ 새 성분 직접 추가", expanded=True):
        with st.form("add_form", clear_on_submit=True):
            name = st.text_input("성분명")
            mw = st.number_input("분자량", min_value=0.0, format="%.3f")
            dens = st.number_input("밀도", min_value=0.0, format="%.3f")
            pur = st.number_input("순도(%)", min_value=0.0, max_value=100.0, value=100.0)
            ghs = st.text_input("GHS (예: 🔥 인화성)")
            note = st.text_input("주의사항")
            if st.form_submit_button("리스트에 추가"):
                if name:
                    new_item = {"성분명": name, "분자량": mw, "밀도": dens, "순도": pur, "GHS": ghs, "주의사항": note}
                    st.session_state.chem_data.append(new_item)
                    st.rerun()

with col_edit:
    df = pd.DataFrame(st.session_state.chem_data)
    # 컬럼 누락 방지
    for c in ["GHS", "주의사항"]:
        if c not in df.columns: df[c] = ""
    edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)
    st.session_state.chem_data = edited_df.to_dict('records')

st.divider()

# 5. 주입 조건 및 계산
st.subheader("2. 주입 조건 및 결과")
c1, c2, c3 = st.columns(3)

with c1:
    target_chem = st.selectbox("분석할 성분 선택", edited_df["성분명"].tolist())
with c2:
    air_vol = st.number_input("Air 주입량 (L)", value=12.0)
with c3:
    target_ppm = st.number_input("목표 PPM", value=1000.0)

# 계산 로직
row = edited_df[edited_df["성분명"] == target_chem].iloc[0]
req_ul = (target_ppm * row["분자량"] * air_vol) / (molar_volume * row["밀도"] * (row["순도"]/100) * 1000)

# 6. 결과 및 안전 정보 표시
res_c, safe_c = st.columns(2)

with res_c:
    st.markdown(f"""
    <div style="background-color:#f0f2f6; padding:20px; border-radius:10px; border-left: 5px solid #ff4b4b;">
        <p style="margin:0;">필요한 <b>{target_chem}</b> 주입량</p>
        <h1 style="color:#ff4b4b; margin-top:0;">{req_ul:.2f} μL</h1>
    </div>
    """, unsafe_allow_html=True)
    
    if req_ul <= 10:
        st.warning(f"📍 **추천:** 마이크로 실린지 (10μL)")
    else:
        st.success(f"📍 **추천:** 마이크로 피펫 (세팅: **{req_ul:.1f}**)")

with safe_c:
    # 빈칸일 경우 기본 문구 처리 (핵심 해결책)
    ghs_display = row["GHS"] if str(row["GHS"]).strip() != "" else "⚠️ GHS 정보를 입력해주세요"
    note_display = row["주의사항"] if str(row["주의사항"]).strip() != "" else "📝 주의사항을 입력해주세요"
    
    bg = "#fff3cd" if any(x in str(ghs_display) for x in ["🔥", "💀", "☣️", "⚠️"]) else "#d4edda"
    
    st.markdown(f"""
    <div style="background-color:{bg}; padding:15px; border-radius:10px; border:1px solid #ffeeba;">
        <p style="margin:0; font-weight:bold;">⚠️ 안전 정보:</p>
        <p style="font-size:16px; margin:5px 0;">{ghs_display}</p>
        <p style="margin:10px 0 0 0; font-weight:bold;">💡 주의사항:</p>
        <p style="margin:0;">{note_display}</p>
    </div>
    """, unsafe_allow_html=True)

st.link_button(f"🌐 {target_chem} MSDS 상세 검색 (외부 링크)", f"https://pubchem.ncbi.nlm.nih.gov/#query={target_chem}")