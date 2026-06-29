import json
from google import genai
from google.genai import types
from pricing_strategy import calculate_dynamic_pricing

GOOGLE_API_KEY = "AQ.Ab8RN6KGUVgT4sOLZP3-uJrqKPqUDS2G6em_qmM2Zp6SsNY2qg"
client = genai.Client(api_key=GOOGLE_API_KEY)

# 🔥 MÜHENDİSLİK DOKUNUŞU: Fonksiyona dışarıdan stok_ajani_yorumu parametresi ekledik
def run_financial_agent(stok_ajani_yorumu=""):
    print("🤖 Finans Ajanı (Gemini v2) yeni fiyatları ve kâr marjlarını analiz ediyor...\n")
    
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