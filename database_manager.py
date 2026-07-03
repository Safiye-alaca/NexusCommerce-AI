import sqlite3
import pandas as pd
import os

DB_FILE = "nexus_store.db"
CSV_FILE = "ecommerce_data.csv"

def init_database():
    """
    Veri tabanını oluşturur ve şemayı (tablo yapısını) hazırlar.
    """
    print("🔮 Veri tabanı başlatılıyor...")
    
    conn = sqlite3.connect(DB_FILE)
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
    
    # 2. 🚨 YENİ: Değişiklik Günlükleri (Audit Logs) Tablosu
    # FOREIGN KEY ile products tablosundaki Urun_ID'ye bağlıyoruz (İlişkisel Veri Tabanı Mantığı)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            Log_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Urun_ID TEXT NOT NULL,
            Islem_Turu TEXT NOT NULL, -- 'FIYAT_GUNCELLEME' veya 'STOK_ENJEKSIYON'
            Eski_Deger REAL,
            Yeni_Deger REAL,
            Zaman_Damgasi DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (Urun_ID) REFERENCES products (Urun_ID)
        )
    """)
    
    conn.commit()
    conn.close()
    print(f"✅ '{DB_FILE}' başarıyla güncellendi. 'audit_logs' tablosu hazır.")

def migrate_csv_to_sql():
    if not os.path.exists(CSV_FILE):
        return
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    df = pd.read_csv(CSV_FILE)
    for _, row in df.iterrows():
        cursor.execute("""
            INSERT OR REPLACE INTO products (Urun_ID, Urun_Adi, Kalan_Stok, Maliyet, Mevcut_Fiyat, Gunluk_Satis)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (str(row['Urun_ID']), str(row['Urun_Adi']), int(row['Kalan_Stok']), float(row['Maliyet']), float(row['Mevcut_Fiyat']), int(row['Gunluk_Satis'])))
        
    conn.commit()
    conn.close()
    print("🚀 Veri göçü kontrol edildi.")

if __name__ == "__main__":
    init_database()
    migrate_csv_to_sql()