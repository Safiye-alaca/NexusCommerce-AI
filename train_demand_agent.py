import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error


# ==========================================
# 1. ADIM: VERİYİ YÜKLEME VE TARİH DÖNÜŞÜMÜ
# ==========================================
# Dün ürettiğimiz e-ticaret geçmiş verisini okuyoruz
df = pd.read_csv("ecommerce_data.csv")

# Tarih sütununu metinden (string) gerçek tarih formatına çeviriyoruz
df['Tarih'] = pd.to_datetime(df['Tarih'])

# ==========================================
# 2. ADIM: ÖZNİTELİK MÜHENDİSLİĞİ (FEATURE ENGINEERING)
# ==========================================
# Modelin kalıpları yakalayabilmesi için tarihten sayısal ipuçları türetiyoruz
df['Haftanin_Gunu'] = df['Tarih'].dt.weekday  # 0 (Pazartesi) - 6 (Pazar) arası
df['Ay'] = df['Tarih'].dt.month               # 1 - 12 arası ay bilgisi
df['Is_Weekend'] = df['Haftanin_Gunu'].apply(lambda x: 1 if x >= 5 else 0)  # Hafta sonu mu? (1/0)

# ==========================================
# 3. ADIM: GECİKMELİ ÖZNİTELİKLER (LAG FEATURES)
# ==========================================
# Modelin trendi görebilmesi için her ürünün 1 ve 2 gün önceki satışlarını sütun olarak ekliyoruz
df['Gecmis_Satis_1_Gun_Once'] = df.groupby('Urun_ID')['Gunluk_Satis'].shift(1)
df['Gecmis_Satis_2_Gun_Once'] = df.groupby('Urun_ID')['Gunluk_Satis'].shift(2)

# İlk günlerin geçmiş verisi olamayacağı için oluşan boş satırları (NaN) temizliyoruz
df = df.dropna()

# ==========================================
# 4. ADIM: MODELİN EĞİTİLMESİ (MACHINE LEARNING)
# ==========================================
# Modelin öğrenirken kullanacağı girdiler (Features)
X = df[['Haftanin_Gunu', 'Ay', 'Is_Weekend', 'Mevcut_Fiyat', 'Gecmis_Satis_1_Gun_Once', 'Gecmis_Satis_2_Gun_Once']]

# Modelin tahmin etmeye çalışacağı hedef değer (Target)
y = df['Gunluk_Satis']

# Veriyi %80 Eğitim (Train) ve %20 Test (Validation) olarak ikiye bölüyoruz
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Matematiksel doğrusal regresyon modelimizi tanımlıyoruz ve eğitiyoruz
model = LinearRegression()
model.fit(X_train, y_train)

# ==========================================
# 5. ADIM: MODEL BAŞARISINI ÖLÇME (EVALUATION)
# ==========================================
# Ayırdığımız %20'lik test verisi üzerinde tahminler yapıyoruz
tahminler = model.predict(X_test)

# Modelin tahminlerinin gerçek değerlerden ortalama ne kadar saptığını (RMSE) hesaplıyoruz
rmse = np.sqrt(mean_squared_error(y_test, tahminler))

print("==================================================")
print("✅ NexusCommerce AI: Talep Tahmin Modeli Eğitildi!")
print("==================================================")
print(f"📉 Modelin Ortalama Tahmin Hatası (RMSE): {rmse:.2f} adet.")
print("--------------------------------------------------")
print("💡 Not: Bu hata payı, modelin gelecekteki satışları")
print("   tahmin ederken ortalama kaç adet yanıldığını gösterir.")
print("==================================================")

# Eğitilen modeli ve sütun isimlerini korumak için kaydediyoruz
joblib.dump(model, "demand_model.joblib")
print("💾 Model 'demand_model.joblib' adıyla başarıyla diske kaydedildi!")