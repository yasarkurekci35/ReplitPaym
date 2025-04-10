import trafilatura
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import re
import json
from datetime import datetime

app = FastAPI()

# CORS ayarlarını ekleyelim (istemci tarafından erişilebilmesi için)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Tüm kaynaklara izin ver
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/exchange-rate")
async def get_exchange_rate():
    try:
        # Google'dan USD/TRY kurunu çekmek için
        url = "https://www.google.com/search?q=1+usd+to+try"
        
        # Web sayfasını çek
        response = requests.get(
            url, 
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
        )
        
        # Sayfadan içeriği çıkar
        downloaded = response.text
        text_content = trafilatura.extract(downloaded)
        
        # Kur değerini bul (ör. "1 ABD Doları = 32,12 Türk Lirası" şeklindeki metni)
        if text_content:
            # Regex ile kur değerini ara
            match = re.search(r'1 (?:ABD Doları|USD) = ([\d.,]+) (?:Türk Lirası|TRY)', text_content)
            if match:
                # Kur değerini temizle ve float'a dönüştür
                rate_str = match.group(1).replace(',', '.')
                rate = float(rate_str)
                
                return {
                    "success": True, 
                    "rate": rate,
                    "timestamp": datetime.now().isoformat()
                }
        
        # Alternatif yöntem: Sayfanın HTML içeriğinden regex ile çek
        match = re.search(r'data-exchange-rate="([\d.]+)"', downloaded)
        if match:
            rate = float(match.group(1))
            return {
                "success": True, 
                "rate": rate,
                "timestamp": datetime.now().isoformat()
            }
            
        # Eğer bulunamazsa hata döndür
        raise HTTPException(status_code=404, detail="Exchange rate not found")
        
    except Exception as e:
        print(f"Error fetching exchange rate: {str(e)}")
        # Sorunu çözemediğimizde geçici bir değer dön
        return {
            "success": False,
            "error": str(e),
            "fallback_rate": 32.45,  # Geçici değer
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    uvicorn.run("currency_api:app", host="0.0.0.0", port=5001, reload=True)