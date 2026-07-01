import os
import time

class ECommerceGateway:
    def __init__(self):
        """
        Geliştirilen sistemin e-ticaret altyapılarından bağımsız (agnostic) 
        çalışmasını sağlayan ağ geçidi sınıfının yapıcı fonksiyonu.
        .env dosyasındaki kimlik bilgilerini simüle eder.
        """
        self.gateway_url = os.getenv("ECOMMERCE_GATEWAY_URL", "https://api.mockstore.com/v1")
        self.auth_token = os.getenv("ECOMMERCE_AUTH_TOKEN", "mock_token_123")

    def sync_product_price(self, product_id: str, new_price: float) -> bool:
        """
        Human-in-the-Loop (HITL) arayüzünden onaylanan nihai fiyat kararını 
        uzak bulut sunucusuna REST API (POST/PUT) isteğiyle göndermeyi simüle eder.
        """
        try:
            # Gerçek dünya ağ gecikmesini (Network Latency) taklit etmek için 1.2 saniye bekler
            time.sleep(1.2)
            
            # Kimlik doğrulama simülasyonu ve başarılı ağ dönüşü
            if self.auth_token:
                print(f"[Gateway Outbound Log] {product_id} ürünü için yeni fiyat ({new_price} TL) e-ticaret kanalına başarıyla senkronize edildi.")
                return True
            else:
                print("[Gateway Error] Kimlik doğrulama token'ı bulunamadı.")
                return False
                
        except Exception as e:
            print(f"[Gateway Critical Error] Ağ bağlantısı simülasyonu başarısız: {str(e)}")
            return False

# NOT: app.py içindeki "from ecommerce_gateway import ECommerceGateway" 
# satırının hatasız çalışması için bu dosyanın adının tam olarak 
# 'ecommerce_gateway.py' olduğundan emin olun ve CTRL+S ile kaydedin.