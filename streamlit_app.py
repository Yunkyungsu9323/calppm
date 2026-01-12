import streamlit as st
import pandas as pd

# 1. 페이지 설정
st.set_page_config(page_title="정밀 PPM 계산기 Safety Pro", page_icon="🧪", layout="wide")

# 사용자가 제공한 표 기반 데이터 정의
default_list = [
    {"성분명": "물 (Water)", "분자량": 18.015, "밀도": 1.000, "순도": 100.0, "인화성": "없음", "독성/위험성": "거의 없음", "특이사항": "전기 기구 접촉 주의"},
    {"성분명": "에탄올 (Ethanol)", "분자량": 46.070, "밀도": 0.789, "순도": 95.0, "인화성": "높음", "독성/위험성": "눈 자극, 장기 노출 시 간 손상", "특이사항": "화기 엄금"},
    {"성분명": "THF (테트라하이드로퓨란)", "분자량": 72.110, "밀도": 0.890, "순도": 99.5, "인화성": "매우 높음", "독성/위험성": "심한 눈 자극, 발암성 의심", "특이사항": "과산화물 형성(폭발 위험)"},
    {"성분명": "톨루엔 (Toluene)", "분자량": 92.140, "밀도": 0.870, "순도": 99.5, "인화성": "높음", "독성/위험성": "생식 독성, 신경계 손상, 흡입 주의", "특이사항": "유기용매 중 독성 강함"},
    {"성분명": "n-헥산 (n-Hexane)", "분자량": 86.180, "밀도": 0.660, "순도": 95.0, "인화성": "매우 높음", "독성/위험성": "말초 신경 장애, 생식 독성", "특이사항": "장기 노출 시 마비 증상"}
]

# 2. 세션 상태 초기화 및 데이터 강제 업데이트
if 'chem_data' not in st.session_state or st.sidebar.button("🔄 데이터 초기화 (신규 정보 반영)"):
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
    with st.expander("➕ 새 성분 직접 추가"):
        with st.form("add_form", clear_on_submit=True):
            name = st.text_input("성분명")
            mw = st.number_input("분자량", min_value=0.0, format="%.3f")
            dens = st.number_input("밀도", min_value=0.0, format="%.3f")
            pur = st.number_input("순도(%)", min_value=0.0, max_value=100.0, value=100.0)
            inhwa = st.text_input("인화성 (예: 높음)")
            tox = st.text_input("독성 및 위험성")
            spec = st.text_input("특이사항")
            if st.form_submit_button("리스트에 추가"):
                if name:
                    new_item = {"성분명": name, "분자량": mw, "밀도": dens, "순도": pur, "인화성": inhwa, "독성/위험성": tox, "특이사항": spec}
                    st.session_state.chem_data.append(new_item)
                    st.rerun()

with col_edit:
    df = pd.DataFrame(st.session_state.chem_data)
    # 컬럼 누락 방지 처리
    for c in ["인화성", "독성/위험성", "특이사항"]:
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
    air_vol = st.number_input("공기(Air) 주입량 (L)", value=12.0)
with c3:
    target_ppm = st.number_input("목표 농도 (PPM)", value=1000.0)

# 선택된 행 데이터 추출
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
        st.warning(f"📍 **추천 도구:** 마이크로 실린지 (10μL)")
    else:
        st.success(f"📍 **추천 도구:** 마이크로 피펫 (세팅 값: **{req_ul:.1f}**)")

with safe_c:
    # 인화성 정보에 따른 아이콘 및 색상 변경
    inhwa_val = str(row["인화성"])
    icon = "🔥 " if "높음" in inhwa_val else "✅ "
    bg_color = "#fff3cd" if "높음" in inhwa_val else "#d4edda"
    
    st.markdown(f"""
    <div style="background-color:{bg_color}; padding:15px; border-radius:10px; border:1px solid #ffeeba;">
        <p style="margin:0; font-weight:bold;">⚠️ 물질 안전 정보</p>
        <p style="margin:5px 0;"><b>인화성:</b> {icon}{inhwa_val}</p>
        <p style="margin:5px 0;"><b>독성 및 위험성:</b> {row["독성/위험성"]}</p>
        <hr style="margin:10px 0; border:0; border-top:1px solid #ccc;">
        <p style="margin:0; font-weight:bold;">💡 특이사항 (실험 주의사항)</p>
        <p style="margin:5px 0; color:#d9534f; font-weight:bold;">{row["특이사항"]}</p>
    </div>
    """, unsafe_allow_html=True)

st.link_button(f"🌐 {target_chem} 상세 MSDS 검색", f"https://pubchem.ncbi.nlm.nih.gov/#query={target_chem}")