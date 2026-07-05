# 🔮 NexusCommerce AI - Multi-Agent Autonomous E-Commerce Engine

<img width="1918" height="851" alt="Ekran görüntüsü 2026-07-05 133546" src="https://github.com/user-attachments/assets/d6bbe2f0-876b-4f25-babd-484e6cea1029" />

NexusCommerce AI, e-ticaret envanter yönetimi, pazar analitiği ve dinamik fiyatlandırma süreçlerini uçtan uca otonom olarak optimize eden, kurumsal mimariye sahip multi-agent (çoklu ajan) tabanlı bir SaaS platformudur. 

Sistem, işletmenin iç depo ve envanter telemetrisi ile dış pazar istihbaratını (rakip fiyat değişimlerini) harmanlayarak **Oyun Teorisi (Nash Dengesi)** ve marj koruma zırhları altında kârlılığı maksimize etmek üzere tasarlanmıştır.

---

## 🏛️ Sistem Mimarisi ve Katman Yapısı

Platform, mikroservis odaklı ve tek sorumluluk (Single Responsibility) prensibine uygun olarak 4 ana operasyonel katmandan oluşmaktadır:


[ Canlı Veri Tabanı Katmanı (SQLite) ]
   │ 🛡️ (Context Manager & timeout=10 Emniyet Zırhı)
   ▼
[ Algoritmik Karar Motoru ] ──► 🧠 (Oyun Teorisi & Taban Fiyat Bariyeri)
   │
   ▼
[ Çoklu Ajan Konsensüs Odası ] ──► 🕵️‍♂️ (Veri Bilimci & CFO Ajanları - Gemini 2.5)
   │
   ▼
[ HITL Yönetim Dashboard ] ──► 📊 (Streamlit UI & ECharts Canlı Telemetri)


### 1. 🛡️ Kararlı Veri Tabanı Katmanı (`database_manager.py`)
* SQLite altyapısı üzerinde **Context Manager (`with` blokları)** ve **`timeout=10` parametresi** entegre edilmiştir.
* Eşzamanlı (concurrent) çalışan ajan istekleri ve yoğun stres testleri altında oluşabilecek `Database Locked` (`OperationalError`) kilitlenmeleri tamamen engellenerek mimari kararlılık en üst düzeye çıkarılmıştır.
* Genişletilmiş veri şeması (`products` tablosu), anlık piyasa takibi için `Rakip_Fiyat_A` ve `Rakip_Fiyat_B` sütunlarını barındırır.
* `audit_logs` tablosu, sistem üzerinden gerçekleştirilen tüm fiyat güncellemelerini ve simüle edilen pazar enjeksiyonlarını tarihsel olarak kayıt altında tutar.

### 2. 🧠 Pazar Duyarlı Dinamik Karar Motoru (`pricing_strategy.py`)
* Sadece iç stok metriklerine odaklanan geleneksel modellerin aksine, **Competitor-Aware (Rakip Duyarlı)** fiyatlandırma algoritmasını koşturur.
* **Sıfıra Doğru Yarış (Price War) Koruması:** Yıkıcı pazar rekabeti koşullarında, önerilen yeni fiyatın ürün maliyetinin %10 taban sınırının altına düşmesini engelleyen algoritmik bir koruma bariyeri (Anti-Price-War Shield) barındırır.
* Stok fazlası durumunda pazar payını korumak adına fiyatı pazar ortalamasına doğru esnetirken (Nash Dengesi Gevşemesi), kritik stok azlığında kâr marjını otonom olarak maksimize eder.

### 3. 🕵️‍♂️ Çoklu Ajan Konsensüs Odası (`data_scientist_agent.py` & `financial_agent.py`)
* **Veri Bilimci Ajanı (Gemini 2.5 Flash):** Canlı SQL verilerini ve rakip telemetrisini analiz ederek talep hızı (Demand Velocity) ve envanter risk haritasını çıkarır.
* **Finans Direktörü (CFO) Ajanı (Gemini 2.5 Flash):** Veri bilimciden gelen lojistik raporu girdi olarak alır, finansal marj süzgecinden geçirerek makro kararları üretir.
* **Çift Katmanlı Hata Toleransı (Fault Tolerance):** Gemini API servislerinde yaşanabilecek olası kota sınırları (`429`) veya sunucu yoğunluğu (`503`) durumlarında, sistem arayüzün çökmesini engelleyerek kural tabanlı yerel emniyet moduna (Guardrails) otonom geçiş yapar.

### 4. 📊 HITL Yönetici Kontrol Dashboard'u (`app.py`)
* **Performans Önbelleği (Agent Response Caching):** Ajan çıktıları ve raporları `st.session_state` mimarisiyle önbelleğe alınarak gereksiz LLM API çağrıları sıfırlanmış, sayfa yenileme hızı 0 milisaniyeye (jet hızı) düşürülmüştür.
* **Akıllı Önbellek Temizleme (Cache Invalidation):** Mağaza yöneticisi panelden yeni bir pazar koşulu simüle ettiği an (`Inject Market Conditions`), eski önbellek otomatik kırılarak ajanların güncel veriyle tek bir istek atması sağlanır.
* **ECharts Telemetri Analitiği:** Veri tabanındaki log dağılımları ve operasyonel geçmiş, interaktif pasta ve çizgi grafikleriyle anlık olarak görselleştirilir.

