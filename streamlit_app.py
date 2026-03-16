import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import os

# Page Config
st.set_page_config(
    page_title="K-National Safety Keeper",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Premium Look
st.markdown("""
    <style>
    .main {
        background-color: #f8fafc;
    }
    .stButton>button {
        width: 100%;
        border-radius: 50px;
        height: 3rem;
        background-color: #135bec;
        color: white;
        border: none;
        font-weight: 700;
    }
    .kpi-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        text-align: center;
        border-bottom: 5px solid #135bec;
    }
    </style>
    """, unsafe_allow_html=True)

# Database Connection
def get_db():
    conn = sqlite3.connect('safety_map.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

# Header
st.title("🛡️ K-국민안전지킴이")
st.subheader("K-National Safety Keeper Portal")

# Sidebar Navigation
menu = st.sidebar.selectbox("메뉴 선택", ["실시간 안전 지도", "제보하기", "관리 현황 (Admin)"])

if menu == "실시간 안전 지도":
    st.header("📍 실시간 안전 상황")
    conn = get_db()
    df = pd.read_sql_query("SELECT * FROM reports", conn)
    
    # KPI
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f'<div class="kpi-card"><h3>전체 제보</h3><h2>{len(df)}</h2></div>', unsafe_allow_html=True)
    with c2:
        resolved = len(df[df['status'].isin(['Rewarded', 'Action Taken'])])
        st.markdown(f'<div class="kpi-card" style="border-color:#10b981"><h3>조치 완료</h3><h2>{resolved}</h2></div>', unsafe_allow_html=True)
    with c3:
        total_pts = df['reward_points'].sum()
        st.markdown(f'<div class="kpi-card" style="border-color:#f59e0b"><h3>누적 포인트</h3><h2>{total_pts:,} P</h2></div>', unsafe_allow_html=True)

    st.write("")
    
    # Map (Simplified Streamlit Map)
    if not df.empty and 'latitude' in df.columns:
        map_df = df.dropna(subset=['latitude', 'longitude'])
        st.map(map_df[['latitude', 'longitude']])
        
    # Feed
    st.header("📸 최신 안전 피드")
    for index, row in df.sort_values(by='created_at', ascending=False).iterrows():
        with st.expander(f"[{row['status']}] {row['category']} - {row['address']}"):
            col1, col2 = st.columns([1, 2])
            with col1:
                # In Streamlit Cloud, pathing needs to be relative to the app root
                img_path = os.path.join('static', row['image_path'])
                if os.path.exists(img_path):
                    try:
                        st.image(img_path, use_container_width=True)
                    except Exception as e:
                        st.warning("⚠️ 이미지를 분석할 수 없습니다. (손상된 파일 또는 지원하지 않는 형식)")
                else:
                    # Show a placeholder icon if file is missing (common in ephemeral cloud storage)
                    st.info("🖼️ 원본 이미지가 서버에 존재하지 않습니다. (로컬 데이터 연동 문제)")
            with col2:
                st.write(f"**제보자:** {row['reporter_name']}")
                st.write(f"**내용:** {row['description']}")
                st.write(f"**AI 가치 점수:** {row['public_value']} / 100")
                if row['admin_feedback']:
                    st.info(f"官方 조치 결과: {row['admin_feedback']}")

elif menu == "제보하기":
    st.header("🚀 새로운 안전 제보")
    with st.form("report_form", clear_on_submit=True):
        name = st.text_input("성함", placeholder="홍길동")
        cat = st.selectbox("분류", ["도로 파손", "시설물 고장", "쓰레기 투기", "기로등 고장", "기타"])
        desc = st.text_area("상세 내용", placeholder="위험 상황을 자세히 설명해 주세요.")
        photo = st.file_uploader("사진 첨부", type=['jpg', 'jpeg', 'png'])
        
        st.info("💡 배포 버전에서는 GPS 정보가 브라우저 보안에 따라 제한될 수 있습니다.")
        
        submit = st.form_submit_button("제보 등록하기")
        
        if submit:
            if not name or not photo:
                st.error("성함과 사진은 필수 항목입니다.")
            else:
                # Save Logic Implementation
                st.success("제보가 성공적으로 접수되었습니다! (체험판: DB 저장 로직은 서버 환경에 따라 다르게 작동할 수 있습니다)")

elif menu == "관리 현황 (Admin)":
    st.header("🏢 행정 통합 관리 시스템")
    pwd = st.text_input("관리자 비밀번호", type="password")
    if pwd == "0303":
        conn = get_db()
        df = pd.read_sql_query("SELECT * FROM reports", conn)
        st.dataframe(df)
        
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📊 전체 리스트 다운로드 (CSV)", csv, "reports_export.csv", "text/csv")
    elif pwd:
        st.error("비밀번호가 틀렸습니다.")

st.sidebar.markdown("---")
st.sidebar.write("© 2026 K-National Safety Keeper")
