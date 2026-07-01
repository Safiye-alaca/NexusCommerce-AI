import os
import json
import sqlite3 # 🚨 SQL Veri tabanı bağlantısı için eklendi
from google import genai
from google.genai import types
from google.genai.errors import ClientError, ServerError
from dotenv import load_dotenv

# .env dosyasını sisteme yükle
load_dotenv()

GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")

# API Anahtarı kontrolü
if not GOOGLE_API_KEY:
    raise ValueError("❌ HATA: .env dosyasından GEMINI_API_KEY okunamadı!")

client = genai.Client(api_key=GOOGLE_API_KEY)
DB_FILE = "nexus_store.db" # 🚨 Canlı SQL Veri Tabanı Dosyamız

def get_live_products_from_db():
    """
    Veri tabanına bağlanır, SELECT sorgusuyla tüm ürünleri çeker 
    ve bunları Python sözlük (Dictionary) listesine dönüştürür.
    """
    try:
        # Veri tabanı odasının kapısını açıyoruz
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # 📊 SQL Sorgusu: products tablosundaki tüm sütun ve satırları getir
        cursor.execute("SELECT * FROM products")
        rows = cursor.fetchall()
        
        # Sütun isimlerini alıyoruz (Urun_ID, Urun_Adi vb.)
        column_names = [description[0] for description in cursor.description]
        
        # Ham SQL verisini ajanımızın kolayca okuyabileceği JSON/Dict yapısına çeviriyoruz
        products_list = []
        for row in rows:
            products_list.append(dict(zip(column_names, row)))
            
        conn.close() # Kapıyı güvenle kapatıyoruz
        return products_list
        
    except Exception as e:
        print(f"❌ Veri tabanından veri çekilirken hata oluştu: {str(e)}")
        return []

def run_data_scientist_agent():
    print("🤖 Veri Bilimci Ajanı (Gemini v2) SQL Veri Tabanını inceliyor...\n")
    
    # 🚨 ARTIK CSV DEĞİL, CANLI SQL VERİ TABANI OKUNUYOR!
    canli_urunler = get_live_products_from_db()
    rapor_metni = json.dumps(canli_urunler, ensure_ascii=False, indent=2)
    
    system_instruction = """
    Sen NexusCommerce AI sisteminin kıdemli Veri Bilimcisi ve Stok Yönetim Ajanısın.
    Görevin, sana verilen e-ticaret stok ve talep tahmin raporunu incelemek, 
    ikas mağaza sahibinin anlayacağı dilden, profesyonel, samimi ve net bir Türkçe özet çıkarmaktır.
    """
    
    prompt = f"İşte mağazanın veri tabanından gelen güncel stok ve talep analiz raporu:\n\n{rapor_metni}"
    
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
        print("📢 VERİ BİLİMCİ AJANININ MAĞAZA SAHİBİNE RAPORU (SQL TABANLI)")
        print("==================================================")
        print(response.text)
        print("==================================================")
        
        return response.text

    except (ClientError, ServerError) as e:
        error_type = "503 Sunucu Yoğunluğu" if "503" in str(e) else "429 Kota Sınırı"
        print(f"\n[Agent Warning] Gemini API {error_type} hatası fırlattı. Yedek mod aktif edildi.\n")
        
        backup_report = """
        [YEDEK OPERASYONEL RAPOR - GEÇİCİ ÇEVRİMDIŞI MOD]
        Google Gemini sunucularındaki anlık yüksek yoğunluk (503) veya kota sınırı nedeniyle canlı yapay zeka analizi şu an duraklatıldı.
        Mevcut envanter kuralları ve kural tabanlı koruma motoru (Guardrails) veri tabanı seviyesinde güvenle çalışmaya devam etmektedir. 
        Lütfen birkaç dakika sonra sayfayı yenileyiniz veya işleminize yerel modda devam ediniz.
        """
        return backup_report

if __name__ == "__main__":
    run_data_scientist_agent()