import os
import json
from google import genai
from google.genai import types
from stock_analyzer import analyze_stock_runout_risk
from dotenv import load_dotenv

# .env dosyasını sisteme yükle
load_dotenv()

GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")

# API Anahtarı kontrolü
if not GOOGLE_API_KEY:
    raise ValueError("❌ HATA: .env dosyasından GEMINI_API_KEY okunamadı!")

client = genai.Client(api_key=GOOGLE_API_KEY)

def run_data_scientist_agent():
    print("🤖 Veri Bilimci Ajanı (Gemini v2) raporları ve tahminleri inceliyor...\n")
    
    teknik_rapor = analyze_stock_runout_risk()
    rapor_metni = json.dumps(teknik_rapor, ensure_ascii=False, indent=2)
    
    system_instruction = """
    Sen NexusCommerce AI sisteminin kıdemli Veri Bilimcisi ve Stok Yönetim Ajanısın.
    Görevin, sana verilen e-ticaret stok ve talep tahmin raporunu incelemek, 
    ikas mağaza sahibinin anlayacağı dilden, profesyonel, samimi ve net bir Türkçe özet çıkarmaktır.
    """
    
    prompt = f"İşte mağazanın güncel stok ve talep analiz raporu:\n\n{rapor_metni}"
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.7
        )
    )
    
    print("==================================================")
    print("📢 VERİ BİLİMCİ AJANININ MAĞAZA SAHİBİNE RAPORU")
    print("==================================================")
    print(response.text)
    print("==================================================")
    
    return response.text

# 🚨 KRİTİK TETİKLEYİCİ: Dosya doğrudan çalıştırıldığında fonksiyonu başlatır!
if __name__ == "__main__":
    run_data_scientist_agent()