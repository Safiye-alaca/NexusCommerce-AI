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
        with sqlite3.connect(DB_FILE, timeout=10) as conn:
            df = pd.read_sql_query(query, conn, params=params)
            return df
    except sqlite3.OperationalError as e:
        st.error(f"❌ Veri Tabanı Yoğunluk Hatası (Kilitlenme Aşımı): {str(e)}")
        return pd.DataFrame()

def sql_execute_command(command, params=()):
    """
    UPDATE, INSERT gibi veri tabanını değiştiren SQL komutlarını 
    otomatik commit ve güvenli bağlantı kapatma garantisi ile yürütür.
    """
    try:
        with sqlite3.connect(DB_FILE, timeout=10) as conn:
            cursor = conn.cursor()
            cursor.execute(command, params)
            conn.commit()
    except sqlite3.OperationalError as e:
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
    🚨 GÜNCELLEME: Rakip fiyat sütunları (Pazar Telemetrisi) eklendi.
    """
    print("🔮 Veri tabanı başlatılıyor...")
    
    with sqlite3.connect(DB_FILE, timeout=10) as conn:
        cursor = conn.cursor()
        
        # 1. Ürünler Tablosu (Pazar Zekası Sütunları Dahil Edildi)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                Urun_ID TEXT PRIMARY KEY,
                Urun_Adi TEXT NOT NULL,
                Kalan_Stok INTEGER NOT NULL,
                Maliyet REAL NOT NULL,
                Mevcut_Fiyat REAL NOT NULL,
                Gunluk_Satis INTEGER NOT NULL,
                Rakip_Fiyat_A REAL DEFAULT 0.0, -- Rakip A Mağazası Fiyatı
                Rakip_Fiyat_B REAL DEFAULT 0.0  -- Rakip B Mağazası Fiyatı
            )
        """)
        
        # 2. Değişiklik Günlükleri (Audit Logs) Tablosu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                Log_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Urun_ID TEXT NOT NULL,
                Islem_Turu TEXT NOT NULL, 
                Eski_Deger REAL,
                Yeni_Deger REAL,
                Zaman_Damgasi DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (Urun_ID) REFERENCES products (Urun_ID)
            )
        """)
        
        conn.commit()
    print(f"✅ '{DB_FILE}' başarıyla güncellendi. Pazar istihbarat mimarisi hazır.")

def migrate_csv_to_sql():
    """
    Mevcut bir e-ticaret CSV dosyası varsa verileri SQL veri tabanına göç ettirir.
    Rakip fiyatlarını otomatik simüle ederek pazar verilerini doldurur.
    """
    if not os.path.exists(CSV_FILE):
        print(f"ℹ️ Göç için '{CSV_FILE}' dosyası bulunamadı. Adım atlanıyor.")
        return
    
    with sqlite3.connect(DB_FILE, timeout=10) as conn:
        cursor = conn.cursor()
        
        df = pd.read_csv(CSV_FILE)
        for _, row in df.iterrows():
            mevcut_fiyat = float(row['Mevcut_Fiyat'])
            
            # Pazar simülasyonu: Rakiplerin fiyatlarını bizim fiyatımıza yakın mantıklı değerler atıyoruz
            rakip_a = round(mevcut_fiyat * 1.05, 2) # %5 pahalı
            rakip_b = round(mevcut_fiyat * 0.97, 2) # %3 ucuz (tehlikeli rakip)
            
            cursor.execute("""
                INSERT OR REPLACE INTO products (Urun_ID, Urun_Adi, Kalan_Stok, Maliyet, Mevcut_Fiyat, Gunluk_Satis, Rakip_Fiyat_A, Rakip_Fiyat_B)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (str(row['Urun_ID']), str(row['Urun_Adi']), int(row['Kalan_Stok']), float(row['Maliyet']), mevcut_fiyat, int(row['Gunluk_Satis']), rakip_a, rakip_b))
            
        conn.commit()
    print("🚀 Veri göçü ve pazar veri simülasyonu başarıyla tamamlandı.")

if __name__ == "__main__":
    # Eğer eski kısıtlı db varsa sütunların temiz eklenmesi için silip sıfırdan kuruyoruz
    if os.path.exists(DB_FILE):
        try:
            os.remove(DB_FILE)
        except:
            pass
    init_database()
    migrate_csv_to_sql()