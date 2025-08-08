import re, hashlib, asyncio
from typing import List, Dict
import httpx
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; PrevostGoBot/1.0; +https://prevostgo.com)"
}

def _hash(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()

def extract_listing_urls(html: str) -> List[str]:
    soup = BeautifulSoup(html, "lxml")
    urls = []
    for a in soup.select("a[href]"):
        href = a.get("href","")
        # Heuristic: listing detail pages usually under same domain with id-like paths
        if "prevost-stuff.com" in href and ("detail" in href.lower() or "for" in href.lower()):
            urls.append(href)
        # Also capture relative detail links from listing cards
        if href.startswith("forsale/") or href.startswith("/forsale/"):
            urls.append(f"https://www.prevost-stuff.com/{href.lstrip('/')}")
    # Deduplicate & filter noise
    urls = [u for u in dict.fromkeys(urls) if "public_list_ads.php" not in u]
    return urls

def parse_detail(html: str, url: str) -> Dict:
    soup = BeautifulSoup(html, "lxml")

    # Title / price
    title = soup.select_one("title")
    title_text = title.get_text(strip=True) if title else None

    # Common places for price/specs
    price_text = None
    cand = soup.find(string=re.compile(r"\$\s?\d"))
    if cand:
        price_text = cand.strip()

    # Specs in tables / lists
    specs = {}
    for row in soup.select("table tr"):
        cells = [c.get_text(" ", strip=True) for c in row.find_all(["td","th"])]
        if len(cells) >= 2 and len(cells[0]) < 40:
            key = cells[0].strip(": ").lower()
            val = cells[1]
            specs[key] = val

    # Fallback: definition lists / bullet lists
    for li in soup.select("ul li"):
        txt = li.get_text(" ", strip=True)
        if ":" in txt and len(txt.split(":")[0]) < 40:
            k,v = txt.split(":",1)
            specs[k.strip().lower()] = v.strip()

    # Photos (skip ad iframes/images by size/domain heuristics)
    photos = []
    for img in soup.find_all("img"):
        src = img.get("src") or img.get("data-src")
        if not src: 
            continue
        if "ads" in src.lower() or "doubleclick" in src.lower():
            continue
        if src.startswith("//"):
            src = "https:" + src
        elif src.startswith("/"):
            src = "https://www.prevost-stuff.com" + src
        photos.append(src)

    # Normalize basics from title/specs
    year = None
    model = None
    m = re.search(r"(20\d{2}|19\d{2})", title_text or "")
    if m:
        year = int(m.group(1))
    if "model" in specs:
        model = specs.get("model")

    # Price numeric
    price = None
    if price_text:
        m2 = re.search(r"\$\s?([\d,]+)", price_text)
        if m2:
            price = float(m2.group(1).replace(",", ""))

    data = {
        "external_id": _hash(url),
        "url": url,
        "title": title_text,
        "year": year,
        "model": model,
        "price": price,
        "location": specs.get("location") or specs.get("city") or specs.get("state"),
        "specs": specs,
        "features": [],
        "photos": photos,
        "seller": {},
        "is_active": True,
    }
    return data

async def scrape_all(list_url: str) -> List[Dict]:
    async with httpx.AsyncClient(headers=HEADERS, timeout=30) as client:
        r = await client.get(list_url)
        r.raise_for_status()
        detail_urls = extract_listing_urls(r.text)

        results = []
        for url in detail_urls:
            try:
                d = await client.get(url)
                d.raise_for_status()
                data = parse_detail(d.text, url)
                results.append(data)
            except Exception as e:
                # continue on errors
                continue
    return results
