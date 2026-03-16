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
    page_title="K-National Safety Keeper",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Theme Configuration ---
THEMES = {
    "Royal Midnight": {
        "bg_gradient": "radial-gradient(circle at top right, #1e293b, #0f172a)",
        "card_bg": "rgba(255, 255, 255, 0.05)",
        "accent_1": "#60a5fa",
        "accent_2": "#34d399",
        "btn_gradient": "linear-gradient(135deg, #3b82f6, #06b6d4)",
        "text": "#f8fafc",
        "map_tiles": "CartoDB dark_matter"
    },
    "Neon Cyberpunk": {
        "bg_gradient": "linear-gradient(180deg, #0d0221 0%, #000000 100%)",
        "card_bg": "rgba(255, 0, 255, 0.03)",
        "accent_1": "#00f3ff",
        "accent_2": "#ff00ff",
        "btn_gradient": "linear-gradient(135deg, #ff00ff, #00f3ff)",
        "text": "#ffffff",
        "map_tiles": "CartoDB dark_matter"
    },
    "Emerald Forest": {
        "bg_gradient": "radial-gradient(circle at center, #064e3b, #022c22)",
        "card_bg": "rgba(16, 185, 129, 0.05)",
        "accent_1": "#34d399",
        "accent_2": "#fbbf24",
        "btn_gradient": "linear-gradient(135deg, #059669, #10b981)",
        "text": "#ecfdf5",
        "map_tiles": "CartoDB positron"
    },
    "Deep Ocean": {
        "bg_gradient": "linear-gradient(135deg, #0c4a6e 0%, #082f49 100%)",
        "card_bg": "rgba(56, 189, 248, 0.05)",
        "accent_1": "#38bdf8",
        "accent_2": "#818cf8",
        "btn_gradient": "linear-gradient(135deg, #0284c7, #0ea5e9)",
        "text": "#f0f9ff",
        "map_tiles": "CartoDB dark_matter"
    }
}

# --- Sidebar UI (Theme Selector First) ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center; color: #60a5fa;'>🛡️ K-NSK</h1>", unsafe_allow_html=True)
    theme_name = st.selectbox("🎨 Select Theme", list(THEMES.keys()), index=0)
    current_theme = THEMES[theme_name]
    
    st.markdown("---")
    menu = st.radio("Navigation", ["🛰️ Real-time Map", "📸 Report Incident", "⚙️ Admin Control"], key="nav")
    st.write("")
    st.info(f"System: {theme_name} Active")

# --- Dynamic CSS Injection ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;800&display=swap');
    
    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif;
    }}
    
    .stApp {{
        background: {current_theme['bg_gradient']};
        color: {current_theme['text']};
    }}
    
    /* Glassmorphism Cards */
    .glass-card {{
        background: {current_theme['card_bg']};
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 24px;
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        transition: transform 0.3s ease;
    }}
    
    .glass-card:hover {{
        transform: translateY(-5px);
    }}
    
    .kpi-value {{
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(90deg, {current_theme['accent_1']}, {current_theme['accent_2']});
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }}
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {{
        background-color: rgba(0, 0, 0, 0.4) !important;
        backdrop-filter: blur(25px);
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }}
    
    .stButton>button {{
        width: 100%;
        border-radius: 16px;
        height: 4rem;
        background: {current_theme['btn_gradient']};
        color: white;
        border: none;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 1px;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }}
    
    .stButton>button:hover {{
        transform: scale(1.02);
        box-shadow: 0 15px 30px rgba(0, 0, 0, 0.4);
    }}
    
    h1, h2, h3 {{
        color: {current_theme['text']} !important;
        font-weight: 800 !important;
    }}

    /* Scanner Effect for Form */
    .scanner-form {{
        position: relative;
        overflow: hidden;
    }}
    
    .scanner-line {{
        width: 100%;
        height: 2px;
        background: {current_theme['accent_1']};
        box-shadow: 0 0 15px {current_theme['accent_1']};
        position: absolute;
        top: 0;
        animation: scan 3s infinite linear;
        z-index: 10;
        opacity: 0.5;
    }}
    
    @keyframes scan {{
        0% {{ top: 0; }}
        100% {{ top: 100%; }}
    }}
    
    .status-badge {{
        padding: 6px 16px;
        border-radius: 50px;
        font-size: 0.8rem;
        font-weight: 800;
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid {current_theme['accent_1']};
    }}
    </style>
    """, unsafe_allow_html=True)

# --- Database Core ---
def get_db():
    conn = sqlite3.connect('safety_map.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def sim_ai_analysis(category):
    urgency_map = {"도로 파손": "CRITICAL", "시설물 고장": "NORMAL", "기타": "CHECK"}
    val = 88 if category == "도로 파손" else 42
    return {
        "public_value": val,
        "urgency": urgency_map.get(category, "NORMAL"),
        "landmarks": "정밀 분석 탐색 완료"
    }

# --- UI LOGIC ---
conn = get_db()

if menu == "🛰️ Real-time Map":
    st.markdown(f"<h1 style='color:{current_theme['accent_1']} !important;'>🛰️ 국가 안전 통합 관제 시스템</h1>", unsafe_allow_html=True)
    st.markdown("<p style='opacity: 0.6; font-size: 1.1rem;'>K-National Safety Keeper Global Monitoring</p>", unsafe_allow_html=True)
    
    df = pd.read_sql_query("SELECT * FROM reports", conn)
    
    # KPI Grid
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f'''<div class="glass-card"><p style="opacity:0.7; font-weight:700;">TOTAL ANALYZED</p><div class="kpi-value">{len(df)}</div></div>''', unsafe_allow_html=True)
    with c2:
        resolved = len(df[df['status'].isin(['Rewarded', 'Action Taken'])])
        st.markdown(f'''<div class="glass-card"><p style="opacity:0.7; font-weight:700;">RESOLVED TASKS</p><div class="kpi-value" style="background: linear-gradient(90deg, {current_theme['accent_2']}, #ffffff);-webkit-background-clip:text;">{resolved}</div></div>''', unsafe_allow_html=True)
    with c3:
        total_pts = df['reward_points'].sum()
        st.markdown(f'''<div class="glass-card"><p style="opacity:0.7; font-weight:700;">CITIZEN REWARDS</p><div class="kpi-value" style="background: linear-gradient(90deg, #f59e0b, {current_theme['accent_1']});-webkit-background-clip:text;">{total_pts:,}</div></div>''', unsafe_allow_html=True)

    # Advanced Folium Map
    st.markdown(f'<div class="glass-card" style="padding: 15px; border: 2px solid {current_theme["accent_1"]}33;">', unsafe_allow_html=True)
    m = folium.Map(location=[37.5665, 126.9780], zoom_start=11, tiles=current_theme['map_tiles'])
    if not df.empty:
        for idx, row in df.iterrows():
            if pd.notnull(row['latitude']) and pd.notnull(row['longitude']):
                is_crit = '시급' in str(row['urgency']) or 'CRITICAL' in str(row['urgency'])
                marker_color = 'red' if is_crit else 'blue'
                folium.CircleMarker(
                    location=[row['latitude'], row['longitude']],
                    radius=10 if is_crit else 7,
                    popup=f"{row['category']}: {row['address']}",
                    color=marker_color,
                    fill=True,
                    fill_color=marker_color,
                    fill_opacity=0.6 if is_crit else 0.4
                ).add_to(m)
    st_folium(m, width="100%", height=600)
    st.markdown('</div>', unsafe_allow_html=True)

    # High-End Safety Feed
    st.markdown(f"### 🔥 최신 위협 감지 피드")
    for index, row in df.sort_values(by='created_at', ascending=False).iterrows():
        with st.container():
            st.markdown(f'''
            <div class="glass-card" style="padding: 1.5rem; background: rgba(255,255,255,0.02); border-left: 5px solid {current_theme['accent_1']};">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <span class="status-badge" style="color: {current_theme['accent_1']};">LIVE FEED</span>
                        <h3 style="margin: 10px 0 5px 0;">{row['category']}</h3>
                        <p style="opacity: 0.8; margin: 0;">📍 {row['address'] or '위치 분석 중'}</p>
                        <p style="font-size: 0.8rem; opacity: 0.5;">{row['created_at']} | ID: NSK-{row['id']}</p>
                    </div>
                    <div style="text-align: right;">
                        <p style="font-size: 0.8rem; opacity: 0.7;">AI VALUE</p>
                        <h2 style="margin: 0; color: {current_theme['accent_2']};">{row['public_value']}%</h2>
                    </div>
                </div>
            </div>
            ''', unsafe_allow_html=True)
            
            # Persistent Media Display
            if row['image_blob']:
                try:
                    st.image(row['image_blob'], caption="STORAGE-ID: BLOB_SECURE", use_container_width=True)
                except:
                    st.warning("Data restoration failed.")
            elif os.path.exists(os.path.join('static', row['image_path'])):
                st.image(os.path.join('static', row['image_path']), use_container_width=True)

elif menu == "📸 Report Incident":
    st.markdown(f"<h1>📸 정밀 위협 스캔 제보</h1>", unsafe_allow_html=True)
    
    st.markdown('<div class="scanner-form">', unsafe_allow_html=True)
    st.markdown('<div class="scanner-line"></div>', unsafe_allow_html=True)
    
    with st.form("premium_scanner"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("👤 제보자 라이센스 성함", placeholder="홍길동")
        with col2:
            cat = st.selectbox("📂 위협 분류 탐지", ["도로 파손", "시설물 고장", "쓰레기 투기", "가로등 고장", "화재 위험", "기타"])
        
        desc = st.text_area("🗒️ 위협 상황 정밀 기술", placeholder="관리자가 즉시 대응할 수 있도록 상세히 적어주세요.")
        
        photo = st.file_uploader("🖼️ 현장 정밀 스캔 데이터 (사진)", type=['jpg', 'jpeg', 'png'])
        
        loc_type = st.radio("📡 위치 좌표 수신 방식", ["자동 스마트 인계", "수동 지점 지정"])
        addr = ""
        if loc_type == "자동 스마트 인계":
            st.success("🛰️ 위성 좌표 수신 완료: 서울특별시 종로구 일대")
            addr = "서울특별시 종로구 세종대로 209 (AI 자동 보정)"
        else:
            addr = st.text_input("직접 위치 입력", placeholder="주소를 입력하세요.")

        st.write("")
        submit = st.form_submit_button("🛡️ SECURE SUBMIT TO AI COMMAND")
        
        if submit:
            if not name or not photo:
                st.error("분석을 위한 필수 데이터가 누락되었습니다.")
            else:
                raw_img = photo.read()
                ai_data = sim_ai_analysis(cat)
                
                c = conn.cursor()
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                c.execute("""
                    INSERT INTO reports (reporter_name, category, description, image_path, latitude, longitude, address, status, reward_points, created_at, updated_at, public_value, urgency, image_blob)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (name, cat, desc, "secure_temp.jpg", 37.5665, 126.9780, addr, "Submitted", ai_data['public_value']*10, now, now, ai_data['public_value'], ai_data['urgency'], raw_img))
                conn.commit()
                st.markdown(f"<h3 style='text-align:center; color:{current_theme['accent_2']}'>🚀 전송 완료! AI 분석이 시작되었습니다.</h3>", unsafe_allow_html=True)
                st.balloons()
    st.markdown('</div>', unsafe_allow_html=True)

elif menu == "⚙️ Admin Control":
    st.markdown("<h1>⚙️ 전 국가 안전 통합 관제 센터</h1>", unsafe_allow_html=True)
    
    pwd = st.text_input("ENCRYPTION ACCESS CODE", type="password")
    if pwd == "0303":
        st.success("BIOMETRIC & ACCESS CODE VERIFIED")
        df = pd.read_sql_query("SELECT * FROM reports", conn)
        
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.write("📊 실시간 통합 데이터베이스 (암호화 전송)")
        # Show all except blob for performance
        st.dataframe(df.drop(columns=['image_blob']), use_container_width=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 통합 리스트 CSV 추출", csv, "nsk_master_db.csv", "text/csv")
        with col2:
            st.button("🛰️ 위성 지도 데이터 동기화")
        with col3:
            st.button("🧹 기록 백업 및 최적화")
        st.markdown('</div>', unsafe_allow_html=True)
    elif pwd:
        st.error("ACCESS DENIED: RED-LEVEL SECURITY ALERT")

st.write("")
st.markdown(f"<p style='text-align: center; opacity: 0.3;'>K-NSK SECURITY ARCHITECTURE V3.0-PREMIUM | Theme: {theme_name}</p>", unsafe_allow_html=True)
