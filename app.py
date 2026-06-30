import os
import json
import numpy as np
import pandas as pd
import streamlit as st
from streamlit_echarts import st_echarts
from dotenv import load_dotenv
from data_scientist_agent import run_data_scientist_agent
from financial_agent import run_financial_agent
from pricing_strategy import calculate_dynamic_pricing

# 1. PAGE CONFIGURATION & ENTERPRISE THEME
st.set_page_config(
    page_title="NexusCommerce AI - Management Console",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load global environment rules
load_dotenv()

# Link directly to your existing production database
CSV_FILE = "ecommerce_data.csv"

# Sync Streamlit Session State with actual database
if "db" not in st.session_state:
    st.session_state.db = pd.read_csv(CSV_FILE)

if "ai_pricing_recommendations" not in st.session_state:
    st.session_state.ai_pricing_recommendations = None

if "inventory_insight" not in st.session_state:
    st.session_state.inventory_insight = ""

if "is_pending" not in st.session_state:
    st.session_state.is_pending = False

# --- SIDEBAR CONTROL ROOM ---
with st.sidebar:
    st.image("https://img.icons8.com/fluent/96/000000/artificial-intelligence.png", width=60)
    st.title("NexusCommerce AI")
    st.caption("Developer Platform Console")
    st.markdown("---")
    
    # Dynamic Product Selection
    st.subheader("📦 Inventory Selection")
    product_options = st.session_state.db["Urun_Adi"].tolist()
    selected_product_name = st.selectbox("Select Target Product", product_options)
    
    # Find indexes and row parameters
    target_idx = st.session_state.db[st.session_state.db["Urun_Adi"] == selected_product_name].index[0]
    product_id = st.session_state.db.loc[target_idx, "Urun_ID"]
    stok_miktari = int(st.session_state.db.loc[target_idx, "Kalan_Stok"])
    maliyet = float(st.session_state.db.loc[target_idx, "Maliyet"])
    mevcut_fiyat = float(st.session_state.db.loc[target_idx, "Mevcut_Fiyat"])
    talep_skoru = int(st.session_state.db.loc[target_idx, "Gunluk_Satis"])

    st.markdown("---")
    st.subheader("⚙️ Model & Parameter Matrix")
    model_secimi = st.selectbox("Active Orchestrator LLM", ["Gemini 2.5 Flash (Production)", "Gemini 2.5 Pro (Hedge Mode)"])
    
    st.markdown("---")
    st.subheader("📊 Live Market Telemetry (Simulation)")
    yeni_talep = st.slider("Simulated Target Demand Velocity", 0, 200, talep_skoru)
    yeni_stok = st.slider("Simulated Local Stock Levels", 0, 500, stok_miktari)
    
    if st.button("Inject Market Conditions"):
        st.session_state.db.at[target_idx, "Gunluk_Satis"] = yeni_talep
        st.session_state.db.at[target_idx, "Kalan_Stok"] = yeni_stok
        st.session_state.db.to_csv(CSV_FILE, index=False)
        st.session_state.is_pending = False  # Reset analysis state for the new input
        st.rerun()

# --- MAIN INDUSTRIAL EXECUTIVE PANEL ---
st.markdown(f"# 🔮 NexusCommerce AI - Operational Optimization Hub")
st.markdown(f"Autonomous multi-agent orchestration console monitoring product telemetry for **{selected_product_name}** ({product_id}).")
st.markdown("---")

# 4. TOP TIERS: EXECUTIVE METRIC BOARDS
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="📦 Warehouse Inventory", value=f"{stok_miktari} Units", delta="-7 Risk Delta" if stok_miktari < talep_skoru else "Optimal")
with col2:
    st.metric(label="📉 Item Cost Base", value=f"{maliyet} TL")
with col3:
    st.metric(label="🏷️ Active Retail Price", value=f"{mevcut_fiyat} TL")
with col4:
    st.metric(label="🔥 Projected Demand (7-Day)", value=f"{talep_skoru} Units", delta=f"+{talep_skoru - stok_miktari} Deficit" if talep_skoru > stok_miktari else "Stable")

st.markdown("<br>", unsafe_allow_html=True)

# 5. CORE LAYER: GRAPHICAL ECHARTS INTERFACE & REAL AGENT BRAIN
layout_col1, layout_col2 = st.columns([3, 2])

with layout_col1:
    st.subheader("📈 Pricing Trajectory & Demand Velocity (ECharts)")
    
    options = {
        "tooltip": {"trigger": "axis", "axisPointer": {"type": "cross"}},
        "legend": {"data": ["Retail Price Level", "Demand Momentum"]},
        "grid": {"top": "15%", "left": "5%", "right": "5%", "bottom": "10%", "containLabel": True},
        "xAxis": {
            "type": "category",
            "boundaryGap": False,
            "data": ["04:00", "08:00", "12:00", "16:00", "20:00", "24:00", "Live Telemetry"],
        },
        "yAxis": [
            {"type": "value", "name": "Price (TL)", "min": int(maliyet * 0.5), "max": int(mevcut_fiyat * 2)},
            {"type": "value", "name": "Demand Metric", "min": 0, "max": 200}
        ],
        "series": [
            {
                "name": "Retail Price Level",
                "type": "line",
                "smooth": True,
                "data": [mevcut_fiyat * 0.9, mevcut_fiyat * 0.95, mevcut_fiyat, mevcut_fiyat, mevcut_fiyat * 1.02, mevcut_fiyat, mevcut_fiyat],
                "lineStyle": {"color": "#5470c6", "width": 3},
                "itemStyle": {"borderWidth": 2}
            },
            {
                "name": "Demand Momentum",
                "type": "line",
                "smooth": True,
                "yAxisIndex": 1,
                "data": [int(talep_skoru*0.5), int(talep_skoru*0.7), int(talep_skoru*0.9), talep_skoru, int(talep_skoru*1.1), int(talep_skoru*0.95), talep_skoru],
                "lineStyle": {"color": "#91cc75", "width": 3},
            }
        ],
    }
    st_echarts(options=options, height="350px")

with layout_col2:
    st.subheader("🤖 Live Multi-Agent Reasoner Session")
    
    # 🎯 KRİTİK DÜZELTME: Eğer ürün değişirse pend State'ini sıfırlayarak ajanı o ürüne özel yeniden tetikliyoruz
    if "last_selected_product" not in st.session_state or st.session_state.last_selected_product != selected_product_name:
        st.session_state.last_selected_product = selected_product_name
        st.session_state.is_pending = False

    if not st.session_state.is_pending:
        with st.spinner(f"🕵️‍♂️ Orchestrating agent focus specifically on {selected_product_name}..."):
            # Ajanların genel fonksiyonlarını çağırıyoruz
            genel_rapor = run_data_scientist_agent()
            st.session_state.ai_pricing_recommendations = calculate_dynamic_pricing()
            
            # 🔥 MÜHENDİSLİK DOKUNUŞU: Gemini'den gelen genel metni sadece seçilen ürüne odaklanacak şekilde LLM filtresinden geçiriyoruz
            from google import genai
            client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
            
            filter_prompt = f"""
            Sana bir multi-agent sisteminin ürettiği tüm dükkan raporu verilecek.
            Senden isteğim, bu rapordan SADECE ve YALNIZCA '{selected_product_name} ({product_id})' ürünü ile ilgili olan analiz, durum ve öneri kısımlarını ayıklayıp, 
            mağaza sahibine hitaben samimi ve profesyonel bir dille sunmandır. Diğer ürünlerden bahsetme.
            
            Genel Rapor:
            {genel_rapor}
            """
            response = client.models.generate_content(model='gemini-2.5-flash', contents=filter_prompt)
            st.session_state.inventory_insight = response.text
            st.session_state.is_pending = True

    st.info(st.session_state.inventory_insight)
    
    proposed_ui_price = mevcut_fiyat
    if st.session_state.ai_pricing_recommendations:
        for item in st.session_state.ai_pricing_recommendations:
            if item["Urun_ID"] == product_id:
                proposed_ui_price = item["Onerilen_Yeni_Fiyat"]
                
    st.metric(label="🎯 System Optimization Price Target", value=f"{proposed_ui_price} TL")

st.markdown("---")

# 6. HUMAN-IN-THE-LOOP (HITL) ENTERPRISE AUDIT GATEWAY
st.subheader("🤝 Human-in-the-Loop Strategic Authorization Deck")
st.write("Authorize the dynamic margin adjustments recommended above to deploy changes directly to the live store database.")

onay_col1, onay_col2, _ = st.columns([1.5, 1.5, 4])

with onay_col1:
    if st.button("🚀 Authorize & Deploy to Store", use_container_width=True, type="primary"):
        df_csv = pd.read_csv(CSV_FILE)
        
        if st.session_state.ai_pricing_recommendations:
            for rec in st.session_state.ai_pricing_recommendations:
                idx = df_csv[df_csv['Urun_ID'] == rec['Urun_ID']].index[-1]
                df_csv.at[idx, 'Mevcut_Fiyat'] = rec['Onerilen_Yeni_Fiyat']
                
        df_csv.to_csv(CSV_FILE, index=False)
        st.session_state.db = df_csv
        
        st.toast(f"Strategy deployed! {selected_product_name} dynamics pushed to live core system layers.", icon="🚀")
        st.session_state.is_pending = False
        st.rerun()

with onay_col2:
    if st.button("❌ Dismiss Recommendations", use_container_width=True):
        st.toast("Pricing updates dropped by manager. Safe baseline metrics intact.", icon="🛑")
        st.session_state.is_pending = False
        st.rerun()