import time
import random
import logging
import sys
from datetime import datetime, timedelta
from urllib.parse import urlparse
from duckduckgo_search import DDGS

# --- [PASTE YOUR DORKS HERE] ---
DORK_LIST = [
    'inurl:"get.php" "username=" "password="', 
    'filetype:env "DB_PASSWORD"',
    'intitle:"index of" "/live/" OR "/hls/"',
    '"config.php" "stalker" -github',
    'inurl:8080 "player_api.php"',
    'ext:log "error" "password"',
    'intitle:"index of" "m3u" OR "m3u8"',
    'inurl:phpmyadmin/setup/index.php'
    # ... Paste all 27 here
]

# --- CONFIGURATION & OPSEC ---
MIN_ACTIVE_WINDOW = 20  # Minutes
MAX_ACTIVE_WINDOW = 30  # Minutes
DOMAIN_COOLDOWN_MIN = 45 # Minutes to wait before hitting same host again
MAX_429_THRESHOLD = 5   # Hard-kill script after 5 blocks
LOG_FILE = "stealth_audit.log"

# Global state trackers
domain_history = {}
session_429_count = 0

logging.basicConfig(filename=LOG_FILE, level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def get_random_headers():
    """Entropy Engine: Generates a fresh identity per request."""
    uas = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/122.0.2365.92",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0"
    ]
    return {
        "User-Agent": random.choice(uas),
        "Referer": random.choice(["https://google.com", "https://duckduckgo.com", "https://t.co/"]),
        "Accept-Language": "en-US,en;q=0.9",
        "DNT": "1"
    }

def can_visit_domain(url):
    domain = urlparse(url).netloc
    if domain in domain_history:
        elapsed = (time.time() - domain_history[domain]) / 60
        if elapsed < DOMAIN_COOLDOWN_MIN:
            return False
    return True

def run_burst_session():
    """Runs a single 20-30 minute human-like burst of activity."""
    global session_429_count
    session_duration = random.randint(MIN_ACTIVE_WINDOW, MAX_ACTIVE_WINDOW)
    end_time = datetime.now() + timedelta(minutes=session_duration)
    
    print(f"[*] SESSION START: {datetime.now().strftime('%H:%M:%S')}")
    print(f"[*] WINDOW LIMIT: {session_duration} mins (Ending at {end_time.strftime('%H:%M:%S')})")

    # Blend Traffic: Manual-like idle before starting
    time.sleep(random.randint(60, 180))

    shuffled_dorks = DORK_LIST[:]
    random.shuffle(shuffled_dorks)

    for dork in shuffled_dorks:
        if datetime.now() >= end_time: break
        
        try:
            with DDGS() as ddgs:
                # Limit to 5 results per dork to avoid deep-crawling patterns
                results = list(ddgs.text(dork, max_results=5)) 
                
                for res in results:
                    if datetime.now() >= end_time: break
                    url = res.get('href')

                    if can_visit_domain(url):
                        # Human Jitter: 1-5 minutes between hits
                        wait = random.uniform(60, 300)
                        print(f"    [>] Jitter: {int(wait)}s before auditing: {url[:40]}...")
                        time.sleep(wait)

                        # --- LOGIC PLACEHOLDER ---
                        # status = perform_audit(url, get_random_headers())
                        # if status == 429: session_429_count += 1
                        
                        domain_history[urlparse(url).netloc] = time.time()
                        logging.info(f"Audited: {url}")

                        if session_429_count >= MAX_429_THRESHOLD:
                            print("!!! EMERGENCY SHUTDOWN: IP Safety threshold exceeded.")
                            sys.exit(1)
                    else:
                        logging.info(f"Skipping {url} - Domain is too 'warm'.")

        except Exception as e:
            logging.error(f"Batch Error: {e}")
            time.sleep(300)

    print(f"[*] Burst complete. Entering mandatory Blackout.")
    return "blackout"

if __name__ == "__main__":
    while True:
        run_burst_session()
        # Mandatory 1-2 hour total network silence
        blackout_period = random.randint(60, 120)
        print(f"[*] BLACKOUT: Total silence for {blackout_period} minutes...")
        time.sleep(blackout_period * 60)
