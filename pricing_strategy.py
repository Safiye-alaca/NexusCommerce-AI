import sqlite3
import pandas as pd
# 🚨 Yeni merkezi veri tabanı kalkanımızı entegre ediyoruz
from database_manager import sql_query_to_dataframe

# ==========================================
# 1. ADIM: DİNAMİK FİYATLANDIRMA MOTORU (SQL & PAZAR ZEKASI TABANLI)
# ==========================================
def calculate_dynamic_pricing():
    """
    Veri tabanındaki canlı verileri ve rakip fiyat pazar telemetrisini çekerek,
    stok/talep/rakip oranını analiz eder ve dinamik fiyatlandırma kararlarını üretir.
    """
    fiyatlandirma_raporu = []
    
    # Yeni eklediğimiz Rakip_Fiyat_A ve Rakip_Fiyat_B sütunlarını da güvenli fonksiyonla çekiyoruz
    query = "SELECT Urun_ID, Urun_Adi, Kalan_Stok, Maliyet, Mevcut_Fiyat, Gunluk_Satis, Rakip_Fiyat_A, Rakip_Fiyat_B FROM products"
    df = sql_query_to_dataframe(query)
    
    if df.empty:
        return []
        
    for _, row in df.iterrows():
        urun_id = row['Urun_ID']
        urun_adi = row['Urun_Adi']
        kalan_stok = int(row['Kalan_Stok'])
        maliyet = float(row['Maliyet'])
        eski_fiyat = float(row['Mevcut_Fiyat'])
        gunluk_satis = int(row['Gunluk_Satis'])
        rakip_a = float(row['Rakip_Fiyat_A'])
        rakip_b = float(row['Rakip_Fiyat_B'])
        
        # Pazar ortalama rakip fiyatını hesaplıyoruz (Nash Dengesi kontrolü için)
        pazar_ortalama_fiyati = (rakip_a + rakip_b) / 2
        
        beklenen_satis_7_gun = gunluk_satis
        yeni_fiyat = eski_fiyat
        strateji_nedeni = ""
        
        # ⚠️ Durum 1: Stok Kritik Seviyede ve Talep Yüksekse (Fiyatı Artır - Kârı Maksimize Et)
        if kalan_stok < beklenen_satis_7_gun:
            yeni_fiyat = eski_fiyat * 1.08
            strateji_nedeni = "Yüksek talep ve kritik stok azlığı tespiti. Arz-talep dengesi için fiyat %8 artırıldı."
            
            # Pazar Zekası İnce Ayarı: Eğer fiyatı artırdığımızda piyasanın çok üzerine çıkıyorsak törpülüyoruz
            if yeni_fiyat > pazar_ortalama_fiyati * 1.10:
                yeni_fiyat = pazar_ortalama_fiyati * 1.05
                strateji_nedeni += " (Piyasa tavan fiyat bariyerine takıldığı için zam %5 ile sınırlandırıldı.)"
                
        # ⚠️ Durum 2: Stok Çok Fazla ama Satışlar Düşükse (Eriyen Stok İçin İndirim Yap)
        elif kalan_stok > (beklenen_satis_7_gun * 3):
            potansiyel_indirimli_fiyat = eski_fiyat * 0.90
            if potansiyel_indirimli_fiyat > (maliyet * 1.1): # En az %10 kâr marjını koru
                yeni_fiyat = potansiyel_indirimli_fiyat
                strateji_nedeni = "Depo stok fazlalığı tespiti. Stok eritme ve nakit akışı için %10 indirim uygulandı."
                
                # Pazar Zekası İnce Ayarı: Eğer rakipler bizden çok daha ucuzsa rekabet için biraz daha esniyoruz
                if yeni_fiyat > pazar_ortalama_fiyati:
                    yeni_fiyat = min(yeni_fiyat, pazar_ortalama_fiyati * 0.99)
                    strateji_nedeni += " (Yoğun rakip baskısı nedeniyle fiyat pazar ortalamasının altına esnetildi.)"
            else:
                strateji_nedeni = "Stok fazla ancak kâr marjı kritik sınırda olduğu için fiyat sabit tutuldu."
                
        # ⚠️ Durum 3: Stok/Talep Dengeli Ama Fiyat Pazarın Çok Altındaysa (Fiyat Güncelleme Potansiyeli)
        elif eski_fiyat < pazar_ortalama_fiyati * 0.90:
            yeni_fiyat = pazar_ortalama_fiyati * 0.95
            strateji_nedeni = "Stok dengeli fakat piyasaya göre aşırı ucuz satış saptandı. Kâr marjını korumak için pazar ortalamasına yaklaştırıldı."
            
        # ⚠️ Durum 4: Her Şey Dengedeyse
        else:
            strateji_nedeni = "Stok, talep ve rakip fiyatları dengeli. Mevcut fiyat kararlılığı korunuyor."
            
        # 🛡️ MARJ KORUMA VE TABAN FİYAT BARİYERİ (Sıfıra Doğru Yarış Koruması)
        taban_fiyat_limiti = maliyet * 1.10
        if yeni_fiyat < taban_fiyat_limiti:
            yeni_fiyat = taban_fiyat_limiti
            strateji_nedeni = "Algoritma hedefi taban marj sınırının altına düştü! Emniyet zırhı tetiklendi, minimum %10 kâr marjı uygulandı."
            
        # Matematiksel Yuvarlamalar ve Marj Hesapları
        yeni_fiyat = round(yeni_fiyat, 2)
        kar_marji = round(((yeni_fiyat - maliyet) / yeni_fiyat) * 100, 2)
        
        fiyatlandirma_raporu.append({
            "Urun_ID": urun_id,
            "Urun_Adi": urun_adi,
            "Maliyet": maliyet,
            "Eski_Fiyat": eski_fiyat,
            "Onerilen_Yeni_Fiyat": yeni_fiyat,
            "Yeni_Kar_Marji_Yuzde": f"%{kar_marji}",
            "Ugulanan_Strateji": strateji_nedeni,
            "Pazar_Ortalamasi": round(pazar_ortalama_fiyati, 2)
        })
        
    return fiyatlandirma_raporu

# ==========================================
# 2. ADIM: SİSTEMİ TEST ETME
# ==========================================
if __name__ == "__main__":
    print("💰 NexusCommerce AI: Pazar ve Rakip Duyarlı Dinamik Fiyatlandırma Motoru Çalıştırılıyor...\n")
    oneriler = calculate_dynamic_pricing()
    
    for o in oneriler:
        print(f"📦 Ürün: {o['Urun_Adi']} ({o['Urun_ID']})")
        print(f"   • Maliyet: {o['Maliyet']} TL | Eski Fiyat: {o['Eski_Fiyat']} TL | Pazar Ortalaması: {o['Pazar_Ortalamasi']} TL")
        print(f"   • 🔥 Önerilen Yeni Fiyat: {o['Onerilen_Yeni_Fiyat']} TL (Yeni Kâr Marjı: {o['Yeni_Kar_Marji_Yuzde']})")
        print(f"   • 📊 Strateji Nedeni: {o['Ugulanan_Strateji']}")
        print("-" * 60)