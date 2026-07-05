import os
import json
import sqlite3
from google import genai
from google.genai import types
from google.genai.errors import ClientError, ServerError
from dotenv import load_dotenv
# 🚨 GÜVENLİK REFACTORING: Zırhlı sorgu fonksiyonumuzu dahil ediyoruz
from database_manager import sql_query_to_dataframe

# .env dosyasını sisteme yükle
load_dotenv()

GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")

# API Anahtarı kontrolü
if not GOOGLE_API_KEY:
    raise ValueError("❌ HATA: .env dosyasından GEMINI_API_KEY okunamadı!")

client = genai.Client(api_key=GOOGLE_API_KEY)
DB_FILE = "nexus_store.db" # Canlı SQL Veri Tabanı Dosyamız

def get_live_products_from_db():
    """
    Güvenli database_manager kalkanı üzerinden veri tabanına bağlanır, 
    SELECT sorgusuyla tüm ürünleri ve yeni rakip fiyatlarını çekerek 
    ajanın kolayca okuyabileceği bir sözlük (Dictionary) listesine dönüştürür.
    """
    # 🚨 YENİ: database_manager üzerindeki timeout ve context manager zırhını buraya da uyguluyoruz
    # Sorguyu genişleterek yeni eklediğimiz pazar sütunlarını (Rakip_Fiyat_A, Rakip_Fiyat_B) dahil ettik
    query = "SELECT Urun_ID, Urun_Adi, Kalan_Stok, Maliyet, Mevcut_Fiyat, Gunluk_Satis, Rakip_Fiyat_A, Rakip_Fiyat_B FROM products"
    df = sql_query_to_dataframe(query)
    
    if df.empty:
        return []
        
    # Pandas DataFrame'i ajanın okuyabileceği dict/json yapısına dönüştürüyoruz
    return df.to_dict(orient="records")

def run_data_scientist_agent():
    print("🤖 Veri Bilimci Ajanı (Gemini v2) SQL Veri Tabanını ve Pazar Metriklerini inceliyor...\n")
    
    # Canlı veri tabanı ve rakip fiyat verileri tek hamlede çekilir
    canli_urunler = get_live_products_from_db()
    rapor_metni = json.dumps(canli_urunler, ensure_ascii=False, indent=2)
    
    # 🚨 PROMPT UPGRADE: Sistem talimatını pazar zekası, rakip baskısı ve Nash dengesi analizi yapacak şekilde genişletiyoruz
    system_instruction = """
    Sen NexusCommerce AI platformunun kıdemli Veri Bilimcisi ve Pazar Analitiği Ajanısın.
    Görevin, sana verilen iç envanter metriklerini ve dış pazar telemetrisini (Rakip A ve Rakip B fiyatlarını) inceleyerek 
    mağaza sahibinin anlayacağı dilden, profesyonel, samimi ve net bir Türkçe özet rapor çıkarmaktır.
    
    Analiz Ederken Şu 3 Kriteri Mutlaka Yorumla:
    1. Talep Hızı (Demand Velocity) ve Stok Riski: Hangi ürünler kritik eşiğin (60 adet) altında?
    2. Pazar Rekabet Konumu: Bizim fiyatlarımız rakiplerin neresinde kalıyor? Pazar payı kaybetme riskimiz var mı?
    3. Stratejik Öneri: Rakiplerin baskısına ve stok durumumuza göre fiyat esnetilmeli mi yoksa kârı maksimize etmek için artırılmalı mı?
    """
    
    prompt = f"İşte mağazanın veri tabanından gelen güncel pazar ve envanter analiz raporu:\n\n{rapor_metni}"
    
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
        print("📢 VERİ BİLİMCİ AJANININ MAĞAZA SAHİBİNE RAPORU (PAZAR VE SQL TABANLI)")
        print("==================================================")
        print(response.text)
        print("==================================================")
        
        return response.text

    except (ClientError, ServerError) as e:
        error_type = "503 Sunucu Yoğunluğu" if "503" in str(e) else "429 Kota Sınırı"
        print(f"\n[Agent Warning] Gemini API {error_type} hatası fırlattı. Yedek mod aktif edildi.\n")
        
        backup_report = """
        [YEDEK OPERASYONEL RAPOR - GEÇİCİ ÇEVRİMDIŞI MOD]
        Google Gemini sunucularındaki anlık yüksek yoğunluk (503) veya kota sınırı nedeniyle canlı yapay zeka pazar analizi şu an duraklatıldı.
        Mevcut envanter kuralları ve kural tabanlı koruma motoru (Guardrails) veri tabanı seviyesinde güvenle çalışmaya devam etmektedir. 
        Lütfen birkaç dakika sonra sayfayı yenileyiniz veya işleminize yerel modda devam ediniz.
        """
        return backup_report

if __name__ == "__main__":
    run_data_scientist_agent()