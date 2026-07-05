import os
import json
import numpy as np
import pandas as pd
import streamlit as st
from streamlit_echarts import st_echarts
from dotenv import load_dotenv

# Merkezi veri tabanı bağlantısı
from database_manager import sql_query_to_dataframe, sql_execute_command
from data_scientist_agent import run_data_scientist_agent
from financial_agent import run_financial_agent
from pricing_strategy import calculate_dynamic_pricing
from ecommerce_gateway import ECommerceGateway

# 1. PAGE CONFIGURATION & ENTERPRISE THEME
st.set_page_config(
    page_title="NexusCommerce AI - Management Console",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load global environment rules
load_dotenv()

# --- 📊 INITIALIZATION LAYER ---
if "ai_pricing_recommendations" not in st.session_state:
    st.session_state.ai_pricing_recommendations = None

if "inventory_insight" not in st.session_state:
    st.session_state.inventory_insight = ""

if "financial_insight" not in st.session_state:
    st.session_state.financial_insight = ""

if "is_pending" not in st.session_state:
    st.session_state.is_pending = False

# Tüm ürünlerin isimlerini Selectbox için SQL'den çekiyoruz
product_options_df = sql_query_to_dataframe("SELECT Urun_Adi FROM products")
product_options = product_options_df["Urun_Adi"].tolist() if not product_options_df.empty else []

# --- SIDEBAR CONTROL ROOM ---
with st.sidebar:
    st.image("https://img.icons8.com/fluent/96/000000/artificial-intelligence.png", width=60)
    st.title("NexusCommerce AI")
    st.caption("Developer Platform Console")
    st.markdown("---")
    
    st.subheader("📦 Inventory Selection")
    if product_options:
        selected_product_name = st.selectbox("Select Target Product", product_options)
        product_data = sql_query_to_dataframe("SELECT * FROM products WHERE Urun_Adi = ?", (selected_product_name,))
        
        if not product_data.empty:
            product_id = product_data.loc[0, "Urun_ID"]
            stok_miktari = int(product_data.loc[0, "Kalan_Stok"])
            maliyet = float(product_data.loc[0, "Maliyet"])
            mevcut_fiyat = float(product_data.loc[0, "Mevcut_Fiyat"])
            talep_skoru = int(product_data.loc[0, "Gunluk_Satis"])
            
            # 🚨 YENİ: Veri tabanından rakip fiyat metriklerini okuyoruz
            rakip_a_fiyati = float(product_data.loc[0, "Rakip_Fiyat_A"])
            rakip_b_fiyati = float(product_data.loc[0, "Rakip_Fiyat_B"])
            pazar_ortalamasi = (rakip_a_fiyati + rakip_b_fiyati) / 2

            st.markdown("---")
            st.subheader("⚙️ Model & Parameter Matrix")
            model_secimi = st.selectbox("Active Orchestrator LLM", ["Gemini 2.5 Flash (Production)", "Gemini 2.5 Pro (Hedge Mode)"])
            
            st.markdown("---")
            st.subheader("📊 Live Market Telemetry (Simulation)")
            yeni_talep = st.slider("Simulated Target Demand Velocity", 0, 200, talep_skoru)
            yeni_stok = st.slider("Simulated Local Stock Levels", 0, 500, stok_miktari)
            
            if st.button("Inject Market Conditions"):
                eski_stok = stok_miktari
                sql_execute_command(
                    "UPDATE products SET Gunluk_Satis = ?, Kalan_Stok = ? WHERE Urun_ID = ?",
                    (yeni_talep, yeni_stok, product_id)
                )
                sql_execute_command(
                    """INSERT INTO audit_logs (Urun_ID, Islem_Turu, Eski_Deger, Yeni_Deger) 
                       VALUES (?, 'STOK_ENJEKSIYON', ?, ?)""",
                    (product_id, eski_stok, yeni_stok)
                )
                st.session_state.is_pending = False  
                st.rerun()
    else:
        st.error("Veri tabanından ürün listesi yüklenemedi!")

# --- MAIN INDUSTRIAL EXECUTIVE PANEL ---
if product_options and not product_data.empty:
    st.markdown(f"# 🔮 NexusCommerce AI - Operational Optimization Hub")
    st.markdown(f"Autonomous multi-agent orchestration console monitoring product telemetry for **{selected_product_name}** ({product_id}).")
    st.markdown("---")

    # Kritik Stok Bildirimleri
    kritik_urunler_df = sql_query_to_dataframe("SELECT Urun_Adi, Kalan_Stok FROM products WHERE Kalan_Stok < 60")
    if not kritik_urunler_df.empty:
        st.subheader("🚨 Critical Operational Alerts (Proactive Supply Chain Control)")
        for _, row in kritik_urunler_df.iterrows():
            st.warning(
                f"⚠️ **CRITICAL INVENTORY DEFICIT:** **{row['Urun_Adi']}** stok seviyesi tehlike eşiğinin altına düşmüştür! "
                f"Güncel Depo Havuzu: **{row['Kalan_Stok']} Adet**. Acilen tedarik zincirini tetikleyin."
            )
        st.markdown("---")

    # 1. Metrik Panosu: Yerel Dükkan Metrikleri
    st.subheader("🏬 Local Inventory Performance Metrics")
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

    # 🚨 2. YENİ METRİK PANOSU: PAZAR REKABET İSTİHBARATI
    st.subheader("📡 Real-Time Market Intelligence & Competitor Matrix")
    p_col1, p_col2, p_col3, p_col4 = st.columns(4)
    with p_col1:
        st.metric(label="🏢 Competitor A Price", value=f"{rakip_a_fiyati} TL")
    with p_col2:
        st.metric(label="🏪 Competitor B Price", value=f"{rakip_b_fiyati} TL")
    with p_col3:
        st.metric(label="📊 Market Average Benchmark", value=f"{round(pazar_ortalamasi, 2)} TL")
    with p_col4:
        # Bizim fiyatımızın piyasa ortalamasına göre farkını hesaplayıp duyarlı delta basıyoruz
        fiyat_farki = mevcut_fiyat - pazar_ortalamasi
        delta_label = f"{round(abs(fiyat_farki), 2)} TL " + ("Below Market" if fiyat_farki < 0 else "Above Market")
        st.metric(label="⚖️ Market Position Index", value="Competitive" if abs(fiyat_farki) < (pazar_ortalamasi * 0.05) else "Aggressive", delta=delta_label, delta_color="normal" if fiyat_farki <= 0 else "inverse")

    st.markdown("<br>", unsafe_allow_html=True)

    # Grafikler ve Ajan Alanı
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
                    "lineStyle": {"color": "#5470c6", "width": 3}
                },
                {
                    "name": "Demand Momentum",
                    "type": "line",
                    "smooth": True,
                    "yAxisIndex": 1,
                    "data": [int(talep_skoru*0.5), int(talep_skoru*0.7), int(talep_skoru*0.9), talep_skoru, int(talep_skoru*1.1), int(talep_skoru*0.95), talep_skoru],
                    "lineStyle": {"color": "#91cc75", "width": 3}
                }
            ],
        }
        st_echarts(options=options, height="350px")

    with layout_col2:
        st.subheader("🔮 Autonomous Agent Consensus Room")
        
        if "last_selected_product" not in st.session_state or st.session_state.last_selected_product != selected_product_name:
            st.session_state.last_selected_product = selected_product_name
            st.session_state.is_pending = False

        if not st.session_state.is_pending:
            with st.spinner(f"🕵️‍♂️ Ajanlar arası otonom pazar ve rekabet tartışması başlatılıyor..."):
                genel_rapor = run_data_scientist_agent()
                st.session_state.ai_pricing_recommendations = calculate_dynamic_pricing()
                mali_rapor = run_financial_agent(stok_ajani_yorumu=genel_rapor)
                
                from google import genai
                from google.genai.errors import ClientError, ServerError
                
                try:
                    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
                    filter_prompt = f"""
                    Sana bir veri bilimci ve bir finans ajanının ortak tartışma raporları verildi.
                    Senden isteğim, bu raporlardan SADECE ve YALNIZCA '{selected_product_name} ({product_id})' ürünü ile ilgili kısımları ayıklayıp sunmandır.
                    Veri Bilimci Raporu: {genel_rapor}
                    Finans Raporu: {mali_rapor}
                    """
                    response = client.models.generate_content(model='gemini-2.5-flash', contents=filter_prompt)
                    st.session_state.inventory_insight = response.text
                    st.session_state.financial_insight = mali_rapor
                    st.session_state.is_pending = True
                except (ClientError, ServerError):
                    st.session_state.is_pending = True
                    st.session_state.inventory_insight = "⚠️ Yerel emniyet modu aktif."

        tab1, tab2 = st.tabs(["🤝 Executive Consensus", "📊 Raw CFO Log"])
        with tab1:
            st.info(st.session_state.inventory_insight)
        with tab2:
            st.caption(st.session_state.financial_insight)
        
        proposed_ui_price = mevcut_fiyat
        if st.session_state.ai_pricing_recommendations:
            for item in st.session_state.ai_pricing_recommendations:
                if item["Urun_ID"] == product_id:
                    proposed_ui_price = item["Onerilen_Yeni_Fiyat"]
                    
        st.metric(label="🎯 System Optimization Price Target", value=f"{proposed_ui_price} TL")

    st.markdown("---")

    # HITL Enterprise Gateway
    st.subheader("🤝 Human-in-the-Loop Strategic Authorization Deck")
    onay_col1, onay_col2, _ = st.columns([1.5, 1.5, 4])

    with onay_col1:
        if st.button("🚀 Authorize & Deploy to Store", use_container_width=True, type="primary"):
            if st.session_state.ai_pricing_recommendations:
                for rec in st.session_state.ai_pricing_recommendations:
                    if rec['Urun_ID'] == product_id:
                        sql_execute_command(
                            """INSERT INTO audit_logs (Urun_ID, Islem_Turu, Eski_Deger, Yeni_Deger) 
                               VALUES (?, 'FIYAT_GUNCELLEME', ?, ?)""",
                            (product_id, mevcut_fiyat, rec['Onerilen_Yeni_Fiyat'])
                        )
                        sql_execute_command(
                            "UPDATE products SET Mevcut_Fiyat = ? WHERE Urun_ID = ?",
                            (rec['Onerilen_Yeni_Fiyat'], rec['Urun_ID'])
                        )
            
            gateway_service = ECommerceGateway()
            with st.spinner("Synchronizing prices..."):
                api_success = gateway_service.sync_product_price(product_id, proposed_ui_price)
                
            if api_success:
                st.toast(f"Strategy deployed!", icon="🚀")
                st.balloons()
            st.session_state.is_pending = False
            st.rerun()

    with onay_col2:
        if st.button("❌ Dismiss Recommendations", use_container_width=True):
            st.toast("Pricing updates dropped.", icon="🛑")
            st.session_state.is_pending = False
            st.rerun()

    # Log Analitiği Paneli
    st.markdown("---")
    st.subheader("📊 System Telemetry & Audit Logs Analytics")
    telemetry_col1, telemetry_col2 = st.columns([2, 3])

    with telemetry_col1:
        st.markdown("#### 🥧 Log Operations Distribution")
        log_counts_df = sql_query_to_dataframe("SELECT Islem_Turu, COUNT(*) as Toplam FROM audit_logs GROUP BY Islem_Turu")
        if not log_counts_df.empty:
            pie_data = [{"value": int(row['Toplam']), "name": str(row['Islem_Turu'])} for _, row in log_counts_df.iterrows()]
            pie_options = {
                "tooltip": {"trigger": "item"},
                "legend": {"top": "5%", "left": "center"},
                "series": [{"name": "Transaction", "type": "pie", "radius": ["40%", "70%"], "data": pie_data}]
            }
            st_echarts(pie_options, height="300px")

    with telemetry_col2:
        st.markdown("#### 📜 Live System Activity Log Stream")
        recent_logs_df = sql_query_to_dataframe("SELECT Log_ID, Urun_ID, Islem_Turu, Eski_Deger, Yeni_Deger, Zaman_Damgasi FROM audit_logs ORDER BY Zaman_Damgasi DESC LIMIT 5")
        if not recent_logs_df.empty:
            st.dataframe(recent_logs_df, use_container_width=True, hide_index=True)