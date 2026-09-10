"""
FaceTrack — AI Facial Recognition Attendance System
Main application entry point.

Author: Built for Awari
Stack: Streamlit + OpenCV (LBPH) + MongoDB Atlas
"""

import streamlit as st
from datetime import datetime, date
import pandas as pd
import numpy as np
from PIL import Image
import io

from utils.styles import inject_css
from utils.database import (
    get_database,
    add_user,
    get_all_users,
    get_user_by_user_id,
    delete_user,
    mark_attendance,
    get_attendance_records,
    already_marked_today,
    get_dashboard_stats,
)
from utils.face_utils import (
    detect_and_crop_face,
    image_to_base64,
    base64_to_cv2_image,
    train_recognizer_from_users,
    recognize_face,
    cv2_image_from_pil,
)

# ----------------------------------------------------------------------------
# PAGE CONFIG — must be the first Streamlit call
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="FaceTrack | Attendance System",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()

# ----------------------------------------------------------------------------
# DATABASE CONNECTION
# ----------------------------------------------------------------------------
try:
    db = get_database()
    db_connected = True
except Exception as e:
    db = None
    db_connected = False
    db_error = str(e)

# ----------------------------------------------------------------------------
# SESSION STATE
# ----------------------------------------------------------------------------
if "capture_samples" not in st.session_state:
    st.session_state.capture_samples = []
if "page" not in st.session_state:
    st.session_state.page = "Dashboard"

# ----------------------------------------------------------------------------
# SIDEBAR — BRANDING + NAVIGATION
# ----------------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        """
        <div class="brand-box">
            <div class="brand-icon">🛡️</div>
            <div class="brand-title">FaceTrack</div>
            <div class="brand-subtitle">Facial Recognition Attendance</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div class='sidebar-divider'></div>", unsafe_allow_html=True)

    page = st.radio(
        "Navigate",
        [
            "📊 Dashboard",
            "🧾 Register New Person",
            "🎯 Mark Attendance",
            "📁 Attendance Records",
            "👥 Manage People",
            "ℹ️ About",
        ],
        label_visibility="collapsed",
    )

    st.markdown("<div class='sidebar-divider'></div>", unsafe_allow_html=True)

    if db_connected:
        st.markdown(
            "<div class='status-pill status-online'>● Database Connected</div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            "<div class='status-pill status-offline'>● Database Offline</div>",
            unsafe_allow_html=True,
        )
        with st.expander("Connection error details"):
            st.code(db_error)

    st.markdown(
        "<div class='sidebar-footer'>© 2026 FaceTrack · Built with Streamlit</div>",
        unsafe_allow_html=True,
    )

# ----------------------------------------------------------------------------
# HEADER
# ----------------------------------------------------------------------------
st.markdown(
    """
    <div class="top-header">
        <h1>Facial Recognition Attendance System</h1>
        <p>Secure, fast, and reliable attendance tracking powered by computer vision.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if not db_connected:
    st.error(
        "⚠️ Could not connect to MongoDB Atlas. Please check your `MONGO_URI` in "
        "Streamlit secrets. The app will still render, but no data can be saved or retrieved."
    )

# ============================================================================
# PAGE: DASHBOARD
# ============================================================================
if page == "📊 Dashboard":
    if db_connected:
        stats = get_dashboard_stats(db)
    else:
        stats = {"total_users": 0, "today_count": 0, "week_count": 0, "last_7_days": {}}

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(
            f"""<div class="metric-card metric-blue">
                    <div class="metric-label">Registered People</div>
                    <div class="metric-value">{stats['total_users']}</div>
                </div>""",
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f"""<div class="metric-card metric-teal">
                    <div class="metric-label">Present Today</div>
                    <div class="metric-value">{stats['today_count']}</div>
                </div>""",
            unsafe_allow_html=True,
        )
    with col3:
        rate = 0
        if stats["total_users"] > 0:
            rate = round((stats["today_count"] / stats["total_users"]) * 100, 1)
        st.markdown(
            f"""<div class="metric-card metric-amber">
                    <div class="metric-label">Today's Attendance Rate</div>
                    <div class="metric-value">{rate}%</div>
                </div>""",
            unsafe_allow_html=True,
        )
    with col4:
        st.markdown(
            f"""<div class="metric-card metric-rose">
                    <div class="metric-label">Check-ins (7 Days)</div>
                    <div class="metric-value">{stats['week_count']}</div>
                </div>""",
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    col_chart, col_recent = st.columns([1.4, 1])

    with col_chart:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.subheader("Attendance — Last 7 Days")
        if stats["last_7_days"]:
            chart_df = pd.DataFrame(
                {
                    "Date": list(stats["last_7_days"].keys()),
                    "Check-ins": list(stats["last_7_days"].values()),
                }
            )
            st.bar_chart(chart_df.set_index("Date"), color="#2563EB")
        else:
            st.info("No attendance data yet. Records will appear here once people start checking in.")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_recent:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.subheader("Recent Check-ins")
        if db_connected:
            recent = get_attendance_records(db, limit=6)
            if recent:
                for r in recent:
                    st.markdown(
                        f"""
                        <div class="recent-item">
                            <div class="recent-avatar">{r['name'][0].upper()}</div>
                            <div>
                                <div class="recent-name">{r['name']}</div>
                                <div class="recent-time">{r['timestamp'].strftime('%d %b %Y, %I:%M %p')}</div>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            else:
                st.info("No check-ins recorded yet.")
        st.markdown("</div>", unsafe_allow_html=True)

# ============================================================================
# PAGE: REGISTER NEW PERSON
# ============================================================================
elif page == "🧾 Register New Person":
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.subheader("Register a New Person")
    st.caption(
        "Capture at least 3 clear face samples for accurate recognition. "
        "Ensure good lighting and only one face is visible in frame."
    )

    with st.form("register_form", clear_on_submit=False):
        c1, c2 = st.columns(2)
        with c1:
            full_name = st.text_input("Full Name *")
            user_id = st.text_input("Unique ID / Matric / Staff No. *")
        with c2:
            department = st.text_input("Department / Class")
            email = st.text_input("Email")
        submit_details = st.form_submit_button("Save Details & Proceed to Capture ➜")

    if submit_details:
        if not full_name or not user_id:
            st.warning("Full Name and Unique ID are required.")
        elif db_connected and get_user_by_user_id(db, user_id):
            st.error(f"A person with ID '{user_id}' is already registered.")
        else:
            st.session_state.pending_user = {
                "user_id": user_id,
                "name": full_name,
                "department": department,
                "email": email,
            }
            st.session_state.capture_samples = []
            st.success("Details saved. Now capture face samples below.")

    st.markdown("</div>", unsafe_allow_html=True)

    if "pending_user" in st.session_state:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.markdown(
            f"**Capturing samples for:** {st.session_state.pending_user['name']} "
            f"({st.session_state.pending_user['user_id']})"
        )

        cam_col, list_col = st.columns([1, 1])
        with cam_col:
            img_file = st.camera_input("Capture face sample", key=f"cam_{len(st.session_state.capture_samples)}")
            if img_file is not None:
                pil_img = Image.open(img_file)
                cv2_img = cv2_image_from_pil(pil_img)
                face, found = detect_and_crop_face(cv2_img)
                if found:
                    st.session_state.capture_samples.append(face)
                    st.success(f"Sample #{len(st.session_state.capture_samples)} captured ✔")
                else:
                    st.error("No face detected in that shot. Try again with better lighting/angle.")

        with list_col:
            st.markdown(f"**Samples collected: {len(st.session_state.capture_samples)} / 3 minimum**")
            if st.session_state.capture_samples:
                thumb_cols = st.columns(4)
                for i, face_img in enumerate(st.session_state.capture_samples):
                    with thumb_cols[i % 4]:
                        st.image(face_img, width=70)

            b1, b2 = st.columns(2)
            with b1:
                if st.button("🗑 Clear Samples"):
                    st.session_state.capture_samples = []
                    st.rerun()
            with b2:
                finish = st.button("✅ Finish Registration", type="primary")

            if finish:
                if len(st.session_state.capture_samples) < 3:
                    st.warning("Please capture at least 3 face samples before finishing.")
                elif not db_connected:
                    st.error("Cannot save — database is not connected.")
                else:
                    encoded_faces = [image_to_base64(f) for f in st.session_state.capture_samples]
                    user_doc = st.session_state.pending_user.copy()
                    user_doc["face_samples"] = encoded_faces
                    user_doc["registered_at"] = datetime.utcnow()
                    add_user(db, user_doc)
                    st.success(f"🎉 {user_doc['name']} registered successfully!")
                    st.balloons()
                    del st.session_state.pending_user
                    st.session_state.capture_samples = []

        st.markdown("</div>", unsafe_allow_html=True)

# ============================================================================
# PAGE: MARK ATTENDANCE
# ============================================================================
elif page == "🎯 Mark Attendance":
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.subheader("Mark Attendance via Face Recognition")
    st.caption("Look directly at the camera and capture a photo to check in.")

    if not db_connected:
        st.error("Database not connected. Cannot mark attendance.")
    else:
        users = get_all_users(db)
        if len(users) == 0:
            st.info("No one is registered yet. Please register people first.")
        else:
            snap = st.camera_input("Capture your face to check in")
            if snap is not None:
                with st.spinner("Analyzing face..."):
                    pil_img = Image.open(snap)
                    cv2_img = cv2_image_from_pil(pil_img)
                    face, found = detect_and_crop_face(cv2_img)

                    if not found:
                        st.error("No face detected. Please try again.")
                    else:
                        recognizer, label_map = train_recognizer_from_users(users)
                        matched_id, confidence = recognize_face(recognizer, label_map, face)

                        if matched_id is None:
                            st.error("❌ Face not recognized. Please register first or try again with better lighting.")
                        else:
                            matched_user = get_user_by_user_id(db, matched_id)
                            if already_marked_today(db, matched_id):
                                st.warning(
                                    f"⚠️ {matched_user['name']} has already been marked present today."
                                )
                            else:
                                mark_attendance(db, matched_id, matched_user["name"])
                                st.markdown(
                                    f"""
                                    <div class="success-banner">
                                        <div class="success-icon">✔</div>
                                        <div>
                                            <div class="success-title">Welcome, {matched_user['name']}!</div>
                                            <div class="success-sub">Attendance marked at {datetime.now().strftime('%I:%M %p')} · Match confidence: {round(100 - confidence, 1)}%</div>
                                        </div>
                                    </div>
                                    """,
                                    unsafe_allow_html=True,
                                )
                                st.balloons()

    st.markdown("</div>", unsafe_allow_html=True)

# ============================================================================
# PAGE: ATTENDANCE RECORDS
# ============================================================================
elif page == "📁 Attendance Records":
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.subheader("Attendance Records")

    if not db_connected:
        st.error("Database not connected.")
    else:
        c1, c2, c3 = st.columns(3)
        with c1:
            filter_date = st.date_input("Filter by date", value=None)
        with c2:
            users = get_all_users(db)
            name_options = ["All"] + sorted([u["name"] for u in users])
            filter_name = st.selectbox("Filter by person", name_options)
        with c3:
            st.write("")
            st.write("")
            refresh = st.button("🔄 Refresh")

        records = get_attendance_records(
            db,
            filter_date=filter_date if filter_date else None,
            filter_name=None if filter_name == "All" else filter_name,
            limit=1000,
        )

        if records:
            df = pd.DataFrame(records)
            df = df[["name", "user_id", "date", "timestamp"]]
            df.columns = ["Name", "ID", "Date", "Time"]
            df["Time"] = pd.to_datetime(df["Time"]).dt.strftime("%I:%M %p")
            st.dataframe(df, use_container_width=True, hide_index=True)

            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "⬇ Download as CSV",
                data=csv,
                file_name=f"attendance_{date.today()}.csv",
                mime="text/csv",
            )
        else:
            st.info("No records match your filters.")

    st.markdown("</div>", unsafe_allow_html=True)

# ============================================================================
# PAGE: MANAGE PEOPLE
# ============================================================================
elif page == "👥 Manage People":
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.subheader("Manage Registered People")

    if not db_connected:
        st.error("Database not connected.")
    else:
        users = get_all_users(db)
        if not users:
            st.info("No one has been registered yet.")
        else:
            search = st.text_input("🔍 Search by name or ID")
            filtered = [
                u for u in users
                if search.lower() in u["name"].lower() or search.lower() in u["user_id"].lower()
            ] if search else users

            for u in filtered:
                with st.container():
                    cols = st.columns([0.6, 2, 1.5, 1.5, 1])
                    with cols[0]:
                        if u.get("face_samples"):
                            img = base64_to_cv2_image(u["face_samples"][0])
                            st.image(img, width=55)
                    with cols[1]:
                        st.markdown(f"**{u['name']}**")
                        st.caption(u["user_id"])
                    with cols[2]:
                        st.write(u.get("department", "—"))
                    with cols[3]:
                        st.write(u.get("email", "—"))
                    with cols[4]:
                        if st.button("🗑 Delete", key=f"del_{u['user_id']}"):
                            delete_user(db, u["user_id"])
                            st.rerun()
                    st.markdown("<hr class='row-divider'>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# ============================================================================
# PAGE: ABOUT
# ============================================================================
elif page == "ℹ️ About":
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.subheader("About FaceTrack")
    st.markdown(
        """
        **FaceTrack** is a facial recognition–based attendance system built with:

        - **Streamlit** — interactive web interface
        - **OpenCV (LBPH Face Recognizer)** — face detection & recognition
        - **MongoDB Atlas** — cloud database for people & attendance records

        **How it works:**
        1. Register a person with a few face samples.
        2. The system trains a lightweight recognition model on registered faces.
        3. When someone checks in, their captured photo is compared against known faces.
        4. A match above the confidence threshold marks attendance automatically (once per day).

        **Deployment:** This app is designed to run on **Streamlit Community Cloud**,
        connected to a **MongoDB Atlas** cluster via a connection string stored in
        `st.secrets`. See the included `README.md` for full setup steps.
        """
    )
    st.markdown("</div>", unsafe_allow_html=True)
