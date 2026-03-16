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
    initial_sidebar_state="expanded"
)

# --- Theme Configuration ---
THEMES = {
    "Bright Crystal (White)": {
        "bg_color": "#ffffff",
        "bg_app": "#f8fafc",
        "text": "#1e293b",
        "card_bg": "rgba(255, 255, 255, 0.9)",
        "glass_border": "rgba(0, 0, 0, 0.05)",
        "primary": "#135bec",
        "hero_grad": "linear-gradient(135deg, #135bec 0%, #4c84ff 100%)",
        "kpi_val": "#135bec",
        "nav_bg": "rgba(19, 91, 236, 0.95)",
        "sidebar_bg": "#f1f5f9",
        "map_tiles": "CartoDB positron"
    },
    "Solar Morning (Warm)": {
        "bg_color": "#fefce8",
        "bg_app": "#fefce8",
        "text": "#422006",
        "card_bg": "rgba(255, 255, 255, 0.95)",
        "glass_border": "rgba(0, 0, 0, 0.05)",
        "primary": "#ca8a04",
        "hero_grad": "linear-gradient(135deg, #fbbf24 0%, #ca8a04 100%)",
        "kpi_val": "#ca8a04",
        "nav_bg": "rgba(202, 138, 4, 0.95)",
        "sidebar_bg": "#fef9c3",
        "map_tiles": "CartoDB positron"
    },
    "Royal Midnight (Dark)": {
        "bg_color": "#0f172a",
        "bg_app": "#0f172a",
        "text": "#f1f5f9",
        "card_bg": "rgba(30, 41, 59, 0.7)",
        "glass_border": "rgba(255, 255, 255, 0.1)",
        "primary": "#3b82f6",
        "hero_grad": "linear-gradient(135deg, #135bec 0%, #00d2ff 100%)",
        "kpi_val": "#ffffff",
        "nav_bg": "rgba(19, 91, 236, 0.9)",
        "sidebar_bg": "#0f172a",
        "map_tiles": "CartoDB dark_matter"
    }
}

# --- Sidebar UI (Theme Selector) ---
with st.sidebar:
    st.markdown("### 🎨 THEME SETTING")
    theme_name = st.selectbox("밝기/테마 선택", list(THEMES.keys()), index=0)
    current_theme = THEMES[theme_name]
    st.markdown("---")
    st.markdown("### 🧭 NAVIGATION")
    menu = st.radio("Menu", ["🏠 홈 (Home)", "📍 안전 지도 (Map)", "🚀 제보하기 (Report)", "⚙️ 관리자 (Admin)"])

# --- Dynamic CSS Injection ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    :root {{
        --primary: {current_theme['primary']};
        --text: {current_theme['text']};
        --radius-lg: 24px;
        --shadow-premium: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
    }}

    .stApp {{
        background-color: {current_theme['bg_app']};
        font-family: 'Inter', sans-serif;
        color: {current_theme['text']};
    }}

    /* Custom Header */
    .custom-header {{
        position: fixed;
        top: 0; left: 0; right: 0;
        background: {current_theme['nav_bg']};
        backdrop-filter: blur(12px);
        padding: 0.8rem 2rem;
        z-index: 999;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid {current_theme['glass_border']};
        color: white;
    }}

    /* Hero Section */
    .hero-box {{
        background: {current_theme['hero_grad']};
        padding: 6rem 2rem 4rem 2rem;
        text-align: center;
        border-radius: 0 0 50px 50px;
        margin-bottom: 3rem;
        box-shadow: var(--shadow-premium);
        color: white;
    }}

    /* Cards */
    .glass-card {{
        background: {current_theme['card_bg']};
        backdrop-filter: blur(10px);
        border: 1px solid {current_theme['glass_border']};
        border-radius: var(--radius-lg);
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        color: {current_theme['text']};
    }}

    .kpi-card {{
        text-align: center;
        border-bottom: 4px solid var(--primary);
    }}
    .kpi-val {{
        font-size: 2.8rem;
        font-weight: 900;
        color: {current_theme['kpi_val']};
        margin: 0;
    }}
    .kpi-lab {{
        font-size: 0.85rem;
        opacity: 0.7;
        font-weight: 600;
        color: {current_theme['text']};
    }}

    .badge-status {{
        padding: 4px 12px;
        border-radius: 50px;
        font-size: 0.75rem;
        font-weight: 800;
        background: rgba(19, 91, 236, 0.1);
        color: var(--primary);
        border: 1px solid var(--primary);
    }}

    section[data-testid="stSidebar"] {{
        background-color: {current_theme['sidebar_bg']} !important;
    }}
    
    /* Input Styling */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {{
        background-color: white !important;
        color: black !important;
    }}
    
    h1, h2, h3, h4 {{
        color: {current_theme['text']} !important;
    }}
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
        <div style="font-size: 0.8rem; font-weight: 600; opacity: 0.8;">Admin: 0303</div>
    </div>
    """, unsafe_allow_html=True)

# Shared DB Connection
conn = get_db()

# --- HOME PAGE ---
if menu == "🏠 홈 (Home)":
    # Hero Section
    st.markdown("""
        <div class="hero-box">
            <h1 style="font-size: 3.5rem; font-weight: 800; margin-bottom: 1rem; color: white !important;">K-국민안전지킴이</h1>
            <p style="font-size: 1.4rem; opacity: 0.9; max-width: 800px; margin: 0 auto; color: white !important;">
                수만 명의 시민과 함께 더 안전한 사회를 만듭니다.<br>사진 한 장이면 AI가 즉시 분석하여 대응합니다.
            </p>
        </div>
        """, unsafe_allow_html=True)

    # Dashboard/Feed
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
                        <div style="display: flex; justify-content: space-between; align-items: start;">
                            <span class="badge-status">{row['status']}</span>
                            <span style="font-weight: 800; color: #ff9800;">💰 {row['reward_points']} P</span>
                        </div>
                        <h3 style="margin: 10px 0;">{row['category']}</h3>
                        <p style="opacity: 0.7; font-size: 0.9rem;">📍 {row['address'] or '위치 분석 중...'}</p>
                        <p style="font-size: 0.8rem; opacity: 0.5;">{row['created_at']} | 제보자: {row['reporter_name']}</p>
                    </div>
                    ''', unsafe_allow_html=True)
                    # Media Handling
                    if row['image_blob'] and len(row['image_blob']) > 0:
                        try:
                            st.image(row['image_blob'], use_container_width=True, caption="[현장 사진]")
                        except:
                            st.warning("이미지 로드 실패")
                    elif row['image_path'] and os.path.exists(os.path.join('static', row['image_path'])):
                        try:
                            st.image(os.path.join('static', row['image_path']), use_container_width=True)
                        except:
                            st.info("🖼️ 이미지를 로로드할 수 없습니다.")

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
    
    m = folium.Map(location=[37.5665, 126.9780], zoom_start=12, tiles=current_theme['map_tiles'])
    for _, row in df.iterrows():
        color = 'red' if '시급' in str(row['urgency']) or 'HIGH' in str(row['urgency']) else 'blue'
        folium.CircleMarker(
            [row['latitude'], row['longitude']],
            radius=8, color=color, fill=True, popup=f"{row['category']}: {row['address']}"
        ).add_to(m)
    st_folium(m, width="100%", height=600)

# --- REPORT PAGE ---
elif menu == "🚀 제보하기 (Report)":
    st.markdown("<h1 style='margin-top: 50px;'>🚀 새로운 안전 제보</h1>", unsafe_allow_html=True)
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
        st.download_button("📥 통합 리스트 CSV 추출", csv, "nsk_admin_export.csv", "text/csv")
    elif pwd:
        st.error("잘못된 비밀번호입니다.")

st.markdown("---")
st.markdown(f"<p style='text-align: center; opacity: 0.4;'>© 2026 K-National Safety Keeper | {theme_name} Theme Applied</p>", unsafe_allow_html=True)
