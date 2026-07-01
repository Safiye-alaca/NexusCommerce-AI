import os
import json
from google import genai
from google.genai import types
from google.genai.errors import ClientError, ServerError # 🚨 Çift Katmanlı Hata Kalkanı Eklendi
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
    print("🤖 Finans Ajanı (Gemini v2) yeni fiyatları ve kâr marjlarını analiz ediyor...\n")
    
    # pricing_strategy artık SQL tabanlı çalıştığı için burası otomatik olarak canlı veri alır.
    fiyat_raporu = calculate_dynamic_pricing()
    fiyat_raporu_metni = json.dumps(fiyat_raporu, ensure_ascii=False, indent=2)
    
    system_instruction = f"""
    Sen NexusCommerce AI sisteminin kıdemli Finans Direktörü (CFO) ve Dinamik Fiyatlandırma Ajanısın.
    Görevin, sana verilen dinamik fiyatlandırma önerilerini incelemek ve mağaza sahibine finansal bir özet sunmaktır.
    
    Arka Plan Bilgisi: Sana dükkanın finansal verileriyle birlikte, Stok Yönetim Ajanımızın yazdığı Türkçe rapor da verilecektir. 
    Kararlarını açıklarken bu rapordaki lojistik uyarıları da göz önünde bulundur.
    
    Stok Ajanından Gelen Türkçe Rapor:
    ---------------------------------
    {stok_ajani_yorumu}
    ---------------------------------
    """
    
    prompt = f"İşte mağazanın otonom dinamik fiyatlandırma raporu:\n\n{fiyat_raporu_metni}"
    
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
        print("📢 FİNANS AJANININ MAĞAZA SAHİBİNE STRATEJİ RAPORU")
        print("==================================================")
        print(response.text)
        print("==================================================")
        return response.text

    except (ClientError, ServerError) as e:
        # 🛡️ FAULT TOLERANCE (HATA TOLERANSI) MİMARİSİ
        error_type = "503 Sunucu Yoğunluğu" if "503" in str(e) else "429 Kota Sınırı"
        print(f"\n[Financial Agent Warning] Gemini API {error_type} hatası fırlattı. Finansal yedek rapor aktif edildi.\n")
        
        backup_financial_report = """
        [FİNANSAL STRATEJİ RAPORU - GEÇİCİ YEDEK MOD]
        Google API servislerindeki anlık yoğunluk nedeniyle CFO Ajanının detaylı finansal yorumları şu an oluşturulamadı.
        Ancak, algoritma motorumuz tarafından hesaplanan dinamik fiyat listesi ve kurumsal güvenlik kuralları (Guardrails) 
        veri tabanı seviyesinde kararlı bir şekilde işletilmektedir. Mevcut önerilen marjları güvenle onaylayabilirsiniz.
        """
        return backup_financial_report

# Modülün test edilebilmesi için tetikleyici
if __name__ == "__main__":
    run_financial_agent()