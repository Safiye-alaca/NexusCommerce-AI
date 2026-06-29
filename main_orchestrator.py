import time
import pandas as pd
from data_scientist_agent import run_data_scientist_agent
from financial_agent import run_financial_agent
from pricing_strategy import calculate_dynamic_pricing

def run_nexus_commerce_ai_system():
    print("==================================================")
    print(f"🚀 NexusCommerce AI: ETKİLEŞİMLİ ÇOKLU AJAN SİSTEMİ BAŞLATILIYOR")
    print("==================================================")
    time.sleep(1)
    
    # 1. AŞAMA: Stok Ajanı Analizi
    print("\n[ORKESTRATOR] >> 1. Aşama: Stok ve Talep Tahmin Ajanı çağrılıyor...")
    print("-" * 60)
    stok_raporu_metni = run_data_scientist_agent()
    time.sleep(1) 
    
    # 2. AŞAMA: Finans Ajanı Analizi
    print("\n[ORKESTRATOR] >> 2. Aşama: Finans Direktörü (CFO) Ajanı çağrılıyor...")
    print("-" * 60)
    run_financial_agent(stok_ajani_yorumu=stok_raporu_metni)
    time.sleep(1)

    # 3. AŞAMA: HUMAN-IN-THE-LOOP (KULLANICI ONAY MEKANIZMASI)
    print("\n==================================================")
    print("🎯 [ORKESTRATOR] 3. Aşama: İnsan Onay Mekanizması (HITL) Devreye Girdi")
    print("==================================================")
    
    # Önerilen fiyatları arka plandaki motorumuzdan ham liste olarak alıyoruz
    onerilen_fiyatlar = calculate_dynamic_pricing()
    
    print("\n💰 Ajanların Önerdiği Yeni Fiyat Listesi:")
    for o in onerilen_fiyatlar:
        print(f"📦 {o['Urun_Adi']}: {o['Eski_Fiyat']} TL -> 🔥 {o['Onerilen_Yeni_Fiyat']} TL (Kar Marjı: {o['Yeni_Kar_Marji_Yuzde']})")
    
    # Kullanıcıya soruyoruz
    secim = input("\n📢 Yapay zeka fiyat önerilerini onaylıyor musunuz ve ikas sistemine yüklensin mi? (E/H): ").strip().upper()
    
    if secim == "E":
        print("\n⚙️ [SİSTEM] Fiyatlar güncelleniyor, veri tabanına (CSV) yazılıyor...")
        
        # CSV dosyasını okuyup fiyatları kalıcı olarak güncelliyoruz
        df = pd.read_csv("ecommerce_data.csv")
        
        for o in onerilen_fiyatlar:
            # En güncel satırdaki fiyatı yeni önerilen fiyatla değiştiriyoruz
            idx = df[df['Urun_ID'] == o['Urun_ID']].index[-1]
            df.at[idx, 'Mevcut_Fiyat'] = o['Onerilen_Yeni_Fiyat']
            
        # Değişiklikleri CSV'ye geri kaydediyoruz
        df.to_csv("ecommerce_data.csv", index=False)
        print("✅ [SİSTEM] Başarılı! Yeni fiyatlar ikas veri tabanına kalıcı olarak işlendi.")
        
    else:
        print("\n❌ [SİSTEM] Güncelleme kullanıcı tarafından reddedildi. Mevcut fiyatlar korundu.")

    print("\n==================================================")
    print("✅ [SİSTEM] Çoklu Ajan Çevrimi Güvenli Bir Şekilde Tamamlandı.")
    print("==================================================")

if __name__ == "__main__":
    run_nexus_commerce_ai_system()