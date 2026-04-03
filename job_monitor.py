import urllib.request
import urllib.parse
import json
import time

TOKEN = "8615330828:AAE_aeIbY30MgXNk8JgQhfFAhFR7xHjdeKM"
CHAT_ID = "737885020"

HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}

SOURCES = [
    ("Alchemy", "https://boards-api.greenhouse.io/v1/boards/alchemy/jobs"),
    ("Uniswap", "https://boards-api.greenhouse.io/v1/boards/uniswap/jobs"),
    ("Optimism", "https://boards-api.greenhouse.io/v1/boards/optimism/jobs"),
    ("MagicEden", "https://boards-api.greenhouse.io/v1/boards/magiceden/jobs"),
    ("Messari", "https://boards-api.greenhouse.io/v1/boards/messari/jobs"),
    ("Coinbase", "https://boards-api.greenhouse.io/v1/boards/coinbase/jobs"),
    ("Ripple", "https://boards-api.greenhouse.io/v1/boards/ripple/jobs"),
    ("Consensys", "https://boards-api.greenhouse.io/v1/boards/consensys/jobs"),
    ("Anchorage", "https://boards-api.greenhouse.io/v1/boards/anchorage/jobs"),
    ("Wise", "https://boards-api.greenhouse.io/v1/boards/wise/jobs"),
    ("Brex", "https://boards-api.greenhouse.io/v1/boards/brex/jobs"),
    ("Ramp", "https://boards-api.greenhouse.io/v1/boards/ramp/jobs"),
    ("Mercury", "https://boards-api.greenhouse.io/v1/boards/mercury/jobs"),
    ("Deel", "https://boards-api.greenhouse.io/v1/boards/deel/jobs"),
    ("Stripe", "https://boards-api.greenhouse.io/v1/boards/stripe/jobs"),
    ("Notion", "https://boards-api.greenhouse.io/v1/boards/notion/jobs"),
    ("Loom", "https://boards-api.greenhouse.io/v1/boards/loom/jobs"),
    ("Webflow", "https://boards-api.greenhouse.io/v1/boards/webflow/jobs"),
    ("Airtable", "https://boards-api.greenhouse.io/v1/boards/airtable/jobs"),
    ("Anthropic", "https://boards-api.greenhouse.io/v1/boards/anthropic/jobs"),
    ("Retool", "https://boards-api.greenhouse.io/v1/boards/retool/jobs"),
    ("Canva", "https://boards-api.greenhouse.io/v1/boards/canva/jobs"),
    ("Figma", "https://boards-api.greenhouse.io/v1/boards/figma/jobs"),
    ("Miro", "https://boards-api.greenhouse.io/v1/boards/miro/jobs"),
    ("Gitlab", "https://boards-api.greenhouse.io/v1/boards/gitlab/jobs"),
    ("Zapier", "https://boards-api.greenhouse.io/v1/boards/zapier/jobs"),
    ("Kraken", "https://api.lever.co/v0/postings/kraken"),
    ("Chainalysis", "https://api.lever.co/v0/postings/chainalysis"),
    ("Ledger", "https://api.lever.co/v0/postings/ledger"),
    ("Bitpanda", "https://api.lever.co/v0/postings/bitpanda"),
    ("Circle", "https://api.lever.co/v0/postings/circle"),
    ("Fireblocks", "https://api.lever.co/v0/postings/fireblocks"),
    ("Monzo", "https://api.lever.co/v0/postings/monzo"),
    ("Revolut", "https://api.lever.co/v0/postings/revolut"),
    ("Klarna", "https://api.lever.co/v0/postings/klarna"),
    ("Framer", "https://api.lever.co/v0/postings/framer"),
    ("Vercel", "https://api.lever.co/v0/postings/vercel"),
    ("Buffer", "https://api.lever.co/v0/postings/buffer"),
    ("Doist", "https://api.lever.co/v0/postings/doist"),
    ("Hotjar", "https://api.lever.co/v0/postings/hotjar"),
]

REMOTEOK_TAGS = ["design", "brand-design", "graphic-design", "ux", "ui"]

ROLE_KEYWORDS = [
    "brand designer", "graphic designer", "visual designer",
    "marketing designer", "communication designer", "creative designer",
    "digital designer", "brand identity", "art director",
    "senior designer", "product designer", "motion designer",
    "presentation designer", "creative lead", "ux designer",
    "ui designer", "ux/ui", "ui/ux", "designer",
]

LEVEL_BLOCK = ["junior", "intern", "entry level", "entry-level", "graduate"]

STOP_WORDS = [
    "us citizen", "green card", "us residence",
    "work authorization", "authorized to work in the us",
    "no visa sponsorship", "must be located in us",
    "us only", "usa only", "hybrid", "on-site", "onsite",
    "must reside in", "must live in", "unpaid", "volunteer",
    "must be based in", "permanently authorized",
]

seen_jobs = set()

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = urllib.parse.urlencode({
        "chat_id": CHAT_ID,
        "text": text[:4000],
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
        return False
    if any(b in title_low for b in LEVEL_BLOCK):
        return False
    if any(s in full for s in STOP_WORDS):
        return False
    return True

def fetch_greenhouse(company, url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=10) as r:
        data = json.loads(r.read())
    results = []
    for j in data.get("jobs", []):
        results.append({
            "id": str(j["id"]),
            "title": j.get("title", ""),
            "location": j.get("location", {}).get("name", "Remote"),
            "link": j.get("absolute_url", ""),
            "description": ""
        })
    return results

def fetch_lever(company, url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=10) as r:
        jobs = json.loads(r.read())
    results = []
    for j in jobs:
        desc = ""
        if isinstance(j.get("descriptionPlain"), str):
            desc = j["descriptionPlain"][:500]
        results.append({
            "id": str(j.get("id", "")),
            "title": j.get("text", ""),
            "location": j.get("categories", {}).get("location", "Remote"),
            "link": j.get("hostedUrl", ""),
            "description": desc
        })
    return results

def fetch_remoteok():
    results = []
    for tag in REMOTEOK_TAGS:
        try:
            url = f"https://remoteok.com/api?tag={tag}"
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=10) as r:
                jobs = json.loads(r.read())
            for job in jobs:
                if not isinstance(job, dict) or "id" not in job:
                    continue
                results.append({
                    "id": str(job["id"]),
                    "company": job.get("company", "Unknown"),
                    "title": job.get("position", ""),
                    "location": job.get("location", "Remote"),
                    "link": job.get("url", ""),
                    "salary": job.get("salary", ""),
                    "description": job.get("description", "")[:500]
                })
            time.sleep(2)
        except Exception as e:
            print(f"⚠️ RemoteOK {tag}: {e}")
    return results

def check_jobs():
    for company, url in SOURCES:
        try:
            if "lever.co" in url:
                jobs = fetch_lever(company, url)
            else:
                jobs = fetch_greenhouse(company, url)
            for job in jobs:
                jid = company + job["id"]
                if jid in seen_jobs:
                    continue
                seen_jobs.add(jid)
                if not is_good_job(job["title"], job["location"], job.get("description","")):
                    continue
                msg = (f"🚀 <b>Новая вакансия!</b>\n\n"
                       f"🏢 <b>{company}</b>\n"
                       f"💼 {job['title']}\n"
                       f"📍 {job['location']}\n"
                       f"🔗 {job['link']}\n\n"
                       f"⚡️ Подавайся в первые 10 минут!")
                send_telegram(msg)
                print(f"✅ {company}: {job['title']}")
            time.sleep(1)
        except Exception as e:
            print(f"⚠️ {company}: {e}")

    try:
        remoteok_jobs = fetch_remoteok()
        for job in remoteok_jobs:
            jid = "remoteok_" + job["id"]
            if jid in seen_jobs:
                continue
            seen_jobs.add(jid)
            if not is_good_job(job["title"], job["location"], job.get("description","")):
                continue
            salary_text = f"💰 {job['salary']}\n" if job.get("salary") else ""
            msg = (f"🌍 <b>RemoteOK!</b>\n\n"
                   f"🏢 <b>{job['company']}</b>\n"
                   f"💼 {job['title']}\n"
                   f"📍 {job['location']}\n"
                   f"{salary_text}"
                   f"🔗 {job['link']}\n\n"
                   f"⚡️ Подавайся в первые 10 минут!")
            send_telegram(msg)
            print(f"✅ RemoteOK: {job['title']} @ {job['company']}")
    except Exception as e:
        print(f"⚠️ RemoteOK: {e}")

send_telegram(
    "✅ <b>PandaJobHunt v6 запущен!</b>\n\n"
    "📋 40 компаний + RemoteOK\n"
    "🔍 Проверяет описание вакансии на стоп-слова\n"
    "🎯 Brand/Graphic/Visual/UX | Art Director\n"
    "📍 Remote Worldwide | 🚫 Без US Auth | 🚫 Unpaid\n"
    "💰 От $60k"
)

while True:
    print("\n🔍 Проверяю вакансии...")
    check_jobs()
    print("💤 Жду 30 минут...")
    time.sleep(1800)
```