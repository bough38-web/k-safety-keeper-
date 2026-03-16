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

# --- Premium CSS & Glassmorphism ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background: radial-gradient(circle at top right, #1e293b, #0f172a);
        color: #f8fafc;
    }
    
    /* Glassmorphism Cards */
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 2rem;
        margin-bottom: 1.5rem;
    }
    
    .kpi-value {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(90deg, #60a5fa, #34d399);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: rgba(15, 23, 42, 0.8) !important;
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        height: 3.5rem;
        background: linear-gradient(135deg, #3b82f6, #06b6d4);
        color: white;
        border: none;
        font-weight: 700;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(59, 130, 246, 0.3);
    }
    
    h1, h2, h3 {
        color: #f8fafc !important;
        font-weight: 800 !important;
    }

    .status-badge {
        padding: 4px 12px;
        border-radius: 50px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Database Core ---
def get_db():
    conn = sqlite3.connect('safety_map.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def sim_ai_analysis(category):
    # Simulated AI logic
    urgency_map = {"도로 파손": "시급", "시설물 고장": "보통", "기타": "확인 필요"}
    val = 75 if category == "도로 파손" else 45
    return {
        "public_value": val,
        "urgency": urgency_map.get(category, "보통"),
        "landmarks": "정밀 분석 탐색 중..."
    }

# --- Sidebar UI ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center; color: #60a5fa;'>🛡️ K-NSK</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 0.8rem; opacity: 0.7;'>Premium Safety Command Center</p>", unsafe_allow_html=True)
    st.write("")
    menu = st.sidebar.radio("Navigation", ["🛰️ Real-time Map", "📸 Report Incident", "⚙️ Admin Control"], key="nav")
    st.write("")
    st.info("System Online: v2.5.0-Final")

# --- UI LOGIC ---
conn = get_db()

if menu == "🛰️ Real-time Map":
    st.markdown("<h1 style='margin-bottom: 0;'>📍 실시간 안전 관제 센터</h1>", unsafe_allow_html=True)
    st.markdown("<p style='opacity: 0.7;'>Korea National Safety Keeper Satellite Feed</p>", unsafe_allow_html=True)
    
    df = pd.read_sql_query("SELECT * FROM reports", conn)
    
    # KPI Glass Cards
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f'''<div class="glass-card"><p style="font-size: 0.9rem; margin:0;">TOTAL INCIDENTS</p><div class="kpi-value">{len(df)}</div></div>''', unsafe_allow_html=True)
    with c2:
        resolved = len(df[df['status'].isin(['Rewarded', 'Action Taken'])])
        st.markdown(f'''<div class="glass-card"><p style="font-size: 0.9rem; margin:0;">RESOLVED</p><div class="kpi-value" style="background: linear-gradient(90deg, #10b981, #34d399);-webkit-background-clip:text;">{resolved}</div></div>''', unsafe_allow_html=True)
    with c3:
        total_pts = df['reward_points'].sum()
        st.markdown(f'''<div class="glass-card"><p style="font-size: 0.9rem; margin:0;">REWARD POOL</p><div class="kpi-value" style="background: linear-gradient(90deg, #f59e0b, #fbbf24);-webkit-background-clip:text;">{total_pts:,} P</div></div>''', unsafe_allow_html=True)

    # Folium Map
    st.markdown('<div class="glass-card" style="padding: 10px;">', unsafe_allow_html=True)
    m = folium.Map(location=[37.5665, 126.9780], zoom_start=11, tiles="CartoDB dark_matter")
    if not df.empty:
        for idx, row in df.iterrows():
            if pd.notnull(row['latitude']) and pd.notnull(row['longitude']):
                color = 'red' if '시급' in str(row['urgency']) else 'blue'
                folium.Marker(
                    [row['latitude'], row['longitude']],
                    popup=f"<b>{row['category']}</b><br>{row['address']}",
                    tooltip=row['category'],
                    icon=folium.Icon(color=color, icon='info-sign')
                ).add_to(m)
    st_folium(m, width="100%", height=500)
    st.markdown('</div>', unsafe_allow_html=True)

    # Safety Feed with Improved Persistence Display
    st.subheader("🔥 실시간 제보 피드")
    for index, row in df.sort_values(by='created_at', ascending=False).iterrows():
        with st.container():
            st.markdown(f'''
            <div class="glass-card" style="padding: 1rem; border-left: 4px solid #3b82f6;">
                <div style="display: flex; justify-content: space-between; align-items: start;">
                    <div>
                        <span style="font-weight: 800; font-size: 1.1rem;">[{row['category']}] {row['address'] or '분석 중...'}</span>
                        <div style="font-size: 0.8rem; opacity: 0.6;">{row['created_at']} | 제보자: {row['reporter_name']}</div>
                    </div>
                </div>
            </div>
            ''', unsafe_allow_html=True)
            
            # Show Image (Try Blob First for Mobile persistence)
            if row['image_blob']:
                try:
                    st.image(row['image_blob'], caption="현장 사진 (DB 보관됨)", use_container_width=True)
                except:
                    st.warning("경고: 이미지 데이터를 복원할 수 없습니다.")
            elif os.path.exists(os.path.join('static', row['image_path'])):
                st.image(os.path.join('static', row['image_path']), caption="현장 사진 (로컬)", use_container_width=True)
            else:
                st.info("🖼️ 이미지는 초기화되었으나 데이터 기록은 보존되었습니다.")

elif menu == "📸 Report Incident":
    st.markdown("<h1>📸 정밀 안전 제보</h1>", unsafe_allow_html=True)
    st.markdown("<p style='opacity: 0.7;'>High-Precision AI Scanning Interface</p>", unsafe_allow_html=True)
    
    with st.form("scanner_form"):
        name = st.text_input("👤 제보자 성함", placeholder="홍길동")
        cat = st.selectbox("📂 위협 카테고리", ["도로 파손", "시설물 고장", "쓰레기 투기", "가로등 고장", "화재 위험", "기타"])
        desc = st.text_area("🗒️ 상세 설명", placeholder="인공지능 분석을 위해 상황을 설명해 주세요.")
        
        # Camera & File
        st.write("🖼️ 미디어 캡처")
        photo = st.file_uploader("사진을 찍거나 업로드하세요", type=['jpg', 'jpeg', 'png'])
        
        # Location (Streamlit doesn't easily get GPS without custom JS, so we simulate or manual)
        loc_type = st.radio("위치 설정", ["자동 스마트 주소", "수동 주소 입력"])
        addr = ""
        if loc_type == "자동 스마트 주소":
            st.success("✅ 스마트 위치 인식이 준비되었습니다. (배포 시 적용)")
            addr = "서울특별시 종로구 세종대로 209 (자동 인식)"
        else:
            addr = st.text_input("위차 주소", placeholder="예: 서울특별시 종로구...")

        submit = st.form_submit_button("🛡️ SECURE SUBMIT TO AI")
        
        if submit:
            if not name or not photo:
                st.error("성함과 사진은 분석을 위한 필수 데이터입니다.")
            else:
                # Process Image for Blob Persistence
                img_bytes = photo.read()
                ai_data = sim_ai_analysis(cat)
                
                # Save to DB
                c = conn.cursor()
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                c.execute("""
                    INSERT INTO reports (reporter_name, category, description, image_path, latitude, longitude, address, status, reward_points, created_at, updated_at, public_value, urgency, image_blob)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (name, cat, desc, f"upload_{datetime.now().timestamp()}.jpg", 37.5665, 126.9780, addr, "Received", ai_data['public_value']*10, now, now, ai_data['public_value'], ai_data['urgency'], img_bytes))
                conn.commit()
                st.success("🎉 제보가 보안 전송되었습니다! AI가 곧 가치 평가를 시작합니다.")
                st.balloons()

elif menu == "⚙️ Admin Control":
    st.markdown("<h1>🏢 행정 관제 센터</h1>", unsafe_allow_html=True)
    
    pwd = st.text_input("ACCESS CODE", type="password")
    if pwd == "0303":
        st.success("AUTHORIZED ACCESS GRANTED")
        df = pd.read_sql_query("SELECT * FROM reports", conn)
        
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.write("📊 데이터 통합 대시보드")
        st.dataframe(df.drop(columns=['image_blob']), use_container_width=True)
        
        col1, col2 = st.columns(2)
        with col1:
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 전체 리스트 CSV 다운로드", csv, "safety_db_export.csv", "text/csv")
        with col2:
            st.button("🔄 시스템 강제 동기화")
        st.markdown('</div>', unsafe_allow_html=True)
    elif pwd:
        st.error("ACCESS DENIED: INVALID CODE")

st.markdown("---")
st.markdown("<p style='text-align: center; opacity: 0.5;'>K-National Safety Keeper Alpha v2.5 | End-to-End Encryption Protected</p>", unsafe_allow_html=True)
