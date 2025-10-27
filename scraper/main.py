import os
import requests
from bs4 import BeautifulSoup

# Credenciais do Telegram vindas dos secrets do GitHub
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Lista de sites e funções específicas
from imobiliarias import casabela, dtx, sainthome, serrano

def send_message(message):
    """Envia mensagem para o Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Erro ao enviar mensagem: {e}")

def main():
    send_message("🏠 Iniciando coleta de imóveis...")
    total_coletados = 0

    # Executa coleta em cada imobiliária
    for func, nome in [
        (casabela.run, "Casa Bela"),
        (dtx.run, "DTX"),
        (sainthome.run, "Saint Home"),
        (serrano.run, "Serrano"),
    ]:
        try:
            qtd = func()
            total_coletados += qtd
            send_message(f"✅ {nome}: {qtd} imóveis coletados com sucesso.")
        except Exception as e:
            send_message(f"⚠️ Erro ao coletar {nome}: {e}")

    send_message(f"🏁 Coleta concluída. Total: {total_coletados} imóveis.")

if __name__ == "__main__":
    main()
