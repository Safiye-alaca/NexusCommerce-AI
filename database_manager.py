import os
import sqlite3
import pandas as pd
import streamlit as st

DB_FILE = "nexus_store.db"
CSV_FILE = "ecommerce_data.csv"

# ======================================================================
# 🛡️ 1. GÜVENLİ VERİ TABANI YARDIMCI FONKSİYONLARI (CONTEXT MANAGER & TIMEOUT)
# ======================================================================

def sql_query_to_dataframe(query, params=()):
    """
    Güvenli Context Manager ve Timeout koruması ile SQL sorgusu çalıştırır.
    Hata oluşsa bile bağlantı sızıntısı (Connection Leak) yapmaz.
    """
    try:
        # timeout=10 ile maksimum sabır süresi eklenerek kilitlenmeler önlenir
        with sqlite3.connect(DB_FILE, timeout=10) as conn:
            df = pd.read_sql_query(query, conn, params=params)
            return df
    except sqlite3.OperationalError as e:
        st.error(f"❌ Veri Tabanı Yoğunluk Hatası (Kilitlenme Aşımı): {str(e)}")
        return pd.DataFrame() # Boş DataFrame dönerek uygulamanın çökmesini engeller

def sql_execute_command(command, params=()):
    """
    UPDATE, INSERT gibi veri tabanını değiştiren SQL komutlarını 
    otomatik commit ve güvenli bağlantı kapatma garantisi ile yürütür.
    """
    try:
        with sqlite3.connect(DB_FILE, timeout=10) as conn:
            cursor = conn.cursor()
            cursor.execute(command, params)
            conn.commit() # with bloğu otomatik commit sağlasa da garantiye alıyoruz
    except sqlite3.OperationalError as e:
        # Eğer hata Streamlit arayüzü dışından (örneğin stres testinden) gelirse st.error patlamasın diye kontrol ediyoruz
        try:
            st.error(f"❌ Kritik SQL Komut Yürütme Hatası (Database Locked): {str(e)}")
        except:
            print(f"❌ Kritik SQL Komut Yürütme Hatası (Database Locked): {str(e)}")

# ======================================================================
# 🔮 2. VERI TABANI ILKLENDIRME VE GÖÇ (MIGRATION) SİSTEMİ
# ======================================================================

def init_database():
    """
    Veri tabanını oluşturur ve şemayı (tablo yapısını) hazırlar.
    """
    print("🔮 Veri tabanı başlatılıyor...")
    
    with sqlite3.connect(DB_FILE, timeout=10) as conn:
        cursor = conn.cursor()
        
        # 1. Ürünler Tablosu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                Urun_ID TEXT PRIMARY KEY,
                Urun_Adi TEXT NOT NULL,
                Kalan_Stok INTEGER NOT NULL,
                Maliyet REAL NOT NULL,
                Mevcut_Fiyat REAL NOT NULL,
                Gunluk_Satis INTEGER NOT NULL
            )
        """)
        
        # 2. Değişiklik Günlükleri (Audit Logs) Tablosu
        # FOREIGN KEY ile products tablosundaki Urun_ID'ye bağlıyoruz (İlişkisel Veri Tabanı Mantığı)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                Log_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Urun_ID TEXT NOT NULL,
                Islem_Turu TEXT NOT NULL, -- 'FIYAT_GUNCELLEME', 'STOK_ENJEKSIYON' veya 'STRES_TESTI_YUKU'
                Eski_Deger REAL,
                Yeni_Deger REAL,
                Zaman_Damgasi DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (Urun_ID) REFERENCES products (Urun_ID)
            )
        """)
        
        conn.commit()
    print(f"✅ '{DB_FILE}' başarıyla güncellendi. Şema mimarisi ve koruma katmanları hazır.")

def migrate_csv_to_sql():
    """
    Mevcut bir e-ticaret CSV dosyası varsa verileri SQL veri tabanına göç ettirir.
    """
    if not os.path.exists(CSV_FILE):
        print(f"ℹ️ Göç için '{CSV_FILE}' dosyası bulunamadı. Adım atlanıyor.")
        return
    
    with sqlite3.connect(DB_FILE, timeout=10) as conn:
        cursor = conn.cursor()
        
        df = pd.read_csv(CSV_FILE)
        for _, row in df.iterrows():
            cursor.execute("""
                INSERT OR REPLACE INTO products (Urun_ID, Urun_Adi, Kalan_Stok, Maliyet, Mevcut_Fiyat, Gunluk_Satis)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (str(row['Urun_ID']), str(row['Urun_Adi']), int(row['Kalan_Stok']), float(row['Maliyet']), float(row['Mevcut_Fiyat']), int(row['Gunluk_Satis'])))
            
        conn.commit()
    print("🚀 Veri göçü başarıyla kontrol edildi ve senkronize edildi.")

if __name__ == "__main__":
    init_database()
    migrate_csv_to_sql()