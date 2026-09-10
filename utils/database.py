"""
database.py
Handles all MongoDB Atlas interactions for FaceTrack.
"""

import streamlit as st
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime, timedelta, date as date_cls


@st.cache_resource(show_spinner=False)
def get_database():
    """
    Establishes a cached connection to MongoDB Atlas.
    Requires MONGO_URI to be set in Streamlit secrets (.streamlit/secrets.toml
    locally, or the Secrets manager on Streamlit Community Cloud).
    """
    mongo_uri = st.secrets["MONGO_URI"]
    db_name = st.secrets.get("MONGO_DB_NAME", "facetrack_db")

    client = MongoClient(mongo_uri, server_api=ServerApi("1"))
    # Verify connection immediately so failures surface at startup
    client.admin.command("ping")
    return client[db_name]


# ------------------------------------------------------------------------
# USERS
# ------------------------------------------------------------------------
def add_user(db, user_doc: dict):
    return db.users.insert_one(user_doc)


def get_all_users(db):
    return list(db.users.find({}))


def get_user_by_user_id(db, user_id: str):
    return db.users.find_one({"user_id": user_id})


def delete_user(db, user_id: str):
    db.users.delete_one({"user_id": user_id})
    db.attendance.delete_many({"user_id": user_id})


# ------------------------------------------------------------------------
# ATTENDANCE
# ------------------------------------------------------------------------
def mark_attendance(db, user_id: str, name: str):
    now = datetime.utcnow()
    doc = {
        "user_id": user_id,
        "name": name,
        "timestamp": now,
        "date": now.strftime("%Y-%m-%d"),
    }
    db.attendance.insert_one(doc)
    return doc


def already_marked_today(db, user_id: str) -> bool:
    today_str = datetime.utcnow().strftime("%Y-%m-%d")
    existing = db.attendance.find_one({"user_id": user_id, "date": today_str})
    return existing is not None


def get_attendance_records(db, filter_date=None, filter_name=None, limit=100):
    query = {}
    if filter_date:
        if isinstance(filter_date, date_cls):
            query["date"] = filter_date.strftime("%Y-%m-%d")
        else:
            query["date"] = str(filter_date)
    if filter_name:
        query["name"] = filter_name

    cursor = db.attendance.find(query).sort("timestamp", -1).limit(limit)
    return list(cursor)


# ------------------------------------------------------------------------
# DASHBOARD STATS
# ------------------------------------------------------------------------
def get_dashboard_stats(db):
    total_users = db.users.count_documents({})

    today_str = datetime.utcnow().strftime("%Y-%m-%d")
    today_count = db.attendance.count_documents({"date": today_str})

    seven_days_ago = datetime.utcnow() - timedelta(days=6)
    week_count = db.attendance.count_documents({"timestamp": {"$gte": seven_days_ago}})

    last_7_days = {}
    for i in range(6, -1, -1):
        d = (datetime.utcnow() - timedelta(days=i)).strftime("%Y-%m-%d")
        label = (datetime.utcnow() - timedelta(days=i)).strftime("%d %b")
        last_7_days[label] = db.attendance.count_documents({"date": d})

    return {
        "total_users": total_users,
        "today_count": today_count,
        "week_count": week_count,
        "last_7_days": last_7_days,
    }
