import pandas as pd
from stock_analyzer import analyze_stock_runout_risk

# ==========================================
# 1. ADIM: DİNAMİK FİYATLANDIRMA MOTORU
# ==========================================
def calculate_dynamic_pricing():
    """
    Stok risk raporunu ve gelecek talep tahminlerini analiz ederek
    her ürün için optimize edilmiş yeni bir fiyat önerisi üretir.
    """
    # 4. günden gelen güncel stok ve talep analiz raporunu alıyoruz
    stok_raporu = analyze_stock_runout_risk()
    fiyatlandirma_raporu = []
    
    for urun in stok_raporu:
        urun_id = urun["Urun_ID"]
        urun_adi = urun["Urun_Adi"]
        mevcut_stok = urun["Mevcut_Stok"]
        beklenen_satis = urun["7_Gunluk_Beklenen_Satis"]
        
        # Orijinal maliyet ve fiyat bilgilerini çekmek için CSV'den en son satırı okuyoruz
        df = pd.read_csv("ecommerce_data.csv")
        son_satir = df[df['Urun_ID'] == urun_id].iloc[-1]
        maliyet = float(son_satir['Maliyet'])
        eski_fiyat = float(son_satir['Mevcut_Fiyat'])
        
        # ⚠️ MÜHENDİSLİK TİCARİ KURALLARI (Business Rules)
        yeni_fiyat = eski_fiyat
        strateji_nedeni = ""
        
        # Durum 1: Stok Kritik Seviyede ve Talep Yüksekse (Fiyatı Artır - Kârı Maksimize Et)
        if urun["Durum"] == "KRITIK_STOK_RISKI":
            # Ürün bitmek üzere, talebi frenlemek ve daha yüksek kâr etmek için %8 zam yap
            yeni_fiyat = eski_fiyat * 1.08
            strateji_nedeni = "Yüksek talep ve kritik stok azlığı tespiti. Arz-talep dengesi için fiyat %8 artırıldı."
            
        # Durum 2: Stok Çok Fazla ama Satışlar Düşükse (Eriyen Stok İçin İndirim Yap)
        elif mevcut_stok > (beklenen_satis * 3): # Stok, 3 haftalık satıştan fazlaysa
            # Depoda mal kalmasın diye %10 indirim yap ama asla maliyetin altına inme!
            potansiyel_indirimli_fiyat = eski_fiyat * 0.90
            if potansiyel_indirimli_fiyat > (maliyet * 1.1): # En az %10 kâr marjını koru
                yeni_fiyat = potansiyel_indirimli_fiyat
                strateji_nedeni = "Depo stok fazlalığı tespiti. Stok eritme ve nakit akışı için %10 indirim uygulandı."
            else:
                strateji_nedeni = "Stok fazla ancak kâr marjı kritik sınırda olduğu için fiyat sabit tutuldu."
                
        # Durum 3: Her Şey Dengedeyse
        else:
            strateji_nedeni = "Stok ve talep dengeli. Mevcut fiyat kararlılığı korunuyor."
            
        # Fiyatı kuruşlardan kurtarmak için yuvarla
        yeni_fiyat = round(yeni_fiyat, 2)
        kar_marji = round(((yeni_fiyat - maliyet) / yeni_fiyat) * 100, 2)
        
        fiyatlandirma_raporu.append({
            "Urun_ID": urun_id,
            "Urun_Adi": urun_adi,
            "Maliyet": maliyet,
            "Eski_Fiyat": eski_fiyat,
            "Onerilen_Yeni_Fiyat": yeni_fiyat,
            "Yeni_Kar_Marji_Yuzde": f"%{kar_marji}",
            "Ugulanan_Strateji": strateji_nedeni
        })
        
    return fiyatlandirma_raporu

# ==========================================
# 2. ADIM: SİSTEMİ TEST ETME
# ==========================================
if __name__ == "__main__":
    print("💰 NexusCommerce AI: Dinamik Fiyatlandırma Motoru Çalıştırılıyor...\n")
    oneriler = calculate_dynamic_pricing()
    
    for o in oneriler:
        print(f"📦 Ürün: {o['Urun_Adi']} ({o['Urun_ID']})")
        print(f"   • Maliyet: {o['Maliyet']} TL | Eski Fiyat: {o['Eski_Fiyat']} TL")
        print(f"   • 🔥 Önerilen Yeni Fiyat: {o['Onerilen_Yeni_Fiyat']} TL (Yeni Kâr Marjı: {o['Yeni_Kar_Marji_Yuzde']})")
        print(f"   • 📊 Strateji Nedeni: {o['Ugulanan_Strateji']}")
        print("-" * 60)