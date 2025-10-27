# scraper/imobiliarias/serrano.py
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

SOURCE_NAME = "Serrano"

# URL que você enviou já com Imbé filtrado
START_URL = "https://www.iserrano.com.br/busca?finalidade=venda&cidades%5B%5D=2"

UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/121 Safari/537.36"}

def _fetch(url, tries=2, sleep=1.0, timeout=25):
    last = None
    for _ in range(tries):
        try:
            r = requests.get(url, headers=UA, timeout=timeout)
            r.raise_for_status()
            return r.text
        except Exception as e:
            last = e
            time.sleep(sleep)
    raise last

def _price_to_int(txt: str | None):
    if not txt:
        return None
    import re
    digits = re.sub(r"[^0-9]", "", txt)
    return int(digits) if digits.isdigit() else None

def _extract_cards(html: str, base_url: str):
    """
    Tenta ser tolerante com variações de HTML:
    - procura blocos de cards
    - pega título, preço e link
    """
    soup = BeautifulSoup(html, "lxml")
    cards = []
    # vários seletores comuns em portais imobiliários
    candidates = soup.select(
        ".card-imovel, .imovel-card, .property, .property-card, "
        ".lista-imoveis .item, .listagem-imoveis .item, .card, ul#imoveis li"
    )
    for c in candidates:
        a = c.select_one("a[href]")
        if not a: 
            continue
        href = urljoin(base_url, a["href"])
        # tenta achar título/preço em seletores comuns
        title_el = c.select_one(".titulo, .title, .property-card__title, h2, h3, .nome") or a
        price_el = c.select_one(".preco, .price, .valor, .property-card__price, .preco-imovel")
        title = title_el.get_text(" ", strip=True) if title_el else ""
        price = _price_to_int(price_el.get_text(" ", strip=True) if price_el else "")
        cards.append({"url": href, "title": title, "price": price})
    # fallback: se não encontrou cards estruturados, pega links de detalhe
    if not cards:
        for a in soup.select('a[href*="imovel"], a[href*="imoveis"]'):
            href = urljoin(base_url, a["href"])
            title = a.get_text(" ", strip=True)
            if len(title) < 3:
                continue
            cards.append({"url": href, "title": title, "price": None})
    return cards

def _find_next_url(html: str, base_url: str):
    soup = BeautifulSoup(html, "lxml")
    # links “Próxima”, “Next”, símbolo » ou rel=next
    nxt = (
        soup.find("a", string=lambda s: s and ("Próxima" in s or "Proxima" in s or "Next" in s or "»" in s))
        or soup.select_one('a[rel="next"], .pagination a.next, .paginacao a.next')
    )
    if nxt and nxt.has_attr("href"):
        return urljoin(base_url, nxt["href"])
    # fallback para paginação numérica ativa → pega o próximo irmão
    current = soup.select_one(".pagination .active a, .paginacao .active a")
    if current and current.parent and current.parent.find_next("a"):
        return urljoin(base_url, current.parent.find_next("a")["href"])
    return None

def scrape():
    """
    Varre TODAS as páginas a partir do START_URL.
    Retorna lista de dicts: {url, title, price}
    """
    url = START_URL
    out, seen = [], set()
    # limite de segurança alto (pode ter 30+ páginas)
    for _ in range(60):
        html = _fetch(url)
        items = _extract_cards(html, url)
        added = 0
        for it in items:
            if it["url"] in seen:
                continue
            seen.add(it["url"])
            out.append(it)
            added += 1
        nxt = _find_next_url(html, url)
        if not nxt or nxt == url or added == 0:
            break
        url = nxt
    return out
