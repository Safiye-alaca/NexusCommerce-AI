import pandas as pd
import numpy as np
import joblib
from datetime import datetime, timedelta

# ==========================================
# 1. ADIM: KAYDEDİLEN MODELİ VE VERİYİ YÜKLEME
# ==========================================
try:
    model = joblib.load("demand_model.joblib")
    df_historical = pd.read_csv("ecommerce_data.csv")
    df_historical['Tarih'] = pd.to_datetime(df_historical['Tarih'])
except FileNotFoundError:
    print("❌ Hata: Önce 'train_demand_agent.py' kodunu çalıştırıp modeli kaydetmelisiniz!")
    exit()

# ==========================================
# 2. ADIM: AJANIN KULLANACAĞI TAHMİN FONKSİYONU
# ==========================================
def predict_next_7_days_demand(urun_id: str):
    """
    Bu fonksiyon, projenin ilerleyen günlerinde LLM (Ajan) tarafından tetiklenecek.
    Verilen ürün ID'sine göre önümüzdeki 7 günün talep tahminini çıkarır.
    """
   # Filtreleme ve sıralamayı birbirinden tamamen bağımsız iki adımda güvenle yapıyoruz:
    urun_verisi = df_historical[df_historical['Urun_ID'] == urun_id].copy()
    urun_verisi = urun_verisi.sort_values('Tarih')
    
    if urun_verisi.empty:
        return {"hata": f"Mağazada {urun_id} kodlu bir ürün bulunamadı."}
    
    # En son satış verilerini ve ürün özelliklerini al
    son_satir = urun_verisi.iloc[-1]
    urun_adi = son_satir['Urun_Adi']
    mevcut_fiyat = son_satir['Mevcut_Fiyat']
    
    # Simülasyonun bittiği tarihten (28 Haziran 2026) ileriye doğru 7 gün oluştur
    baslangic_tarihi = datetime(2026, 6, 29)
    gelecek_tarihler = pd.date_range(start=baslangic_tarihi, periods=7, freq='D')
    
    tahmin_raporu = []
    
    # Modelin geçmiş satış hafızasını (Lag) başlatmak için son 2 günün satışını alıyoruz
    g1 = urun_verisi.iloc[-1]['Gunluk_Satis']
    g2 = urun_verisi.iloc[-2]['Gunluk_Satis']
    
    # 7 gün boyunca döngüsel olarak tahmin üret (Hafızalı Tahmin)
    for tarih in gelecek_tarihler:
        haftanin_gunu = tarih.weekday()
        ay = tarih.month
        is_weekend = 1 if haftanin_gunu >= 5 else 0
        
        # Modelin beklediği formatta girdiyi (Feature Vector) hazırla
        girdi_verisi = pd.DataFrame([{
            'Haftanin_Gunu': haftanin_gunu,
            'Ay': ay,
            'Is_Weekend': is_weekend,
            'Mevcut_Fiyat': mevcut_fiyat,
            'Gecmis_Satis_1_Gun_Once': g1,
            'Gecmis_Satis_2_Gun_Once': g2
        }])
        
        # Modeli kullanarak o günkü satışı tahmin et
        tahmin_satis = model.predict(girdi_verisi)[0]
        # Satış adedi eksi çıkamayacağı için 0 ile sınırla ve tam sayıya yuvarla
        tahmin_satis = max(0, int(round(tahmin_satis)))
        
        tahmin_raporu.append({
            "Tarih": tarih.strftime('%Y-%m-%d'),
            "Tahmini_Satis": tahmin_satis
        })
        
        # ZİNCİRLEME TAHMİN MANTIĞI:
        # Yarın tahmin yaparken, bugünün tahmini artık dünün satışı (g1) olacak.
        g2 = g1
        g1 = tahmin_satis

    total_predicted_demand = sum([gun["Tahmini_Satis"] for gun in tahmin_raporu])
    
    return {
        "Urun_ID": urun_id,
        "Urun_Adi": urun_adi,
        "Onumuzdeki_7_Gunluk_Toplam_Talep_Tahmini": total_predicted_demand,
        "Gunluk_Detaylar": tahmin_raporu
    }

# ==========================================
# 3. ADIM: SİSTEMİ TEST ETME (BEYAZ TİŞÖRT İÇİN)
# ==========================================
if __name__ == "__main__":
    print("🤖 Stok ve Talep Tahmin Ajanı: 'URUN_003' (Beyaz Tişört) için gelecek analizi yapıyor...\n")
    sonuc = predict_next_7_days_demand("URUN_003")
    
    print(f"📦 Ürün: {sonuc['Urun_Adi']} ({sonuc['Urun_ID']})")
    print(f"📈 Önümüzdeki 7 günde beklenen toplam satış: {sonuc['Onumuzdeki_7_Gunluk_Toplam_Talep_Tahmini']} adet.\n")
    print("📅 Günlük Tahmin Dağılımı:")
    for gun in sonuc['Gunluk_Detaylar']:
        print(f"  • {gun['Tarih']}: {gun['Tahmini_Satis']} adet satış bekleniyor.")