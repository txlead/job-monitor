import urllib.request
import urllib.parse
import json
import time

TOKEN = "8615330828:AAE_aeIbY30MgXNk8JgQhfFAhFR7xHjdeKM"
CHAT_ID = "737885020"

SOURCES = [
    ("Alchemy", "https://boards-api.greenhouse.io/v1/boards/alchemy/jobs"),
    ("Kraken", "https://boards-api.greenhouse.io/v1/boards/kraken/jobs"),
    ("Chainalysis", "https://boards-api.greenhouse.io/v1/boards/chainalysis/jobs"),
    ("Ledger", "https://boards-api.greenhouse.io/v1/boards/ledger/jobs"),
    ("Messari", "https://boards-api.greenhouse.io/v1/boards/messari/jobs"),
]

KEYWORDS = ["design", "brand", "graphic", "visual", "creative", "motion"]
STOP_WORDS = ["us only", "us citizen", "green card", "work permit", "authorized to work in the us"]

seen_jobs = set()

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = urllib.parse.urlencode({"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}).encode()
    urllib.request.urlopen(url, data)

def check_jobs():
    for company, url in SOURCES:
        try:
            with urllib.request.urlopen(url) as r:
                jobs = json.loads(r.read())["jobs"]
            for job in jobs:
                jid = job["id"]
                title = job["title"].lower()
                location = job.get("location", {}).get("name", "").lower()
                link = job["absolute_url"]
                if jid in seen_jobs:
                    continue
                seen_jobs.add(jid)
                if not any(k in title for k in KEYWORDS):
                    continue
                if any(s in (title + location) for s in STOP_WORDS):
                    continue
                msg = f"🚀 <b>Новая вакансия!</b>\n\n<b>{company}</b>: {job['title']}\n📍 {job.get('location',{}).get('name','Remote')}\n🔗 {link}"
                send_telegram(msg)
        except Exception as e:
            print(f"Error {company}: {e}")

send_telegram("✅ PandaJobHunt запущен! Мониторю вакансии каждые 30 минут.")

while True:
    print("Проверяю вакансии...")
    check_jobs()
    time.sleep(1800)