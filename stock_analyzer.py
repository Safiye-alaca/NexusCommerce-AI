import pandas as pd
from demand_forecaster import predict_next_7_days_demand

# ==========================================
# 1. ADIM: MEVCUT STOK DURUMUNU OKUMA
# ==========================================
def get_current_stock_status():
    """
    ikas veri tabanından (yani bizim CSV'den) ürünlerin en son güncel stoklarını çeker.
    """
    df = pd.read_csv("ecommerce_data.csv")
    df['Tarih'] = pd.to_datetime(df['Tarih'])
    
    # En son tarihteki (28 Haziran 2026) stok verilerini filtrele
    en_son_tarih = df['Tarih'].max()
    son_stoklar = df[df['Tarih'] == en_son_tarih]
    
    stok_sozlugu = {}
    for _, row in son_stoklar.iterrows():
        stok_sozlugu[row['Urun_ID']] = {
            "Urun_Adi": row['Urun_Adi'],
            "Mevcut_Stok": int(row['Kalan_Stok']),
            "Mevcut_Fiyat": row['Mevcut_Fiyat']
        }
    return stok_sozlugu

# ==========================================
# 2. ADIM: STOK VE TALEP KARŞILAŞTIRMA MANTIĞI
# ==========================================
def analyze_stock_runout_risk():
    """
    Mevcut stokları, gelecek 7 günlük taleple karşılaştırır ve risk analizi yapar.
    """
    mevcut_stoklar = get_current_stock_status()
    stok_analiz_raporu = []
    
    # Mağazadaki her bir ürünü tek tek incele
    for urun_id, stok_bilgisi in mevcut_stoklar.items():
        # Dün yazdığımız tahmin motorunu çağırıp önümüzdeki 7 günün tahminini alıyoruz
        tahmin_sonucu = predict_next_7_days_demand(urun_id)
        
        mevcut_stok = stok_bilgisi["Mevcut_Stok"]
        toplam_7_gunluk_talep = tahmin_sonucu["Onumuzdeki_7_Gunluk_Toplam_Talep_Tahmini"]
        
        # Karar Mekanizması (İş Mantığı)
        # Eğer depodaki mal, önümüzdeki 7 günün satışı için yetersizse:
        if mevcut_stok < toplam_7_gunluk_talep:
            durum = "KRITIK_STOK_RISKI"
            aciklama = f"Dikkat! Önümüzdeki 7 günde {toplam_7_gunluk_talep} adet satış bekleniyor ancak depoda sadece {mevcut_stok} adet var!"
            stok_yenileme_oneresi = toplam_7_gunluk_talep - mevcut_stok + 50 # Güvenli stok için +50 ekle
        else:
            durum = "STOK_YETERLI"
            aciklama = "Stok seviyesi önümüzdeki 7 günlük talebi karşılamak için güvenli."
            stok_yenileme_oneresi = 0
            
        stok_analiz_raporu.append({
            "Urun_ID": urun_id,
            "Urun_Adi": stok_bilgisi["Urun_Adi"],
            "Mevcut_Stok": mevcut_stok,
            "7_Gunluk_Beklenen_Satis": toplam_7_gunluk_talep,
            "Durum": durum,
            "Mesaj": aciklama,
            "Onerilen_Tedarik_Miktari": stok_yenileme_oneresi
        })
        
    return stok_analiz_raporu

# ==========================================
# 3. ADIM: SİSTEMİ ÇALIŞTIRMA VE GÖRSELLEŞTİRME
# ==========================================
if __name__ == "__main__":
    print("🔍 NexusCommerce AI: Mağaza Stok Risk Analizi Başlatılıyor...\n")
    rapor = analyze_stock_runout_risk()
    
    for urun in rapor:
        print(f"📦 Ürün: {urun['Urun_Adi']} ({urun['Urun_ID']})")
        print(f"   • Depodaki Stok: {urun['Mevcut_Stok']} adet")
        print(f"   • 7 Günlük Tahmini Satış: {urun['7_Gunluk_Beklenen_Satis']} adet")
        
        if urun['Durum'] == "KRITIK_STOK_RISKI":
            print(f"   🚨 DURUM: {urun['Durum']}")
            print(f"   💡 ÖNERİ: Tedarikçiden acilen en az {urun['Onerilen_Tedarik_Miktari']} adet sipariş verin!")
        else:
            print(f"   ✅ DURUM: {urun['Durum']}")
            
        print(f"   💬 Analiz: {urun['Mesaj']}")
        print("-" * 60)