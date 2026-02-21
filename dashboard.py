import streamlit as st
import pandas as pd
from supabase import create_client
import os
import httpx
import json
import random
from dotenv import load_dotenv
import streamlit.components.v1 as components

load_dotenv()

# --- Connections ---
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"

st.set_page_config(page_title="Digital Curator", layout="wide", page_icon="✨")

# --- 🔥 ULTIMATE REFINED STYLING ---
st.markdown("""
    <style>
    /* Global Background */
    .stApp { background-color: #0E1117; }

    /* Compact Gradient Button */
    div.stButton > button {
        background: linear-gradient(45deg, #FF4B4B, #FF8C42) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        height: 2.8rem !important;
        transition: transform 0.2s ease;
    }
    div.stButton > button:hover {
        transform: scale(1.02);
    }

    /* Video Masking: Hides the Instagram 'View Profile' bar */
    .video-mask {
        width: 100%;
        overflow: hidden;
        position: relative;
        border-radius: 12px;
        border: 1px solid #333333;
        background: #000;
    }
    .video-mask iframe {
        position: absolute;
        top: -65px; /* Crops the header */
        left: 0;
        width: 100%;
    }

    /* Compact Animation for Inspiration Box */
    @keyframes fadeInDown {
        0% { opacity: 0; transform: translateY(-15px); }
        100% { opacity: 1; transform: translateY(0); }
    }
    .inspiration-box {
        animation: fadeInDown 0.5s ease-out;
        border: 2px solid #FF4B4B !important;
        padding: 20px;
        border-radius: 16px;
        background-color: #1E1E1E;
        margin-bottom: 25px;
        box-shadow: 0 10px 30px rgba(255, 75, 75, 0.15);
    }

    /* Grid Card Styling */
    [data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 16px !important;
        border: 1px solid #333333 !important;
        background-color: #1E1E1E;
        transition: transform 0.2s ease;
    }
    [data-testid="stVerticalBlockBorderWrapper"]:hover {
         transform: translateY(-5px);
         border-color: #FF4B4B !important;
    }

    /* Search Input Styling */
    .stTextInput input {
        background-color: #1E1E1E !important;
        color: white !important;
        border: 1px solid #333333 !important;
        border-radius: 10px !important;
    }

    /* Typography */
    .category-tag { font-size: 11px; color: #A0AEC0; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; }
    .smart-summary { height: 45px; font-size: 14px; color: #F7FAFC; line-height: 1.5; overflow: hidden; }
    </style>
    """, unsafe_allow_html=True)

# --- Fetch Data ---
@st.cache_data(ttl=60)
def fetch_data():
    try:
        response = supabase.table("saves").select("*").order("created_at", desc=True).execute()
        return pd.DataFrame(response.data)
    except:
        return pd.DataFrame()

df = fetch_data()

# --- Random Inspiration Logic ---
if 'random_index' not in st.session_state:
    st.session_state.random_index = None

def get_random():
    if not df.empty:
        st.balloons()
        st.session_state.random_index = random.randint(0, len(df) - 1)

# --- Header ---
col_title, col_btn = st.columns([3, 1])
with col_title:
    st.title("✨ Digital Curator")
    st.caption("AI-Powered Semantic Archive of your Visual Inspiration.")

with col_btn:
    st.write(" ") 
    st.button("🎲 Inspire Me", on_click=get_random, use_container_width=True)

# --- 💡 COMPACT & CLIPPED INSPIRATION SECTION ---
if st.session_state.random_index is not None:
    row = df.iloc[st.session_state.random_index]
    embed_url = str(row['url']).split("?")[0].rstrip("/") + "/embed/"
    
    # Combined HTML block to prevent layout breaking
    st.markdown(f"""
        <div class="inspiration-box">
            <div style="display: flex; flex-wrap: wrap; gap: 20px; align-items: center;">
                <div style="flex: 1; min-width: 280px;">
                    <p class="category-tag">⭐ Featured Discovery</p>
                    <h3 style="color: white; margin: 10px 0;">{row['summary']}</h3>
                    <p style="color: #A0AEC0; font-size: 13px;">Breaking your filter bubble with a random spark.</p>
                </div>
                <div style="flex: 1; min-width: 280px;">
                    <div class="video-mask" style="height: 320px;">
                        <iframe src="{embed_url}" frameborder="0" scrolling="no" style="height: 450px; top: -65px;"></iframe>
                    </div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("✕ Close Discovery", use_container_width=True):
        st.session_state.random_index = None
        st.rerun()

st.markdown("---")

# --- 🔍 SMART FILTERS ---
if not df.empty:
    all_tags = sorted(df['category'].unique().tolist())
    
    col_s, col_t, col_ai = st.columns([2, 1, 1])
    with col_s:
        search = st.text_input("🔍 Search", placeholder="Vibe search...", label_visibility="collapsed")
    with col_t:
        selected_tags = st.multiselect("🏷️ Tags", options=all_tags, placeholder="All Tags", label_visibility="collapsed")
    with col_ai:
        use_ai = st.toggle("🧠 AI Smart Search")

    # Filter Logic
    filtered = df.copy()
    if selected_tags:
        filtered = filtered[filtered['category'].isin(selected_tags)]

    if search:
        if use_ai:
            with st.spinner("🤖 Matching vibes..."):
                db_context = filtered[['url', 'category', 'summary']].to_dict(orient='records')
                prompt = f"Database: {json.dumps(db_context)}\nQuery: '{search}'\nReturn ONLY a JSON list of URLs. No prose."
                try:
                    res = httpx.post(MODEL_URL, json={"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"responseMimeType": "application/json"}}, timeout=15.0)
                    matched_urls = json.loads(res.json()['candidates'][0]['content']['parts'][0]['text'])
                    filtered = filtered[filtered['url'].isin(matched_urls)]
                except:
                    filtered = filtered[filtered['summary'].str.contains(search, case=False, na=False)]
        else:
            filtered = filtered[filtered['summary'].str.contains(search, case=False, na=False)]

    # --- 🖼️ DISPLAY GRID (Clipped & Symmetrical) ---
    if filtered.empty:
        st.warning("No matches found.")
    else:
        for i in range(0, len(filtered), 3):
            cols = st.columns(3)
            for j in range(3):
                if i + j < len(filtered):
                    row = filtered.iloc[i + j]
                    with cols[j]:
                        with st.container(border=True):
                            st.markdown(f"""
                                <span class="category-tag">🏷️ {str(row['category']).upper()}</span>
                                <div class="smart-summary" title="{row['summary']}">{row['summary']}</div>
                            """, unsafe_allow_html=True)
                            
                            u = str(row['url']).split("?")[0].rstrip("/") + "/embed/"
                            st.markdown(f"""
                                <div class="video-mask" style="height: 320px;">
                                    <iframe src="{u}" frameborder="0" scrolling="no" style="height: 450px; top: -65px;"></iframe>
                                </div>
                            """, unsafe_allow_html=True)
else:
    st.info("WhatsApp a Reel link to your bot to start your collection!")