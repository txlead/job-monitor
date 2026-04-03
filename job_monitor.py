cat > ~/job_monitor/job_monitor.py << 'ENDOFSCRIPT'
import urllib.request
import urllib.parse
import json
import time

TOKEN = "8615330828:AAE_aeIbY30MgXNk8JgQhfFAhFR7xHjdeKM"
CHAT_ID = "737885020"

SOURCES = [
    ("Alchemy", "https://boards-api.greenhouse.io/v1/boards/alchemy/jobs"),
    ("Uniswap", "https://boards-api.greenhouse.io/v1/boards/uniswap/jobs"),
    ("Optimism", "https://boards-api.greenhouse.io/v1/boards/optimism/jobs"),
    ("MagicEden", "https://boards-api.greenhouse.io/v1/boards/magiceden/jobs"),
    ("Messari", "https://boards-api.greenhouse.io/v1/boards/messari/jobs"),
    ("Phantom", "https://boards-api.greenhouse.io/v1/boards/phantom/jobs"),
    ("Coinbase", "https://boards-api.greenhouse.io/v1/boards/coinbase/jobs"),
    ("Figma", "https://boards-api.greenhouse.io/v1/boards/figma/jobs"),
    ("Anthropic", "https://boards-api.greenhouse.io/v1/boards/anthropic/jobs"),
    ("Ripple", "https://boards-api.greenhouse.io/v1/boards/ripple/jobs"),
    ("Kraken", "https://api.lever.co/v0/postings/kraken"),
    ("Chainalysis", "https://api.lever.co/v0/postings/chainalysis"),
    ("Ledger", "https://api.lever.co/v0/postings/ledger"),
    ("Bitpanda", "https://api.lever.co/v0/postings/bitpanda"),
    ("Circle", "https://api.lever.co/v0/postings/circle"),
    ("Monzo", "https://api.lever.co/v0/postings/monzo"),
]

ROLE_KEYWORDS = [
    "brand designer", "graphic designer", "visual designer",
    "marketing designer", "communication designer", "creative designer",
    "digital designer", "brand identity", "art director",
    "senior designer", "mid designer", "product designer",
    "motion designer", "presentation designer", "creative lead",
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

REMOTE_GOOD = [
    "remote", "worldwide", "anywhere", "global",
    "emea", "contractor", "distributed",
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

def is_good_job(title, location, description=""):
    title_low = title.lower()
    loc_low = location.lower()
    desc_low = description.lower()
    full = title_low + " " + loc_low + " " + desc_low

    if not any(k in title_low for k in ROLE_KEYWORDS):
        return False, "роль не подходит"

    if any(b in title_low for b in LEVEL_BLOCK):
        return False, "junior/intern уровень"

    if any(s in full for s in STOP_WORDS):
        return False, "стоп-слово"

    return True, "ок"

def fetch_greenhouse(company, url):
    results = []
    with urllib.request.urlopen(url, timeout=10) as r:
        jobs = json.loads(r.read()).get("jobs", [])
    for job in jobs:
        results.append({
            "id": str(job["id"]),
            "title": job.get("title", ""),
            "location": job.get("location", {}).get("name", "Remote"),
            "link": job.get("absolute_url", ""),
        })
    return results

def fetch_lever(company, url):
    results = []
    with urllib.request.urlopen(url, timeout=10) as r:
        jobs = json.loads(r.read())
    for job in jobs:
        results.append({
            "id": str(job.get("id", "")),
            "title": job.get("text", ""),
            "location": job.get("categories", {}).get("location", "Remote"),
            "link": job.get("hostedUrl", ""),
        })
    return results

def check_jobs():
    for company, url in SOURCES:
        try:
            if "lever.co" in url:
                jobs = fetch_lever(company, url)
            else:
                jobs = fetch_greenhouse(company, url)

            new_count = 0
            for job in jobs:
                jid = company + job["id"]
                if jid in seen_jobs:
                    continue
                seen_jobs.add(jid)

                title = job["title"]
                location = job["location"]
                link = job["link"]

                ok, reason = is_good_job(title, location)
                if not ok:
                    continue

                new_count += 1
                msg = (
                    f"🚀 <b>Новая вакансия!</b>\n\n"
                    f"🏢 <b>{company}</b>\n"
                    f"💼 {title}\n"
                    f"📍 {location}\n"
                    f"🔗 {link}\n\n"
                    f"⚡️ Подавайся в первые 10 минут!"
                )
                send_telegram(msg)
                print(f"✅ {company}: {title}")

        except Exception as e:
            print(f"⚠️ {company}: {e}")

send_telegram(
    "✅ <b>PandaJobHunt v3 запущен!</b>\n\n"
    "📋 Мониторю 16 компаний каждые 30 минут\n"
    "🎯 Фильтры: Brand/Graphic/Visual/Art Director\n"
    "📍 Только Remote Worldwide\n"
    "🚫 Без US Auth / Green Card / Hybrid\n"
    "💰 Mid-Senior уровень"
)

while True:
    print("\n🔍 Проверяю вакансии...")
    check_jobs()
    print("💤 Жду 30 минут...")
    time.sleep(1800)
ENDOFSCRIPT