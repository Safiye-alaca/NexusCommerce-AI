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
    
    # Veri tabanına bağlanır (Dosya yoksa otomatik oluşturulur)
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # 1. Tablo Oluşturma (SQL Diliyle)
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
    
    conn.commit()
    conn.close()
    print(f"✅ '{DB_FILE}' başarıyla oluşturuldu ve 'products' tablosu hazırlandı.")

def migrate_csv_to_sql():
    """
    Eski bakkal defterindeki (CSV) verileri güvenli dijital arşive (SQL) taşır.
    """
    if not os.path.exists(CSV_FILE):
        print(f"❌ HATA: Göç için '{CSV_FILE}' dosyası bulunamadı!")
        return

    print(f"📦 '{CSV_FILE}' içerisindeki veriler SQL'e göç ettiriliyor...")
    
    # CSV dosyasını Pandas ile oku
    df = pd.read_csv(CSV_FILE)
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Verileri SQL tablosuna güvenle yaz (Tekrarlanmayı önlemek için INSERT OR REPLACE)
    for _, row in df.iterrows():
        cursor.execute("""
            INSERT OR REPLACE INTO products (Urun_ID, Urun_Adi, Kalan_Stok, Maliyet, Mevcut_Fiyat, Gunluk_Satis)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            str(row['Urun_ID']),
            str(row['Urun_Adi']),
            int(row['Kalan_Stok']),
            float(row['Maliyet']),
            float(row['Mevcut_Fiyat']),
            int(row['Gunluk_Satis'])
        ))
        
    conn.commit()
    conn.close()
    print("🚀 Veri göçü (Migration) başarıyla tamamlandı! Tüm veriler artık SQL içinde.")

# Dosya doğrudan çalıştırıldığında tetiklenecek kurumsal mekanizma
if __name__ == "__main__":
    init_database()
    migrate_csv_to_sql()