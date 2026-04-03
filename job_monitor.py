import urllib.request
import urllib.parse
import json
import time

TOKEN = "8615330828:AAE_aeIbY30MgXNk8JgQhfFAhFR7xHjdeKM"
CHAT_ID = "737885020"

SOURCES = [
    # Крипто/Web3 - Greenhouse
    ("Alchemy", "https://boards-api.greenhouse.io/v1/boards/alchemy/jobs"),
    ("Uniswap", "https://boards-api.greenhouse.io/v1/boards/uniswap/jobs"),
    ("Optimism", "https://boards-api.greenhouse.io/v1/boards/optimism/jobs"),
    ("MagicEden", "https://boards-api.greenhouse.io/v1/boards/magiceden/jobs"),
    ("Messari", "https://boards-api.greenhouse.io/v1/boards/messari/jobs"),
    ("Coinbase", "https://boards-api.greenhouse.io/v1/boards/coinbase/jobs"),
    ("Ripple", "https://boards-api.greenhouse.io/v1/boards/ripple/jobs"),
    ("Consensys", "https://boards-api.greenhouse.io/v1/boards/consensys/jobs"),
    ("Dapper", "https://boards-api.greenhouse.io/v1/boards/dapperlabs/jobs"),
    ("Anchorage", "https://boards-api.greenhouse.io/v1/boards/anchorage/jobs"),
    # Крипто/Web3 - Lever
    ("Kraken", "https://api.lever.co/v0/postings/kraken"),
    ("Chainalysis", "https://api.lever.co/v0/postings/chainalysis"),
    ("Ledger", "https://api.lever.co/v0/postings/ledger"),
    ("Bitpanda", "https://api.lever.co/v0/postings/bitpanda"),
    ("Circle", "https://api.lever.co/v0/postings/circle"),
    ("Fireblocks", "https://api.lever.co/v0/postings/fireblocks"),
    ("Lido", "https://api.lever.co/v0/postings/lidofinance"),
    # Fintech
    ("Wise", "https://boards-api.greenhouse.io/v1/boards/wise/jobs"),
    ("Brex", "https://boards-api.greenhouse.io/v1/boards/brex/jobs"),
    ("Ramp", "https://boards-api.greenhouse.io/v1/boards/ramp/jobs"),
    ("Mercury", "https://boards-api.greenhouse.io/v1/boards/mercury/jobs"),
    ("Deel", "https://boards-api.greenhouse.io/v1/boards/deel/jobs"),
    ("Stripe", "https://boards-api.greenhouse.io/v1/boards/stripe/jobs"),
    ("Monzo", "https://api.lever.co/v0/postings/monzo"),
    ("Revolut", "https://api.lever.co/v0/postings/revolut"),
    ("Klarna", "https://api.lever.co/v0/postings/klarna"),
    # AI/Tech
    ("Notion", "https://boards-api.greenhouse.io/v1/boards/notion/jobs"),
    ("Linear", "https://boards-api.greenhouse.io/v1/boards/linear/jobs"),
    ("Loom", "https://boards-api.greenhouse.io/v1/boards/loom/jobs"),
    ("Webflow", "https://boards-api.greenhouse.io/v1/boards/webflow/jobs"),
    ("Airtable", "https://boards-api.greenhouse.io/v1/boards/airtable/jobs"),
    ("Anthropic", "https://boards-api.greenhouse.io/v1/boards/anthropic/jobs"),
    ("Runway", "https://boards-api.greenhouse.io/v1/boards/runwayml/jobs"),
    ("Framer", "https://api.lever.co/v0/postings/framer"),
    ("Pitch", "https://api.lever.co/v0/postings/pitch"),
    # Стартапы YC/a16z
    ("Retool", "https://boards-api.greenhouse.io/v1/boards/retool/jobs"),
    ("Superhuman", "https://boards-api.greenhouse.io/v1/boards/superhuman/jobs"),
    ("Coda", "https://boards-api.greenhouse.io/v1/boards/coda/jobs"),
    ("Vercel", "https://api.lever.co/v0/postings/vercel"),
    ("Planetscale", "https://api.lever.co/v0/postings/planetscale"),
    ("Supabase", "https://api.lever.co/v0/postings/supabase"),
    ("Resend", "https://api.lever.co/v0/postings/resend"),
    # Design tools
    ("Canva", "https://boards-api.greenhouse.io/v1/boards/canva/jobs"),
    ("Figma", "https://boards-api.greenhouse.io/v1/boards/figma/jobs"),
    ("Miro", "https://boards-api.greenhouse.io/v1/boards/miro/jobs"),
    # Remote-first компании
    ("Gitlab", "https://boards-api.greenhouse.io/v1/boards/gitlab/jobs"),
    ("Zapier", "https://boards-api.greenhouse.io/v1/boards/zapier/jobs"),
    ("Buffer", "https://api.lever.co/v0/postings/buffer"),
    ("Doist", "https://api.lever.co/v0/postings/doist"),
    ("Hotjar", "https://api.lever.co/v0/postings/hotjar"),
]

ROLE_KEYWORDS = [
    "brand designer", "graphic designer", "visual designer",
    "marketing designer", "communication designer", "creative designer",
    "digital designer", "brand identity", "art director",
    "senior designer", "mid designer", "product designer",
    "motion designer", "presentation designer", "creative lead",
    "ux designer", "ui designer", "ux/ui", "ui/ux",
]

LEVEL_BLOCK = ["junior", "intern", "entry level", "entry-level", "graduate"]

STOP_WORDS = [
    "us citizen", "green card", "us residence",
    "work authorization", "authorized to work in the us",
    "authorized to work in the uk", "authorized to work in canada",
    "no visa sponsorship", "must be located in us",
    "us only", "usa only", "hybrid", "on-site", "onsite",
    "must reside in", "must live in",
]

seen_jobs = set()

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = urllib.parse.urlencode({
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }).encode()
    try:
        urllib.request.urlopen(url, data)
    except Exception as e:
        print(f"Telegram error: {e}")

def is_good_job(title, location):
    title_low = title.lower()
    loc_low = location.lower()
    full = title_low + " " + loc_low
    if not any(k in title_low for k in ROLE_KEYWORDS):
        return False
    if any(b in title_low for b in LEVEL_BLOCK):
        return False
    if any(s in full for s in STOP_WORDS):
        return False
    return True

def fetch_greenhouse(url):
    with urllib.request.urlopen(url, timeout=10) as r:
        jobs = json.loads(r.read()).get("jobs", [])
    return [{"id": str(j["id"]), "title": j.get("title",""), "location": j.get("location",{}).get("name","Remote"), "link": j.get("absolute_url","")} for j in jobs]

def fetch_lever(url):
    with urllib.request.urlopen(url, timeout=10) as r:
        jobs = json.loads(r.read())
    return [{"id": str(j.get("id","")), "title": j.get("text",""), "location": j.get("categories",{}).get("location","Remote"), "link": j.get("hostedUrl","")} for j in jobs]

def check_jobs():
    for company, url in SOURCES:
        try:
            jobs = fetch_lever(url) if "lever.co" in url else fetch_greenhouse(url)
            for job in jobs:
                jid = company + job["id"]
                if jid in seen_jobs:
                    continue
                seen_jobs.add(jid)
                if not is_good_job(job["title"], job["location"]):
                    continue
                msg = (f"🚀 <b>Новая вакансия!</b>\n\n"
                       f"🏢 <b>{company}</b>\n"
                       f"💼 {job['title']}\n"
                       f"📍 {job['location']}\n"
                       f"🔗 {job['link']}\n\n"
                       f"⚡️ Подавайся в первые 10 минут!")
                send_telegram(msg)
                print(f"✅ {company}: {job['title']}")
        except Exception as e:
            print(f"⚠️ {company}: {e}")

send_telegram("✅ <b>PandaJobHunt v4 запущен!</b>\n\n📋 50 компаний | Крипто + Fintech + AI + Стартапы\n🎯 Brand/Graphic/Visual/UX Designer | Art Director\n📍 Remote Worldwide | 🚫 Без US Auth\n💰 От $60k")

while True:
    print("\n🔍 Проверяю вакансии...")
    check_jobs()
    print("💤 Жду 30 минут...")
    time.sleep(1800)
```

После вставки → **CMD+S** → в Terminal:
```
cd ~/job_monitor && git add . && git commit -m "v4 50 companies" && git push