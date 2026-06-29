import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# ==========================================
# 1. BÖLÜM: ZAMAN EKSENİNİ KURMAK
# ==========================================
# Bugünün tarihi: 28 Haziran 2026. 1 yıl geriye gidiyoruz.
bitis_tarihi = datetime(2026, 6, 28)
baslangic_tarihi = bitis_tarihi - timedelta(days=364)
tarihler = pd.date_range(start=baslangic_tarihi, end=bitis_tarihi, freq='D')

# ==========================================
# 2. BÖLÜM: ÜRÜN SENARYOLARINI TANIMLAMAK
# ==========================================
urunler = {
    "URUN_001": {"isim": "Deri Ceket", "maliyet": 1000, "fiyat": 1800, "baslangic_stok": 50},
    "URUN_002": {"isim": "Bez Çanta", "maliyet": 150, "fiyat": 350, "baslangic_stok": 150},
    "URUN_003": {"isim": "Beyaz Tişört", "maliyet": 200, "fiyat": 450, "baslangic_stok": 120}
}

# Tüm satırları biriktireceğimiz liste
veri_listesi = []

# ==========================================
# 3. BÖLÜM: SİMÜLASYON VE DÖNGÜ MANTIĞI
# ==========================================
# Her bir ürün için gün gün stok takibi yapabilmek adına mevcut stokları kopyalıyoruz
guncel_stoklar = {urun_id: urunler[urun_id]["baslangic_stok"] for urun_id in urunler}

for tarih in tarihler:
    # Hafta sonu kontrolü (5 = Cumartesi, 6 = Pazar)
    is_weekend = tarih.weekday() >= 5
    
    for urun_id, ozellikler in urunler.items():
        # Ürüne özel satış karakteri belirleme (Gürültü - Noise ekleme)
        if urun_id == "URUN_001":  # Deri Ceket az satılır
            satis = np.random.randint(2, 6) if is_weekend else np.random.randint(0, 3)
        elif urun_id == "URUN_002":  # Bez Çanta orta satılır
            satis = np.random.randint(8, 15) if is_weekend else np.random.randint(3, 9)
        else:  # Beyaz Tişört çok satılır (Sürüm ürünü)
            satis = np.random.randint(12, 22) if is_weekend else np.random.randint(5, 13)
            
        # Satışın eldeki stoktan fazla olmamasını garanti edelim
        satis = min(satis, guncel_stoklar[urun_id])
        
        # Gün sonu stoğunu hesapla
        guncel_stoklar[urun_id] -= satis
        
        # OTOMATİK STOK YENİLEME 
        # Stok kritik seviyeye (10'a) düştüyse depoya yeni mal girsin
        stok_yenilendi_mi = 0
        if guncel_stoklar[urun_id] <= 10:
            guncel_stoklar[urun_id] += 100  # Depoya 100 adet yeni ürün eklendi
            stok_yenilendi_mi = 1
            
        # Oluşan günlük veriyi listeye ekle
        veri_listesi.append({
            "Tarih": tarih.strftime('%Y-%m-%d'),
            "Urun_ID": urun_id,
            "Urun_Adi": ozellikler["isim"],
            "Maliyet": ozellikler["maliyet"],
            "Mevcut_Fiyat": ozellikler["fiyat"],
            "Gunluk_Satis": satis,
            "Kalan_Stok": guncel_stoklar[urun_id],
            "Stok_Yenileme_Tetiklendi": stok_yenilendi_mi
        })

# ==========================================
# 4. BÖLÜM: VERİYİ KAYDETME VE KONTROL
# ==========================================
df = pd.DataFrame(veri_listesi)
df.to_csv("ecommerce_data.csv", index=False)

print("✅ NexusCommerce AI için 1 yıllık Mock Veri Seti başarıyla üretildi!")
print(f"📊 Toplam Satır Sayısı: {len(df)}")
print("\n--- İlk 5 Satıra Göz Atalım ---")
print(df.head())