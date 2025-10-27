
import os
import requests
from scraper.imobiliarias import serrano, dtx, casabela, sainthome

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message}
    requests.post(url, data=data)

def main():
    novos = []
    for func in [serrano.get_data, dtx.get_data, casabela.get_data, sainthome.get_data]:
        novos.extend(func())
    if novos:
        send_telegram_message(f"Novos imóveis detectados: {len(novos)}")
    else:
        send_telegram_message("Nenhuma atualização encontrada.")

if __name__ == "__main__":
    main()
