import sqlite3
import pandas as pd

DB_FILE = "nexus_store.db" # 🚨 Single Source of Truth - Tek Doğruluk Kaynağımız

# ==========================================
# 1. ADIM: DİNAMİK FİYATLANDIRMA MOTORU (SQL TABANLI)
# ==========================================
def calculate_dynamic_pricing():
    """
    Veri tabanındaki canlı verileri tek bir SQL sorgusuyla çeker,
    stok/talep oranını analiz ederek dinamik fiyatlandırma kararlarını üretir.
    """
    fiyatlandirma_raporu = []
    
    try:
        # 🚨 Artık döngü içinde CSV okumak yok! Tek seferde tüm güncel tabloyu SQL'den alıyoruz.
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute("SELECT Urun_ID, Urun_Adi, Kalan_Stok, Maliyet, Mevcut_Fiyat, Gunluk_Satis FROM products")
        rows = cursor.fetchall()
        conn.close()
        
        for row in rows:
            urun_id, urun_adi, kalan_stok, maliyet, eski_fiyat, gunluk_satis = row
            
            # 7 Günlük Beklenen Satış Hesabı (Mevcut mantığı koruyoruz)
            beklenen_satis_7_gun = gunluk_satis
            
            yeni_fiyat = eski_fiyat
            strateji_nedeni = ""
            
            # ⚠️ Durum 1: Stok Kritik Seviyede ve Talep Yüksekse (Fiyatı Artır - Kârı Maksimize Et)
            # Eğer kalan stok, 7 günlük beklenen satıştan azsa risk vardır
            if kalan_stok < beklenen_satis_7_gun:
                yeni_fiyat = eski_fiyat * 1.08
                strateji_nedeni = "Yüksek talep ve kritik stok azlığı tespiti. Arz-talep dengesi için fiyat %8 artırıldı."
                
            # ⚠️ Durum 2: Stok Çok Fazla ama Satışlar Düşükse (Eriyen Stok İçin İndirim Yap)
            elif kalan_stok > (beklenen_satis_7_gun * 3): # Stok, 3 haftalık satıştan fazlaysa
                potansiyel_indirimli_fiyat = eski_fiyat * 0.90
                if potansiyel_indirimli_fiyat > (maliyet * 1.1): # En az %10 kâr marjını koru
                    yeni_fiyat = potansiyel_indirimli_fiyat
                    strateji_nedeni = "Depo stok fazlalığı tespiti. Stok eritme ve nakit akışı için %10 indirim uygulandı."
                else:
                    strateji_nedeni = "Stok fazla ancak kâr marjı kritik sınırda olduğu için fiyat sabit tutuldu."
                    
            # ⚠️ Durum 3: Her Şey Dengedeyse
            else:
                strateji_nedeni = "Stok ve talep dengeli. Mevcut fiyat kararlılığı korunuyor."
                
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
                "Ugulanan_Strateji": strateji_nedeni
            })
            
    except Exception as e:
        print(f"❌ Fiyatlandırma motoru çalışırken SQL hatası: {str(e)}")
        
    return fiyatlandirma_raporu

# ==========================================
# 2. ADIM: SİSTEMİ TEST ETME
# ==========================================
if __name__ == "__main__":
    print("💰 NexusCommerce AI: Dinamik Fiyatlandırma Motoru (SQL) Çalıştırılıyor...\n")
    oneriler = calculate_dynamic_pricing()
    
    for o in oneriler:
        print(f"📦 Ürün: {o['Urun_Adi']} ({o['Urun_ID']})")
        print(f"   • Maliyet: {o['Maliyet']} TL | Eski Fiyat: {o['Eski_Fiyat']} TL")
        print(f"   • 🔥 Önerilen Yeni Fiyat: {o['Onerilen_Yeni_Fiyat']} TL (Yeni Kâr Marjı: {o['Yeni_Kar_Marji_Yuzde']})")
        print(f"   • 📊 Strateji Nedeni: {o['Ugulanan_Strateji']}")
        print("-" * 60)