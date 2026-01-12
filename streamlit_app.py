import streamlit as st
import pandas as pd

# 1. 페이지 설정
st.set_page_config(page_title="정밀 PPM 계산기 Pro", page_icon="🧪", layout="wide")

# 2. 세션 상태 초기화 (사용자가 추가한 데이터를 유지하기 위함)
if 'chem_data' not in st.session_state:
    st.session_state.chem_data = [
        {"성분명": "Water", "분자량": 18.015, "밀도": 1.000, "순도": 100.0},
        {"성분명": "Ethanol", "분자량": 46.070, "밀도": 0.789, "순도": 95.0},
        {"성분명": "THF", "분자량": 72.110, "밀도": 0.890, "순도": 99.5},
        {"성분명": "Toluene", "분자량": 92.140, "밀도": 0.870, "순도": 99.5},
        {"성분명": "n-Hexane", "분자량": 86.180, "밀도": 0.660, "순도": 95.0}
    ]

st.title("🧪 정밀 가스 농도 계산기 Pro")
st.markdown("기존 성분을 수정하거나, **새로운 시약 성분을 직접 추가**하여 계산할 수 있습니다.")

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

# 4. 성분 데이터 관리 섹션
st.subheader("1. 성분 리스트 관리")
col_table, col_add = st.columns([2, 1])

with col_add:
    with st.expander("➕ 새 성분 직접 추가", expanded=True):
        with st.form("new_chem_form", clear_on_submit=True):
            new_name = st.text_input("성분명 (예: Acetone)")
            new_mw = st.number_input("분자량 (g/mol)", min_value=0.0, format="%.3f")
            new_density = st.number_input("밀도 (g/mL)", min_value=0.0, format="%.3f")
            new_purity = st.number_input("순도 (%)", min_value=0.0, max_value=100.0, value=100.0)
            submit_btn = st.form_submit_button("리스트에 추가")
            
            if submit_btn:
                if new_name:
                    new_item = {"성분명": new_name, "분자량": new_mw, "밀도": new_density, "순도": new_purity}
                    st.session_state.chem_data.append(new_item)
                    st.rerun()
                else:
                    st.error("성분명을 입력해주세요.")

with col_table:
    # 데이터 에디터를 통해 기존 데이터 수정 및 삭제 가능
    df = pd.DataFrame(st.session_state.chem_data)
    edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True, key="data_editor")
    # 에디터에서 수정된 내용을 세션 상태에 반영
    st.session_state.chem_data = edited_df.to_dict('records')

st.divider()

# 5. 계산 조건 입력 섹션
st.subheader("2. 주입 조건 입력")
c1, c2, c3 = st.columns(3)

with c1:
    target_chem = st.selectbox("분석할 성분 선택", edited_df["성분명"].tolist())
with c2:
    air_vol = st.number_input("공기(Air) 주입량 (L)", value=12.0, step=0.1)
with c3:
    target_ppm = st.number_input("목표 농도 (PPM)", value=1000.0, step=10.0)

# 선택된 성분 데이터 추출
row = edited_df[edited_df["성분명"] == target_chem].iloc[0]
mw = row["분자량"]
density = row["밀도"]
purity_val = row["순도"] / 100

# 계산 공식
required_ul = (target_ppm * mw * air_vol) / (molar_volume * density * purity_val * 1000)

# 6. 최종 결과 및 도구 추천
st.divider()
res_col, tool_col = st.columns(2)

with res_col:
    st.markdown("### 📊 계산 결과")
    st.markdown(f"""
    <div style="background-color:#f0f2f6; padding:20px; border-radius:10px; border-left: 5px solid #ff4b4b;">
        <p style="font-size:16px; margin-bottom:5px;">필요한 <b>{target_chem}</b> 주입량</p>
        <h1 style="color:#ff4b4b; margin-top:0;">{required_ul:.2f} μL</h1>
    </div>
    """, unsafe_allow_html=True)

with tool_col:
    st.markdown("### 🛠️ 추천 도구 및 세팅")
    if required_ul <= 10:
        st.warning("📍 **추천 도구: 마이크로 실린지 (10 μL)**")
        st.write(f"**실린지 눈금 확인:** {required_ul:.2f} 단위를 확인하여 주입하세요.")
    else:
        st.success("📍 **추천 도구: 마이크로 피펫 (100 μL)**")
        st.markdown(f"""
        <div style="background-color:#e8f4ea; padding:15px; border-radius:10px; border: 1px solid #28a745;">
            <p style="margin:0; font-weight:bold; color:#1e7e34;">피펫 다이얼 세팅 값:</p>
            <h2 style="margin:5px 0; color:#1e7e34;">{required_ul:.1f}</h2>
            <p style="margin:0; font-size:14px;">(100μL 피펫의 숫자창을 위와 같이 맞추세요)</p>
        </div>
        """, unsafe_allow_html=True)

st.info(f"💡 **실험 가이드:** {temp}°C 환경에서 {air_vol}L의 Air에 시약을 주입하면 {target_ppm} PPM이 됩니다.")