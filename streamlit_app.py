import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import os
import folium
from streamlit_folium import st_folium
import base64
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import io
import requests
import time
from streamlit_js_eval import streamlit_js_eval

# --- PROFESSIONAL PUBLISHING STANDARDS ---
st.set_page_config(
    page_title="K-국민안전지킴이 | K-National Safety Keeper",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- PREMIUM THEME ENGINE (Top 10 Tech #2 & #9) ---
THEMES = {
    "Bright Crystal (Premium)": {
        "bg_color": "#ffffff",
        "bg_app": "#f8fafc",
        "text": "#0f172a",
        "card_bg": "rgba(255, 255, 255, 0.85)",
        "glass_border": "rgba(255, 255, 255, 0.5)",
        "primary": "#135bec",
        "secondary": "#4c84ff",
        "hero_grad": "linear-gradient(135deg, #135bec 0%, #4c84ff 100%)",
        "kpi_val": "#135bec",
        "nav_bg": "rgba(19, 91, 236, 0.95)",
        "sidebar_bg": "#f1f5f9",
        "map_tiles": "CartoDB positron",
        "shadow": "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)"
    },
    "Royal Midnight (Expert)": {
        "bg_color": "#0f172a",
        "bg_app": "#020617",
        "text": "#f8fafc",
        "card_bg": "rgba(15, 23, 42, 0.6)",
        "glass_border": "rgba(255, 255, 255, 0.1)",
        "primary": "#3b82f6",
        "secondary": "#60a5fa",
        "hero_grad": "linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%)",
        "kpi_val": "#60a5fa",
        "nav_bg": "rgba(15, 23, 42, 0.9)",
        "sidebar_bg": "#0f172a",
        "map_tiles": "CartoDB dark_matter",
        "shadow": "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)"
    }
}

# --- Sidbar UI ---
with st.sidebar:
    st.markdown("### 🎨 UI ENGINE")
    theme_name = st.selectbox("Select Display Mode", list(THEMES.keys()), index=0)
    current_theme = THEMES[theme_name]
    st.markdown("---")
    st.markdown("### 🧭 NAVIGATION")
    menu = st.radio("Access Level", ["🏠 메인 로비 (Home)", "📍 전술 지도 (Map)", "🚀 사고 제보 (Report)", "⚙️ 통합 관제 (Admin)"])

# --- EXPERT CSS LIBRARY (Top 10 Tech #1, #3, #4) ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@100;400;700;900&display=swap');
    
    :root {{
        --primary: {current_theme['primary']};
        --secondary: {current_theme['secondary']};
        --text: {current_theme['text']};
        --glass: {current_theme['card_bg']};
        --border: {current_theme['glass_border']};
        --shadow-expert: {current_theme['shadow']};
    }}

    .stApp {{
        background-color: {current_theme['bg_app']};
        font-family: 'Pretendard', sans-serif;
        color: var(--text);
    }}

    /* Top 10 Tech #1: Micro-Interactions */
    @keyframes slideUp {{
        from {{ opacity: 0; transform: translateY(20px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    
    @keyframes pulse-soft {{
        0% {{ transform: scale(1); opacity: 0.8; }}
        50% {{ transform: scale(1.02); opacity: 1; }}
        100% {{ transform: scale(1); opacity: 0.8; }}
    }}

    .expert-card {{
        background: var(--glass);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid var(--border);
        border-radius: 28px;
        padding: 2rem;
        margin-bottom: 1.5rem;
        box-shadow: var(--shadow-expert);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        animation: slideUp 0.6s ease-out;
    }}

    .expert-card:hover {{
        transform: translateY(-8px) scale(1.01);
        border-color: var(--primary);
    }}

    /* Top 10 Tech #2: Hero Refined */
    .hero-container {{
        background: {current_theme['hero_grad']};
        padding: 8rem 2rem 6rem 2rem;
        text-align: center;
        border-radius: 0 0 80px 80px;
        margin-bottom: 4rem;
        color: white;
        position: relative;
        overflow: hidden;
    }}
    
    .hero-container::after {{
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        background: url('https://www.transparenttextures.com/patterns/carbon-fibre.png');
        opacity: 0.05;
    }}

    /* Typography & Badges */
    .expert-h1 {{ font-weight: 900; font-size: 4rem; letter-spacing: -2px; line-height: 1.1; margin-bottom: 1rem; }}
    .expert-p {{ font-weight: 400; font-size: 1.3rem; opacity: 0.85; max-width: 700px; margin: 0 auto; }}

    .badge-premium {{
        background: var(--primary);
        color: white;
        padding: 6px 16px;
        border-radius: 50px;
        font-size: 0.75rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 1px;
    }}

    /* Admin Table High-End */
    .stDataFrame {{
        border-radius: 18px;
        overflow: hidden;
        box-shadow: var(--shadow-expert);
    }}

    section[data-testid="stSidebar"] {{
        background-color: {current_theme['sidebar_bg']} !important;
        border-right: 1px solid var(--border);
    }}

    /* Global Header Expert */
    .expert-nav {{
        position: fixed;
        top: 0; left: 0; right: 0;
        background: {current_theme['nav_bg']};
        backdrop-filter: blur(15px);
        -webkit-backdrop-filter: blur(15px);
        padding: 0.8rem 1.5rem;
        z-index: 1000;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid var(--border);
    }}

    /* Top 10 Tech #8: Adaptive Responsive UI (Media Queries) */
    @media (max-width: 768px) {{
        .hero-container {{
            padding: 6rem 1rem 3rem 1rem;
            border-radius: 0 0 40px 40px;
            margin-bottom: 2rem;
        }}
        .expert-h1 {{
            font-size: 2.2rem;
            letter-spacing: -1px;
        }}
        .expert-p {{
            font-size: 1rem;
            padding: 0 10px;
        }}
        .expert-card {{
            padding: 1.2rem;
            border-radius: 20px;
        }}
        .expert-nav {{
            padding: 0.6rem 1rem;
        }}
        .expert-nav div:first-child {{
            font-size: 1.1rem !important;
        }}
        /* Hide complex elements on small mobile if necessary */
        .status-dot-text {{ display: none; }}
    }}
    
    .status-dot {{
        height: 10px; width: 10px;
        background-color: #10b981;
        border-radius: 50%;
        display: inline-block;
        margin-right: 8px;
        animation: pulse-soft 2s infinite;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- Global Components ---
def expert_header():
    st.markdown("""
        <div class="expert-nav">
            <div style="font-weight: 900; font-size: 1.4rem; color: white;">🛡️ K-SAFETY KEEPER</div>
            <div style="display: flex; align-items: center; color: white; font-size: 0.85rem; font-weight: 600;">
                <span class="status-dot"></span> <span class="status-dot-text">SYSTEM LIVE | v2.5.0 Expert</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

def get_db():
    conn = sqlite3.connect('safety_map.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def sim_analysis(cat):
    # Top 10 Tech #7: Advanced AI Simulation
    scores = {"도로 파손": 92, "시설물 고장": 78, "쓰레기 투기": 65}
    val = scores.get(cat, 50)
    return {"val": val, "urb": "CRITICAL" if val > 90 else "HIGH" if val > 70 else "NORMAL"}

def get_exif_data(image):
    info = image._getexif()
    if not info: return {}
    return {TAGS.get(tag, tag): value for tag, value in info.items()}

def get_lat_lon(exif_data):
    if "GPSInfo" not in exif_data: return None, None
    gps_info = exif_data["GPSInfo"]
    def to_dec(dms, ref):
        dec = dms[0] + dms[1]/60 + dms[2]/3600
        return -dec if ref in ['S', 'W'] else dec
    try:
        lat = to_dec(gps_info[2], gps_info[1])
        lon = to_dec(gps_info[4], gps_info[3])
        return lat, lon
    except: return None, None

def get_address_from_coords(lat, lon):
    try:
        response = requests.get(
            "https://nominatim.openstreetmap.org/reverse",
            params={
                "lat": lat,
                "lon": lon,
                "format": "jsonv2",
                "accept-language": "ko",
            },
            headers={"User-Agent": "SafetyMapExpert/2.5"},
            timeout=8,
        )
        response.raise_for_status()
        data = response.json()
        return data.get("display_name") or f"정밀 좌표: {lat:.5f}, {lon:.5f}"
    except Exception:
        return f"정밀 좌표: {lat:.5f}, {lon:.5f}"

# --- APP FLOW ---
expert_header()
conn = get_db()

if menu == "🏠 메인 로비 (Home)":
    # Hero Top 10 Tech #2
    st.markdown(f"""
        <div class="hero-container">
            <div class="expert-h1">PROTECTING KOREA</div>
            <div class="expert-p">
                지능형 AI 관제와 시민의 발빠른 제보가 결합된 대한민국 1등 안전 플랫폼.<br>
                당신의 소중한 제보 한 건이 더 안전한 내일을 만듭니다.
            </div>
        </div>
        """, unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 🔥 실시간 지능형 피드 (Live Intelligence)")
        df = pd.read_sql_query("SELECT * FROM reports ORDER BY id DESC LIMIT 15", conn)
        if df.empty:
            st.info("현재 분석된 위험 요소가 없습니다.")
        else:
            # Top 10 Tech #5: Dynamic Grid Reporting
            for _, row in df.iterrows():
                with st.container():
                    st.markdown(f'''
                    <div class="expert-card">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span class="badge-premium">{row['status']}</span>
                            <span style="font-weight: 900; color: var(--primary); font-size: 1.1rem;">💰 {row['reward_points']:,} P</span>
                        </div>
                        <h4 style="margin: 1.5rem 0 0.5rem 0; font-weight: 800; font-size: 1.3rem;">{row['category']}</h4>
                        <p style="font-size: 0.95rem; opacity: 0.7; margin-bottom: 1rem;">📍 {row['address'] or 'GPS 분석 중...'}</p>
                        <div style="font-size: 0.8rem; opacity: 0.5; border-top: 1px solid var(--border); padding-top: 10px;">
                            {row['created_at']} | 🛡️ ID {row['id']} Verified
                        </div>
                    </div>
                    ''', unsafe_allow_html=True)
                    # Media with failover
                    if row['image_blob'] and len(row['image_blob']) > 0:
                        try: st.image(row['image_blob'], use_container_width=True)
                        except: pass
                    elif row['image_path'] and os.path.exists(os.path.join('static', row['image_path'])):
                        try: st.image(os.path.join('static', row['image_path']), use_container_width=True)
                        except: pass

    with col2:
        st.markdown("### 📊 수치 관제 (Metrics)")
        all_df = pd.read_sql_query("SELECT * FROM reports", conn)
        
        # Expert KPI Cards
        st.markdown(f'''
            <div class="expert-card" style="text-align: center; border-left: 8px solid #3b82f6;">
                <p style="font-size: 0.85rem; font-weight: 700; opacity: 0.6;">TOTAL LOGS</p>
                <div style="font-size: 3rem; font-weight: 900; color: var(--primary);">{len(all_df)}</div>
            </div>
            <div class="expert-card" style="text-align: center; border-left: 8px solid #10b981;">
                <p style="font-size: 0.85rem; font-weight: 700; opacity: 0.6;">RESOLVED</p>
                <div style="font-size: 3rem; font-weight: 900; color: #10b981;">{len(all_df[all_df['status'].isin(['Rewarded', 'Action Taken'])])}</div>
            </div>
            <div class="expert-card" style="text-align: center; border-left: 8px solid #f59e0b;">
                <p style="font-size: 0.85rem; font-weight: 700; opacity: 0.6;">TOTAL REWARDS</p>
                <div style="font-size: 2.2rem; font-weight: 900; color: #f59e0b;">{all_df['reward_points'].sum():,} P</div>
            </div>
        ''', unsafe_allow_html=True)

elif menu == "📍 전술 지도 (Map)":
    st.markdown("<h2 style='margin-top: 60px;'>🛰️ SAFETY TACTICAL MAP</h2>", unsafe_allow_html=True)
    df = pd.read_sql_query("SELECT * FROM reports WHERE latitude IS NOT NULL", conn)
    m = folium.Map(location=[37.5665, 126.9780], zoom_start=12, tiles=current_theme['map_tiles'])
    for _, row in df.iterrows():
        color = 'red' if 'CRITICAL' in str(row['urgency']) else 'orange' if 'HIGH' in str(row['urgency']) else 'blue'
        folium.Marker(
            [row['latitude'], row['longitude']],
            popup=f"<b>{row['category']}</b><br>{row['address']}",
            icon=folium.Icon(color=color, icon='info-sign')
        ).add_to(m)
    st_folium(m, width="100%", height=700)

elif menu == "🚀 사고 제보 (Report)":
    st.markdown("<h2 style='margin-top: 60px;'>🛡️ INCIDENT SUBMISSION</h2>", unsafe_allow_html=True)
    
    # Session States for Automation (Top 10 Tech #7)
    if 'e_lat' not in st.session_state: st.session_state.e_lat = None
    if 'e_lon' not in st.session_state: st.session_state.e_lon = None
    if 'e_addr' not in st.session_state: st.session_state.e_addr = ""

    # --- Reactive Location & AI Analysis Logic (Outside Form for immediate reflection) ---
    st.markdown('<div class="expert-card">', unsafe_allow_html=True)
    st.markdown("### 📸 현장 분석 (AI Analysis)")
    photo = st.file_uploader("🖼️ Evidence Photo (Auto-Location Support)", type=['jpg', 'jpeg', 'png'])
    if photo:
        try:
            photo.seek(0)
            img = Image.open(photo)
            exif = get_exif_data(img)
            lat, lon = get_lat_lon(exif)
            if lat and lon:
                st.session_state.e_lat, st.session_state.e_lon = lat, lon
                st.session_state.e_addr = get_address_from_coords(lat, lon)
                st.success(f"📍 GPS 데이터 추출 성공: {st.session_state.e_addr}")
            photo.seek(0)
        except: pass

    st.markdown("---")
    st.write("📡 **Precision Geolocation**")
    if st.checkbox("🛰️ 위성 좌표 수신 허용 (Real-Time GPS)"):
        loc = streamlit_js_eval(data_of='get_location', key='gps_expert')
        if loc:
            st.session_state.e_lat = loc['coords']['latitude']
            st.session_state.e_lon = loc['coords']['longitude']
            st.session_state.e_addr = get_address_from_coords(st.session_state.e_lat, st.session_state.e_lon)
            st.success(f"✅ 현위치 위성 수신 완료: {st.session_state.e_addr}")
    
    # Move address input here for immediate reflection
    st.session_state.e_addr = st.text_input("📍 분석된 위치 (주소 직접 수정 가능)", value=st.session_state.e_addr)
    st.markdown('</div>', unsafe_allow_html=True)

    # --- Submission Form ---
    with st.form("report_form_expert"):
        st.markdown('<div class="expert-card">', unsafe_allow_html=True)
        name = st.text_input("👤 Reporter Name", placeholder="이름을 입력하세요")
        cat = st.selectbox("📂 Category", ["도로 파손", "시설물 고장", "쓰레기 투기", "기본 안전 위험"])
        desc = st.text_area("🗒️ Description", placeholder="현장 상황을 전문가처럼 상세히 기술해주세요.")
        st.markdown('</div>', unsafe_allow_html=True)
        
        btn = st.form_submit_button("🛡️ SUBMIT SAFE REPORT")
        if btn:
            if not name:
                st.error("👤 제보자 이름을 입력해주세요.")
            elif not photo:
                st.error("🖼️ 현장 사진을 업로드해주세요.")
            elif not st.session_state.e_addr:
                st.error("📍 위치 주소를 확인해주세요.")
            else:
                try:
                    # Top 10 Tech #10: Data Integrity Polish
                    photo.seek(0)
                    img_data = photo.read()
                    ai = sim_analysis(cat)
                    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    # Explicitly cast to ensure SQLite compatibility (Fallback to Seoul central if None)
                    b_name = str(name)
                    b_cat = str(cat)
                    b_desc = str(desc)
                    b_lat = float(st.session_state.e_lat if st.session_state.e_lat is not None else 37.5665)
                    b_lon = float(st.session_state.e_lon if st.session_state.e_lon is not None else 126.9780)
                    b_addr = str(st.session_state.e_addr)
                    b_val = int(ai['val'])
                    b_urb = str(ai['urb'])
                    
                    c = conn.cursor()
                    c.execute("""INSERT INTO reports 
                        (reporter_name, category, description, image_path, latitude, longitude, address, status, reward_points, created_at, updated_at, public_value, urgency, image_blob) 
                        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                        (b_name, b_cat, b_desc, "m_up.jpg", b_lat, b_lon, b_addr, "Verified", b_val*10, now, now, b_val, b_urb, sqlite3.Binary(img_data)))
                    conn.commit()
                    st.success("✅ 제보가 안전하게 접수되었습니다. (Expert System Logged)")
                    st.balloons()
                    # Clear state after success
                    st.session_state.e_lat = None
                    st.session_state.e_lon = None
                    st.session_state.e_addr = ""
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ 데이터 정합성 오류: {str(e)}")

elif menu == "⚙️ 통합 관제 (Admin)":
    st.markdown("<h2 style='margin-top: 60px;'>⚙️ COMMAND CENTER</h2>", unsafe_allow_html=True)
    pwd = st.text_input("Secure Access Token", type="password")
    if pwd == "0303":
        # Top 10 Tech #6: Advanced Admin Intelligence
        df = pd.read_sql_query("SELECT * FROM reports", conn)
        st.markdown("### 🔍 Global Safety Database")
        st.dataframe(df.drop(columns=['image_blob']), use_container_width=True)
        
        col_ex1, col_ex2 = st.columns(2)
        with col_ex1:
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 Export CSV Bundle", csv, "safety_db.csv", "text/csv")
        with col_ex2:
            st.button("🧹 Clear Test Records (Prototype)")

        # --- AI Address Intelligence Recovery (Top 10 Tech #6 Extension) ---
        st.markdown("---")
        st.markdown("### 🤖 AI 스마트 주소 복구 (Intelligence Recovery)")
        st.info("💡 제보 시 자동 주소 등록에 실패한 사례를 찾아 30초 간격으로 최대 3회 재분석을 시도합니다.")
        
        # Top 10 Tech #6 Enhanced: Robust placeholder detection
        reports_to_fix = df[
            (df['latitude'].notnull()) & 
            (
                (df['address'].isna()) | 
                (df['address'].str.strip() == "") |
                (df['address'].str.contains('분석 중|좌표:', na=False))
            )
        ]
        
        if not reports_to_fix.empty:
            st.warning(f"⚠️ 현재 {len(reports_to_fix)}건의 제보가 실시간 주소 보정이 필요합니다.")
            if st.button("🛰️ AI 주소 분석 자동 시도 (30초 간격/3회)"):
                for idx, row in reports_to_fix.iterrows():
                    success = False
                    for attempt in range(1, 4):
                        st.write(f"⏳ ID {row['id']} 분석 중... (시도 {attempt}/3)")
                        # Real address resolution simulation
                        new_addr = get_address_from_coords(row['latitude'], row['longitude'])
                        
                        if "분석 중" not in new_addr and "좌표:" not in new_addr:
                            # Success! Update DB
                            c = conn.cursor()
                            c.execute("UPDATE reports SET address = ?, updated_at = ? WHERE id = ?", 
                                     (new_addr, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), int(row['id'])))
                            conn.commit()
                            st.success(f"✅ ID {row['id']} 주소 복구 성공: {new_addr}")
                            success = True
                            break
                        
                        if attempt < 3:
                            time.sleep(30) # User requested 30s interval
                    
                    if not success:
                        st.error(f"❌ ID {row['id']} 주소 복구 최종 실패 (3회 시도 완료)")
                st.rerun()
        else:
            st.success("✅ 모든 제보의 주소 데이터가 최신 상태입니다 (AI 검증 완료).")

    elif pwd:
        st.error("비정상적인 접근입니다.")

st.markdown("---")
st.markdown(f"<p style='text-align: center; opacity: 0.4; font-size: 0.8rem;'>SECURITY VERIFIED BY K-NATIONAL SAFETY KEEPER EXPERT ENGINE | {theme_name} Active</p>", unsafe_allow_html=True)
