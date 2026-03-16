import os
import sqlite3
import uuid
from datetime import datetime
from fractions import Fraction
from typing import Optional, Tuple

from flask import Flask, flash, g, redirect, render_template, request, url_for
from PIL import Image, ExifTags
import requests
from werkzeug.utils import secure_filename

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "safety_map.db")
UPLOAD_DIR = os.path.join(BASE_DIR, "static", "uploads")
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}

app = Flask(__name__)
app.config["SECRET_KEY"] = "dev-secret-change-me"
app.config["UPLOAD_FOLDER"] = UPLOAD_DIR
app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024  # 20MB

os.makedirs(UPLOAD_DIR, exist_ok=True)


# -----------------------------
# Database helpers
# -----------------------------
def get_db() -> sqlite3.Connection:
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(error):  # noqa: ANN001
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db() -> None:
    db = sqlite3.connect(DB_PATH)
    cur = db.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reporter_name TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            image_path TEXT NOT NULL,
            latitude REAL,
            longitude REAL,
            address TEXT,
            status TEXT NOT NULL DEFAULT '접수',
            reward_points INTEGER NOT NULL DEFAULT 0,
            public_value INTEGER DEFAULT 0,
            admin_feedback TEXT,
            transferred_to TEXT,
            landmarks TEXT,
            urgency TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )
    # Migration: Add columns if they don't exist
    cols = [
        ("public_value", "INTEGER DEFAULT 0"),
        ("admin_feedback", "TEXT"),
        ("transferred_to", "TEXT"),
        ("landmarks", "TEXT"),
        ("urgency", "TEXT")
    ]
    for col_name, col_type in cols:
        try:
            cur.execute(f"ALTER TABLE reports ADD COLUMN {col_name} {col_type}")
        except sqlite3.OperationalError:
            pass # Column already exists
    
    db.commit()
    db.close()


# -----------------------------
# EXIF GPS helpers
# -----------------------------
def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def to_float(value) -> float:  # noqa: ANN001
    if isinstance(value, tuple) and len(value) == 2:
        return float(value[0]) / float(value[1])
    if isinstance(value, Fraction):
        return float(value)
    try:
        return float(value)
    except Exception:
        return float(Fraction(str(value)))


def dms_to_decimal(dms, ref: str) -> float:  # noqa: ANN001
    degrees = to_float(dms[0])
    minutes = to_float(dms[1])
    seconds = to_float(dms[2])
    decimal = degrees + (minutes / 60.0) + (seconds / 3600.0)
    if ref in ["S", "W"]:
        decimal *= -1
    return decimal


def extract_gps_from_image(image_path: str) -> Tuple[Optional[float], Optional[float]]:
    try:
        image = Image.open(image_path)
        exif_data = image.getexif()
        if not exif_data:
            return None, None

        gps_info = None
        for tag_id, value in exif_data.items():
            tag = ExifTags.TAGS.get(tag_id, tag_id)
            if tag == "GPSInfo":
                gps_info = value
                break

        if not gps_info:
            return None, None

        gps_parsed = {}
        for key, value in gps_info.items():
            decoded_key = ExifTags.GPSTAGS.get(key, key)
            gps_parsed[decoded_key] = value

        lat = gps_parsed.get("GPSLatitude")
        lat_ref = gps_parsed.get("GPSLatitudeRef")
        lon = gps_parsed.get("GPSLongitude")
        lon_ref = gps_parsed.get("GPSLongitudeRef")

        if lat and lat_ref and lon and lon_ref:
            latitude = dms_to_decimal(lat, lat_ref)
            longitude = dms_to_decimal(lon, lon_ref)
            return latitude, longitude
    except Exception:
        return None, None

    return None, None


# -----------------------------
# AI Analysis Simulation
# -----------------------------
def simulate_ai_analysis(image_path: str) -> dict:
    """
    Simulates AI analysis of the photo to extract category, evaluate public value,
    detect nearby landmarks, and determine urgency.
    """
    categories = ["도로 파손", "시설물 고장", "쓰레기 투기", "가로등 고장", "보행로 사각지대"]
    landmarks_list = [
        "성산타워 인근 15m 지점", "중앙공원 입구 맞은편", "서울시청 본관 서측 30m", 
        "남산도서관 정문 앞", "강남역 10번 출구 인근", "잠실 롯데타워 북단 50m"
    ]
    urgencies = ["보통", "시급", "매우 시급(위험)"]
    
    import time
    import random
    time.sleep(1.5)  # Simulate processing time
    
    return {
        "category": random.choice(categories),
        "public_value": random.randint(30, 95),
        "landmarks": random.choice(landmarks_list),
        "urgency": random.choice(urgencies)
    }


# -----------------------------
# Geocoding helper
# -----------------------------
def reverse_geocode(latitude: float, longitude: float) -> str:
    """Uses Nominatim; if unavailable, returns fallback text."""
    try:
        response = requests.get(
            "https://nominatim.openstreetmap.org/reverse",
            params={
                "lat": latitude,
                "lon": longitude,
                "format": "jsonv2",
                "accept-language": "ko",
            },
            headers={"User-Agent": "SafetyMapPrototype/1.0"},
            timeout=8,
        )
        response.raise_for_status()
        data = response.json()
        return data.get("display_name") or f"좌표: {latitude:.6f}, {longitude:.6f}"
    except Exception:
        return f"좌표: {latitude:.6f}, {longitude:.6f}"


# -----------------------------
# Routes
# -----------------------------
@app.route("/")
def index():
    db = get_db()
    rows = db.execute(
        "SELECT * FROM reports ORDER BY id DESC"
    ).fetchall()
    reports = [dict(row) for row in rows]
    return render_template("index.html", reports=reports)


@app.route("/report/new", methods=["GET", "POST"])
def create_report():
    if request.method == "POST":
        reporter_name = request.form.get("reporter_name", "").strip()
        category = request.form.get("category", "").strip()
        description = request.form.get("description", "").strip()
        uploaded = request.files.get("image")

        if not reporter_name or not uploaded or uploaded.filename == "":
            flash("이름, 사진은 필수입니다.")
            return redirect(url_for("create_report"))

        if not allowed_file(uploaded.filename):
            flash("지원되는 파일 형식은 jpg, jpeg, png, webp 입니다.")
            return redirect(url_for("create_report"))

        ext = uploaded.filename.rsplit(".", 1)[1].lower()
        unique_name = f"{uuid.uuid4().hex}.{ext}"
        saved_name = secure_filename(unique_name)
        save_path = os.path.join(app.config["UPLOAD_FOLDER"], saved_name)
        uploaded.save(save_path)

        # Metadata extraction
        latitude, longitude = extract_gps_from_image(save_path)

        # Coordinate fallback (from Geolocation API or manual hidden inputs)
        manual_lat = request.form.get("manual_latitude", "").strip()
        manual_lon = request.form.get("manual_longitude", "").strip()
        if (latitude is None or longitude is None) and manual_lat and manual_lon:
            try:
                latitude = float(manual_lat)
                longitude = float(manual_lon)
            except (ValueError, TypeError):
                pass

        address = None
        if latitude is not None and longitude is not None:
            address = reverse_geocode(latitude, longitude)
        
        # Fallback to manual address if reverse geocode fails or if manual address was provided
        manual_addr = request.form.get("manual_address", "").strip()
        if manual_addr and (not address or "좌표" in address):
            address = manual_addr

        # AI Analysis Simulation
        ai_result = simulate_ai_analysis(save_path)
        if not category or category == "":
            category = ai_result["category"]
        
        public_value = ai_result["public_value"]
        landmarks = ai_result["landmarks"]
        urgency = ai_result["urgency"]

        # Automatic initial points based on AI value (points = value * 10)
        reward_points = public_value * 10

        now = datetime.now().isoformat()
        db = get_db()
        db.execute(
            """
            INSERT INTO reports (
                reporter_name, category, description, image_path, 
                latitude, longitude, address, status, reward_points, 
                public_value, landmarks, urgency, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                reporter_name,
                category,
                description,
                f"uploads/{saved_name}",
                latitude,
                longitude,
                address,
                "접수",
                reward_points,
                public_value,
                landmarks,
                urgency,
                now,
                now,
            ),
        )
        db.commit()
        flash("신고가 등록되었습니다.")
        return redirect(url_for("index"))

    return render_template("report_form.html")


@app.route("/report/<int:report_id>")
def report_detail(report_id: int):
    db = get_db()
    row = db.execute("SELECT * FROM reports WHERE id = ?", (report_id,)).fetchone()
    if not row:
        flash("신고를 찾을 수 없습니다.")
        return redirect(url_for("index"))
    report = dict(row)
    return render_template("report_detail.html", report=report)


@app.route("/api/reverse-geocode")
def api_reverse_geocode():
    lat = request.args.get("lat")
    lng = request.args.get("lng")
    if not lat or not lng:
        return {"address": "위치를 가져올 수 없습니다."}
    
    try:
        latitude = float(lat)
        longitude = float(lng)
        address = reverse_geocode(latitude, longitude)
        return {"address": address}
    except (ValueError, TypeError):
        return {"address": "잘못된 좌표 형식입니다."}


@app.route("/admin", methods=["GET", "POST"])
def admin():
    db = get_db()
    if request.method == "POST":
        report_id = request.form.get("report_id")
        status = request.form.get("status", "접수")
        reward_points = request.form.get("reward_points", "0")
        admin_feedback = request.form.get("admin_feedback", "").strip()
        transferred_to = request.form.get("transferred_to", "").strip()
        
        try:
            report_id_int = int(report_id)
            reward_points_int = int(reward_points)
        except (ValueError, TypeError):
            flash("잘못된 데이터 형식입니다.")
            return redirect(url_for("admin"))

        now = datetime.now().isoformat()
        db.execute(
            """
            UPDATE reports SET 
                status = ?, 
                reward_points = ?, 
                admin_feedback = ?, 
                transferred_to = ?, 
                updated_at = ? 
            WHERE id = ?
            """,
            (status, reward_points_int, admin_feedback, transferred_to, now, report_id_int),
        )
        db.commit()
        flash("관리자 처리가 반영되었습니다.")
        return redirect(url_for("admin"))

    rows = db.execute("SELECT * FROM reports ORDER BY id DESC").fetchall()
    reports = [dict(row) for row in rows]
    return render_template("admin.html", reports=reports)


@app.route("/export/csv")
def export_csv():
    import csv
    import io
    from flask import Response

    db = get_db()
    rows = db.execute("SELECT * FROM reports ORDER BY id DESC").fetchall()
    
    output = io.StringIO()
    # Add BOM for Excel Korean support
    output.write('\ufeff')
    writer = csv.writer(output)
    
    # Headers
    writer.writerow([
        "ID", "제보자", "유형", "상세내용", "주소", "위도", "경도", 
        "상태", "포상포인트", "AI가치점수", "행정피드백", "이송부처", "등록일시"
    ])
    
    for r in rows:
        writer.writerow([
            r["id"], r["reporter_name"], r["category"], r["description"], 
            r["address"], r["latitude"], r["longitude"], r["status"], 
            r["reward_points"], r["public_value"], r["admin_feedback"], 
            r["transferred_to"], r["created_at"]
        ])
    
    response = Response(output.getvalue(), mimetype="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=safety_reports.csv"
    return response


@app.route("/report/<int:report_id>/print")
def report_print(report_id: int):
    db = get_db()
    row = db.execute("SELECT * FROM reports WHERE id = ?", (report_id,)).fetchone()
    if not row:
        flash("신고를 찾을 수 없습니다.")
        return redirect(url_for("index"))
    report = dict(row)
    return render_template("report_print.html", report=report)


@app.route("/map")
def safety_map():
    db = get_db()
    rows = db.execute(
        "SELECT * FROM reports WHERE latitude IS NOT NULL AND longitude IS NOT NULL ORDER BY id DESC"
    ).fetchall()
    reports = [dict(row) for row in rows]
    return render_template("map.html", reports=reports)


if __name__ == "__main__":
    init_db()
    # 로컬 실행 시에만 작동하도록 설정 (Debug 모드 오버라이드 방지)
    import sys
    if 'streamlit' not in sys.modules:
        app.run(debug=True, host='127.0.0.1', port=5000)
