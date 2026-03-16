import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import os
import folium
from streamlit_folium import st_folium
import base64
from PIL import Image
import io

# Page Config
st.set_page_config(
    page_title="K-국민안전지킴이 (K-National Safety Keeper)",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Premium Global CSS (Replicating style.css) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    :root {
        --primary: #135bec;
        --secondary: #00d2ff;
        --accent: #ff9800;
        --bg-dark: #0f172a;
        --text-dark: #f1f5f9;
        --radius-lg: 24px;
        --shadow-premium: 0 10px 25px -5px rgba(0, 0, 0, 0.2);
    }

    .stApp {
        background-color: var(--bg-dark);
        font-family: 'Inter', sans-serif;
    }

    /* Hide Sidebar & Standard Nav */
    [data-testid="stSidebarNav"] {display: none;}
    
    /* Premium Header */
    .custom-header {
        position: fixed;
        top: 0; left: 0; right: 0;
        background: rgba(19, 91, 236, 0.9);
        backdrop-filter: blur(12px);
        padding: 0.8rem 2rem;
        z-index: 999;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid rgba(255,255,255,0.1);
        color: white;
    }

    .nav-links a {
        color: white;
        text-decoration: none;
        margin-left: 1.5rem;
        font-weight: 600;
        font-size: 0.95rem;
        opacity: 0.8;
        transition: opacity 0.3s;
    }
    .nav-links a:hover { opacity: 1; }

    /* Hero Section */
    .hero-box {
        background: linear-gradient(135deg, #135bec 0%, #00d2ff 100%);
        padding: 6rem 2rem 4rem 2rem;
        text-align: center;
        border-radius: 0 0 50px 50px;
        margin-bottom: 3rem;
        box-shadow: var(--shadow-premium);
        color: white;
    }

    /* Glass Cards */
    .glass-card {
        background: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: var(--radius-lg);
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        transition: transform 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    .glass-card:hover { transform: translateY(-5px); }

    .kpi-card {
        text-align: center;
        border-bottom: 4px solid var(--primary);
    }
    .kpi-val {
        font-size: 2.8rem;
        font-weight: 900;
        color: #ffffff;
        margin: 0;
    }
    .kpi-lab {
        font-size: 0.85rem;
        opacity: 0.7;
        font-weight: 600;
        letter-spacing: 1px;
    }

    /* Report Grid */
    .report-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
        gap: 1.5rem;
    }

    /* Photo Handling */
    .card-img {
        width: 100%;
        height: 200px;
        object-fit: cover;
        border-radius: 15px;
        margin-bottom: 1rem;
    }

    .badge-status {
        padding: 4px 12px;
        border-radius: 50px;
        font-size: 0.75rem;
        font-weight: 800;
        background: rgba(19, 91, 236, 0.2);
        color: #60a5fa;
        border: 1px solid rgba(96, 165, 250, 0.3);
    }

    /* Sidebar Overrides */
    section[data-testid="stSidebar"] {
        background-color: #0f172a !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Database & AI ---
def get_db():
    conn = sqlite3.connect('safety_map.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def sim_analysis(cat):
    return {"val": 85 if cat == "도로 파손" else 50, "urb": "HIGH" if cat == "도로 파손" else "MID"}

# --- Global Header ---
st.markdown("""
    <div class="custom-header">
        <div style="font-weight: 800; font-size: 1.2rem;">🛡️ K-국민안전지킴이</div>
        <div class="nav-links">
            <a href="?page=home">홈</a>
            <a href="?page=map">안전지도</a>
            <a href="?page=report">제보하기</a>
            <a href="?page=admin">관리자</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Navigation via Query Params (Simulation)
query_params = st.query_params
page = query_params.get("page", "home")

# Fallback Sidebar Menu for Ease of Use in Streamlit
with st.sidebar:
    st.markdown("### 🧭 NAVIGATION")
    menu = st.radio("Menu", ["🏠 홈 (Home)", "📍 안전 지도 (Map)", "🚀 제보하기 (Report)", "⚙️ 관리자 (Admin)"])

# Shared DB Connection
conn = get_db()

# --- HOME PAGE ---
if menu == "🏠 홈 (Home)":
    # Hero Section
    st.markdown("""
        <div class="hero-box">
            <h1 style="font-size: 3.5rem; font-weight: 800; margin-bottom: 1rem;">K-국민안전지킴이</h1>
            <p style="font-size: 1.4rem; opacity: 0.9; max-width: 800px; margin: 0 auto;">
                수만 명의 시민과 함께 더 안전한 사회를 만듭니다.<br>사진 한 장이면 AI가 즉시 분석하여 대응합니다.
            </p>
        </div>
        """, unsafe_allow_html=True)

    # Dashboard/Feed
    st.container()
    col_a, col_b = st.columns([2, 1])
    
    with col_a:
        st.markdown("## 🔥 실시간 안전 피드")
        df = pd.read_sql_query("SELECT * FROM reports ORDER BY id DESC LIMIT 10", conn)
        
        if df.empty:
            st.info("현재 신고된 내역이 없습니다. 첫 번째 제보자가 되어주세요!")
        else:
            for _, row in df.iterrows():
                with st.container():
                    st.markdown(f'''
                    <div class="glass-card">
                        <div style="display: flex; gap: 1.5rem;">
                            <div style="flex: 1;">
                                <div style="display: flex; justify-content: space-between; align-items: start;">
                                    <span class="badge-status">{row['status']}</span>
                                    <span style="font-weight: 800; color: #ff9800;">💰 {row['reward_points']} P</span>
                                </div>
                                <h3 style="margin: 10px 0;">{row['category']}</h3>
                                <p style="opacity: 0.7; font-size: 0.9rem;">📍 {row['address'] or '위치 분석 중...'}</p>
                                <p style="font-size: 0.8rem; opacity: 0.5;">{row['created_at']} | 제보자: {row['reporter_name']}</p>
                            </div>
                        </div>
                    </div>
                    ''', unsafe_allow_html=True)
                    # Media Handling with Robust Error Protection
                    if row['image_blob'] and len(row['image_blob']) > 0:
                        try:
                            # Use io.BytesIO for blob safety
                            st.image(row['image_blob'], use_container_width=True, caption="[현장 분석 사진]")
                        except Exception as e:
                            st.warning("⚠️ 이미지 데이터를 복원할 수 없습니다. (데이터 손상)")
                    elif row['image_path'] and os.path.exists(os.path.join('static', row['image_path'])):
                        try:
                            st.image(os.path.join('static', row['image_path']), use_container_width=True)
                        except:
                            st.info("🖼️ 이미지를 로드할 수 없습니다.")
                    else:
                        st.info("🖼️ 실시간 분석 이미지가 서버에 존재하지 않습니다. (로컬 연동 필요)")

    with col_b:
        st.markdown("## 📊 시스템 현황")
        full_df = pd.read_sql_query("SELECT * FROM reports", conn)
        st.markdown(f'''<div class="glass-card kpi-card"><p class="kpi-lab">전체 제보</p><div class="kpi-val">{len(full_df)}</div></div>''', unsafe_allow_html=True)
        st.markdown(f'''<div class="glass-card kpi-card" style="border-color: #34d399;"><p class="kpi-lab">조치 완료</p><div class="kpi-val">{len(full_df[full_df['status'].isin(['Rewarded', 'Action Taken'])])}</div></div>''', unsafe_allow_html=True)
        st.markdown(f'''<div class="glass-card kpi-card" style="border-color: #fbbf24;"><p class="kpi-lab">누적 포상금</p><div class="kpi-val">{full_df['reward_points'].sum():,}</div></div>''', unsafe_allow_html=True)

# --- MAP PAGE ---
elif menu == "📍 안전 지도 (Map)":
    st.markdown("<h1 style='margin-top: 50px;'>🛰️ 실시간 안전 관제 지도</h1>", unsafe_allow_html=True)
    df = pd.read_sql_query("SELECT * FROM reports WHERE latitude IS NOT NULL", conn)
    
    m = folium.Map(location=[37.5665, 126.9780], zoom_start=12, tiles="CartoDB dark_matter")
    for _, row in df.iterrows():
        color = 'red' if '시급' in str(row['urgency']) or 'HIGH' in str(row['urgency']) else 'blue'
        folium.CircleMarker(
            [row['latitude'], row['longitude']],
            radius=8, color=color, fill=True, popup=f"{row['category']}: {row['address']}"
        ).add_to(m)
    st_folium(m, width="100%", height=600)

# --- REPORT PAGE ---
elif menu == "🚀 제보하기 (Report)":
    st.markdown("<h1 style='margin-top: 50px;'>📸 새로운 안전 제보</h1>", unsafe_allow_html=True)
    with st.form("report_form"):
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        name = st.text_input("👤 성함", placeholder="홍길동")
        cat = st.selectbox("📂 제보 분류", ["도로 파손", "시설물 고장", "쓰레기 투기", "기타"])
        desc = st.text_area("🗒️ 상세 내용", placeholder="현장 상황을 상세히 적어주세요.")
        photo = st.file_uploader("🖼️ 현장 사진", type=['jpg', 'jpeg', 'png'])
        addr = st.text_input("📍 주소", "서울특별시 종로구 세종대로 209 (자동 인식)")
        st.markdown('</div>', unsafe_allow_html=True)
        
        btn = st.form_submit_button("🛡️ 제보 제출하기")
        if btn:
            if name and photo:
                img_data = photo.read()
                ai = sim_analysis(cat)
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                c = conn.cursor()
                c.execute("INSERT INTO reports (reporter_name, category, description, image_path, latitude, longitude, address, status, reward_points, created_at, updated_at, public_value, urgency, image_blob) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                          (name, cat, desc, "upload.jpg", 37.5665, 126.9780, addr, "Received", ai['val']*10, now, now, ai['val'], ai['urb'], img_data))
                conn.commit()
                st.success("데이터가 안전하게 전송되었습니다!")
                st.balloons()

# --- ADMIN PAGE ---
elif menu == "⚙️ 관리자 (Admin)":
    st.markdown("<h1 style='margin-top: 50px;'>⚙️ 행정 총괄 관리 시스템</h1>", unsafe_allow_html=True)
    pwd = st.text_input("Admin Password", type="password")
    if pwd == "0303":
        df = pd.read_sql_query("SELECT * FROM reports", conn)
        st.markdown("### 📊 전체 제보 데이터베이스")
        st.dataframe(df.drop(columns=['image_blob']), use_container_width=True)
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 통합 리스트 CSV 다운로드", csv, "nsk_admin_export.csv", "text/csv")
    elif pwd:
        st.error("잘못된 비밀번호입니다.")

st.markdown("---")
st.markdown("<p style='text-align: center; opacity: 0.4;'>© 2026 K-National Safety Keeper | Advanced AI Monitoring</p>", unsafe_allow_html=True)
