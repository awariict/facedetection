"""
styles.py
Centralized custom CSS for a clean, professional look.

Color palette:
  Primary (Indigo)   #2563EB
  Primary Dark       #1E3A8A
  Teal Accent        #0D9488
  Amber Accent       #F59E0B
  Rose Accent        #E11D48
  Background         #F4F6FB
  Surface / Cards    #FFFFFF
  Text Primary       #0F172A
  Text Secondary     #64748B
  Border             #E2E8F0
"""

import streamlit as st


def inject_css():
    st.markdown(
        """
        <style>
        /* ---------- GLOBAL ---------- */
        html, body, [class*="css"] {
            font-family: 'Inter', 'Segoe UI', sans-serif;
        }

        .stApp {
            background-color: #F4F6FB;
        }

        #MainMenu, footer {visibility: hidden;}

        /* ---------- TOP HEADER ---------- */
        .top-header {
            background: linear-gradient(135deg, #1E3A8A 0%, #2563EB 60%, #0D9488 100%);
            padding: 28px 32px;
            border-radius: 16px;
            margin-bottom: 24px;
            box-shadow: 0 8px 24px rgba(30, 58, 138, 0.25);
        }
        .top-header h1 {
            color: #FFFFFF;
            font-size: 28px;
            font-weight: 700;
            margin: 0 0 6px 0;
        }
        .top-header p {
            color: #DBEAFE;
            font-size: 14.5px;
            margin: 0;
        }

        /* ---------- SIDEBAR ---------- */
        section[data-testid="stSidebar"] {
            background-color: #0F172A;
        }
        section[data-testid="stSidebar"] * {
            color: #E2E8F0 !important;
        }
        .brand-box {
            text-align: center;
            padding: 18px 0 10px 0;
        }
        .brand-icon { font-size: 34px; }
        .brand-title {
            font-size: 22px;
            font-weight: 800;
            color: #FFFFFF !important;
            letter-spacing: 0.5px;
        }
        .brand-subtitle {
            font-size: 12px;
            color: #94A3B8 !important;
        }
        .sidebar-divider {
            border-top: 1px solid #1E293B;
            margin: 14px 0;
        }
        .sidebar-footer {
            font-size: 11px;
            color: #64748B !important;
            text-align: center;
            margin-top: 20px;
        }
        section[data-testid="stSidebar"] div[role="radiogroup"] label {
            background-color: #1E293B;
            border-radius: 10px;
            padding: 10px 12px;
            margin-bottom: 6px;
            transition: 0.15s ease-in-out;
        }
        section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
            background-color: #2563EB;
        }

        .status-pill {
            display: inline-block;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
        }
        .status-online {
            background-color: rgba(13, 148, 136, 0.18);
            color: #2DD4BF !important;
        }
        .status-offline {
            background-color: rgba(225, 29, 72, 0.18);
            color: #FB7185 !important;
        }

        /* ---------- CARDS ---------- */
        .section-card {
            background-color: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 20px;
            box-shadow: 0 2px 10px rgba(15, 23, 42, 0.04);
        }

        /* ---------- METRIC CARDS ---------- */
        .metric-card {
            border-radius: 14px;
            padding: 18px 20px;
            color: white;
            box-shadow: 0 6px 16px rgba(15, 23, 42, 0.10);
        }
        .metric-label {
            font-size: 13px;
            font-weight: 500;
            opacity: 0.9;
        }
        .metric-value {
            font-size: 32px;
            font-weight: 800;
            margin-top: 6px;
        }
        .metric-blue  { background: linear-gradient(135deg, #2563EB, #1E40AF); }
        .metric-teal  { background: linear-gradient(135deg, #0D9488, #0F766E); }
        .metric-amber { background: linear-gradient(135deg, #F59E0B, #D97706); }
        .metric-rose  { background: linear-gradient(135deg, #E11D48, #BE123C); }

        /* ---------- RECENT LIST ---------- */
        .recent-item {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 8px 0;
            border-bottom: 1px solid #F1F5F9;
        }
        .recent-avatar {
            width: 36px;
            height: 36px;
            border-radius: 50%;
            background: linear-gradient(135deg, #2563EB, #0D9488);
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            font-size: 14px;
        }
        .recent-name {
            font-weight: 600;
            font-size: 14px;
            color: #0F172A;
        }
        .recent-time {
            font-size: 12px;
            color: #64748B;
        }

        /* ---------- SUCCESS BANNER ---------- */
        .success-banner {
            display: flex;
            align-items: center;
            gap: 16px;
            background: linear-gradient(135deg, #ECFDF5, #D1FAE5);
            border: 1px solid #6EE7B7;
            border-radius: 14px;
            padding: 18px 20px;
            margin-top: 12px;
        }
        .success-icon {
            font-size: 28px;
            background-color: #10B981;
            color: white;
            width: 44px;
            height: 44px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .success-title {
            font-size: 17px;
            font-weight: 700;
            color: #065F46;
        }
        .success-sub {
            font-size: 13px;
            color: #047857;
        }

        .row-divider {
            border: none;
            border-top: 1px solid #F1F5F9;
            margin: 4px 0 10px 0;
        }

        /* ---------- BUTTONS ---------- */
        div.stButton > button, div.stFormSubmitButton > button {
            background: linear-gradient(135deg, #2563EB, #1E40AF);
            color: white;
            border: none;
            border-radius: 10px;
            padding: 8px 18px;
            font-weight: 600;
            transition: 0.15s ease-in-out;
        }
        div.stButton > button:hover, div.stFormSubmitButton > button:hover {
            opacity: 0.9;
            transform: translateY(-1px);
        }

        /* ---------- INPUTS ---------- */
        div[data-baseweb="input"], div[data-baseweb="select"] {
            border-radius: 10px !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
