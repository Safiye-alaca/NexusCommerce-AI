import os
import json
from google import genai
from google.genai import types
from google.genai.errors import ClientError, ServerError # Çift Katmanlı Hata Kalkanı Korundu
from pricing_strategy import calculate_dynamic_pricing
from dotenv import load_dotenv

# .env dosyasını sisteme yükle
load_dotenv()

GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")

# API Anahtarı kontrolü
if not GOOGLE_API_KEY:
    raise ValueError("❌ HATA: .env dosyasından GEMINI_API_KEY okunamadı!")

client = genai.Client(api_key=GOOGLE_API_KEY)

def run_financial_agent(stok_ajani_yorumu=""):
    print("🤖 Finans Ajanı (Gemini v2) yeni pazar fiyatlarını ve kâr marjlarını analiz ediyor...\n")
    
    # pricing_strategy artık pazar ve rakip ortalamalarını da barındıran güncel canlı veriyi döner
    fiyat_raporu = calculate_dynamic_pricing()
    fiyat_raporu_metni = json.dumps(fiyat_raporu, ensure_ascii=False, indent=2)
    
    # 🚨 PROMPT UPGRADE: Sistem talimatını Oyun Teorisi, Nash Dengesi ve Fiyat Savaşı Korumasına göre genişletiyoruz
    system_instruction = f"""
    Sen NexusCommerce AI sisteminin kıdemli Finans Direktörü (CFO) ve Dinamik Fiyatlandırma Stratejistisin.
    Görevin, sana verilen pazar duyarlı dinamik fiyatlandırma önerilerini incelemek ve mağaza sahibine finansal bir özet sunmaktır.
    
    Finansal Analiz Kuralların:
    1. Önerilen yeni fiyatların dükkanın kâr marjını koruyup korumadığını maliyet tabanına göre denetle.
    2. Rakiplerin fiyat ortalamalarını (Pazar_Ortalamasi) göz önünde bulundurarak, mağazanın pazar payını kaybetmeyeceği rasyonel fiyat dengeleri (Nash Dengesi) kur.
    3. Yıkıcı fiyat savaşlarından (Price War) kaçınmak adına, algoritmanın emniyet bariyerlerini (maliyet alt sınırlarını) finansal açıdan yorumla.
    
    Arka Plan Bilgisi: Sana dükkanın finansal verileriyle birlikte, Stok ve Pazar Analitiği Ajanımızın yazdığı Türkçe rapor da verilmiştir. 
    Kararlarını ve finansal gerekçelerini açıklarken bu rapordaki lojistik ve rakip uyarılarını da göz önünde bulundur.
    
    Stok ve Pazar Ajanından Gelen Türkçe Rapor:
    ---------------------------------
    {stok_ajani_yorumu}
    ---------------------------------
    """
    
    prompt = f"İşte mağazanın otonom dinamik fiyatlandırma ve pazar benchmark raporu:\n\n{fiyat_raporu_metni}"
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.7
            )
        )
        
        print("==================================================")
        print("📢 FİNANS AJANININ MAĞAZA SAHİBİNE STRATEJİ RAPORU (PAZAR ODAKLI)")
        print("==================================================")
        print(response.text)
        print("==================================================")
        return response.text

    except (ClientError, ServerError) as e:
        # 🛡️ FAULT TOLERANCE (HATA TOLERANSI) MİMARİSİ KORUNDU
        error_type = "503 Sunucu Yoğunluğu" if "503" in str(e) else "429 Kota Sınırı"
        print(f"\n[Financial Agent Warning] Gemini API {error_type} hatası fırlattı. Finansal yedek rapor aktif edildi.\n")
        
        backup_financial_report = """
        [FİNANSAL STRATEJİ RAPORU - GEÇİCİ YEDEK MOD]
        Google API servislerindeki anlık yoğunluk nedeniyle CFO Ajanının detaylı finansal yorumları şu an oluşturulamadı.
        Unutmayın, algoritma motorumuz tarafından hesaplanan pazar duyarlı dinamik fiyat listesi ve kurumsal güvenlik kuralları (Guardrails) 
        veri tabanı seviyesinde kararlı bir şekilde işletilmektedir. Mevcut önerilen marjları güvenle onaylayabilirsiniz.
        """
        return backup_financial_report

# Modülün test edilebilmesi için tetikleyici
if __name__ == "__main__":
    run_financial_agent()