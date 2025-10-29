import nest_asyncio
nest_asyncio.apply()

import logging
import requests
import asyncio
import re
from datetime import datetime, timedelta, timezone
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# ------------------------------
# 1. KONFIGURACJA BOTA
# ------------------------------

TELEGRAM_TOKEN = "Telegram-Token"
CHECK_INTERVAL = 15  # w sekundach
LAST_SEEN_OFFERS = set()

# Docelowe ceny kupna
PRICES = {
    "X": 150,
    "XR": 150,
    "XS": 200,
    "XS Max": 200,
    "11": 300,
    "11 Pro": 350,
    "11 Pro Max": 450,
    "12": 500,
    "12 Mini": 350,
    "12 Pro": 700,
    "12 Pro Max": 800,
    "13": 700,
    "13 Mini": 650,
    "13 Pro": 1200,
    "13 Pro Max": 1400,
    "14": 1200,
    "14 Plus": 1300,
    "14 Pro": 1800,
    "14 Pro Max": 2000,
    "15": 1800,
    "15 Plus": 1900,
    "15 Pro": 2400,
    "15 Pro Max": 2800,
    "16": 2500,
    "16 Plus": 2500,
    "16 Pro": 3000,
    "16 Pro Max": 3500
}
# alias
desired_prices = PRICES

# OLX API (dostosuj parametry jeśli potrzebujesz)
OLX_API_URL = (
    "https://www.olx.pl/api/v1/offers/"
    "?offset=0&limit=40&query=iphone&category_id=1839"
    "&sort_by=created_at%3Adesc"
)

# ------------------------------
# 2. POBIERANIE OFERT Z API
# ------------------------------

def fetch_offers_from_api():
    try:
        resp = requests.get(OLX_API_URL)
        resp.raise_for_status()
        data = resp.json().get("data", [])
        logging.info(f"Pobrano {len(data)} ofert")
        offers = []
        for ad in data:
            offer_id = ad.get("id")
            title = ad.get("title", "Brak tytułu")
            # parsowanie ceny
            price_val = None
            for p in ad.get("params", []):
                if p.get("key") == "price":
                    lbl = p.get("value", {}).get("label", "")
                    digits = re.sub(r"\D", "", lbl)
                    if digits:
                        price_val = int(digits)
                    break
            link = ad.get("url", "")
            # 3 pierwsze zdjęcia
            imgs = []
            for ph in ad.get("photos", [])[:3]:
                url = ph.get("link", "").replace("{width}", "400").replace("{height}", "400")
                imgs.append(url)
            # lokalizacja
            loc = ad.get("location", {})
            city = loc.get("city", {}).get("name", "")
            region = loc.get("region", {}).get("name", "")
            dist = loc.get("district", {}).get("name", "")
            location = ", ".join(filter(None, [city, region, dist])) or "Brak lokalizacji"
            created = ad.get("created_time")
            offers.append({
                "id": offer_id,
                "title": title,
                "price": price_val,
                "url": link,
                "image_urls": imgs,
                "created_time": created,
                "location": location
            })
        # unikalne po ID
        unique = {o["id"]: o for o in offers}
        return list(unique.values())
    except Exception as e:
        logging.error(f"fetch_offers error: {e}")
        return []

# ------------------------------
# 3. SPRAWDZANIE I WYSYŁANIE
# ------------------------------

async def check_new_offers(context: ContextTypes.DEFAULT_TYPE):
    logging.info("check_new_offers...")
    chat_id = context.job.chat_id
    offers = fetch_offers_from_api()
    now = datetime.now(timezone.utc)
    new_offers = []
    for o in offers:
        ct = o.get("created_time")
        if ct:
            try:
                created = datetime.fromisoformat(ct)
            except:
                continue
            if created < now - timedelta(minutes=15):
                continue
        if o["id"] not in LAST_SEEN_OFFERS:
            LAST_SEEN_OFFERS.add(o["id"])
            new_offers.append(o)
    logging.info(f"Nowych ofert: {len(new_offers)}")
    for o in new_offers:
        title = o["title"]
        price = o["price"]
        link = o["url"]
        loc = o["location"]
        imgs = o["image_urls"]

        # odnajdź model (najpierw dłuższe nazwy)
        model = None
        low = title.lower()
        for m in sorted(desired_prices.keys(), key=lambda x: -len(x)):
            if f"iphone {m.lower()}" in low:
                model = m
                break

        diff_str = ""
        if model and price is not None:
            target = desired_prices[model]
            d = price - target
            if d > 0:
                diff_str = f"🟥 +{d}"
            elif d < 0:
                diff_str = f"🟩 {d}"
            else:
                diff_str = "0"

        msg = f"{title}\nCena: {price} zł"
        if diff_str:
            msg += f" ({diff_str})"
        msg += f"\n📍 {loc}\n🔗 {link}"

        try:
            if imgs:
                # tylko pierwsze zdjęcie z podpisem
                await context.bot.send_photo(chat_id=chat_id, photo=imgs[0], caption=msg)
            else:
                await context.bot.send_message(chat_id=chat_id, text=msg)
        except Exception as e:
            logging.error(f"send error: {e}")

# ------------------------------
# 4. KOMENDA /start
# ------------------------------

ALLOWED_USERS = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid not in ALLOWED_USERS:
        await update.message.reply_text("🚫 Brak uprawnień.")
        return
    await update.message.reply_text("🔍 Bot uruchomiony. Monitoruję OLX...")
    context.application.job_queue.run_repeating(
        check_new_offers,
        interval=CHECK_INTERVAL,
        first=0,
        chat_id=update.effective_chat.id
    )

# ------------------------------
# 5. MAIN
# ------------------------------

async def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    logging.info("Polling...")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
