import sqlite3
import concurrent.futures
import time
import random

DB_FILE = "nexus_store.db"

def simulate_concurrent_write(thread_id):
    """
    Her bir thread'in aynı anda veri tabanına hem UPDATE hem de INSERT 
    yaparak yoğun yük bindirdiği simülasyon fonksiyonu.
    """
    print(f"🚀 Thread-{thread_id} başlatıldı, veri tabanına saldırmaya hazırlanıyor...")
    
    # Simülasyon çeşitliliği için rastgele değerler üretiyoruz
    simule_stok = random.randint(10, 500)
    simule_talep = random.randint(5, 150)
    
    start_time = time.time()
    
    try:
        # app.py içindeki zırhlı mimarinin aynısını (timeout=10) kullanıyoruz
        with sqlite3.connect(DB_FILE, timeout=10) as conn:
            cursor = conn.cursor()
            
            # 1. Adım: products tablosunda URUN_001 stok ve talebini güncelle (UPDATE)
            cursor.execute(
                "UPDATE products SET Kalan_Stok = ?, Gunluk_Satis = ? WHERE Urun_ID = 'URUN_001'",
                (simule_stok, simule_talep)
            )
            
            # 2. Adım: audit_logs tablosuna bu stres testi işlemini kaydet (INSERT)
            cursor.execute(
                """INSERT INTO audit_logs (Urun_ID, Islem_Turu, Eski_Deger, Yeni_Deger) 
                   VALUES ('URUN_001', 'STRES_TESTI_YUKU', ?, ?)""",
                (thread_id, simule_stok)
            )
            
            conn.commit()
            
        end_time = time.time()
        duration = round(end_time - start_time, 4)
        print(f"✅ Thread-{thread_id} görevini BAŞARIYLA tamamlama süresi: {duration} saniye.")
        return True

    except sqlite3.OperationalError as e:
        print(f"❌ Thread-{thread_id} KİLİTLENME HATASINA DÜŞTÜ: {str(e)}")
        return False

def run_heavy_stress_test():
    """
    ThreadPoolExecutor kullanarak 20 adet eş zamanlı thread'i 
    aynı anda veri tabanına gönderir.
    """
    print("🔥 NexusCommerce AI: Veri Tabanı Yoğun Yük ve Stres Testi Başlatılıyor...\n")
    print("----------------------------------------------------------------------")
    
    global_start = time.time()
    
    # 20 adet eş zamanlı iş parçacığı tetikliyoruz
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(simulate_concurrent_write, i) for i in range(1, 21)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
    global_end = time.time()
    
    başarılı_islemler = results.count(True)
    hatalı_islemler = results.count(False)
    
    print("----------------------------------------------------------------------")
    print("📊 STRES TESTİ NİHAİ RAPORU")
    print("----------------------------------------------------------------------")
    print(f"🔹 Toplam Gönderilen Eş Zamanlı İstek: 20")
    print(f"🔹 Başarıyla Veri Tabanına İşlenen: {başarılı_islemler}")
    print(f"🔹 Hata Alıp Çöken İşlem Sayısı: {hatalı_islemler}")
    print(f"🔹 Toplam Test Süresi: {round(global_end - global_start, 4)} saniye.")
    print("----------------------------------------------------------------------")

if __name__ == "__main__":
    run_heavy_stress_test()