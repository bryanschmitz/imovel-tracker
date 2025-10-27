import os, requests
from scraper.imobiliarias import (
    serrano, solemar, conceito, supreema, casabela, genial, mw, silvaso
)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def tg(msg: str):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("Telegram não configurado.")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

SITES = [serrano, solemar, conceito, supreema, casabela, genial, mw, silvaso]

def main():
    tg("✅ Imóvel Tracker iniciado. Coletando nos 8 sites...")
    total = 0
    linhas = []
    for mod in SITES:
        try:
            itens = mod.scrape()
            total += len(itens)
            linhas.append(f"{mod.SOURCE_NAME}: {len(itens)}")
        except Exception as e:
            linhas.append(f"{getattr(mod,'SOURCE_NAME','site')}: erro ({e})")
    tg(f"📊 Coleta concluída: {total} imóveis. " + " | ".join(linhas))

if __name__ == "__main__":
    main()
