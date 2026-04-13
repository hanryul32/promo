import os
import json
import glob
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGS_DIR = os.path.join(BASE_DIR, "logs")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
SITE_URL = "https://masa032.github.io/ichannels-promo/"
FACEBOOK_PAGE_URL = "https://www.facebook.com/gogo.buy.it/"
FACEBOOK_PAGE_ID = os.environ.get("FACEBOOK_PAGE_ID", "")
FACEBOOK_PAGE_ACCESS_TOKEN = os.environ.get("FACEBOOK_PAGE_ACCESS_TOKEN", "")


def load_latest_records():
    files = sorted(glob.glob(os.path.join(LOGS_DIR, "log_*.json")))
    if not files:
        return []
    with open(files[-1], "r", encoding="utf-8") as f:
        return json.load(f)


def build_post(records):
    top = records[:3]
    items = []
    for record in top:
        items.append(f"- {record['brand']}")

    intro = "今天幫大家整理了幾個我自己會先點開看的優惠，先把值得逛的放在這裡，省點比價時間。"
    body = "\n".join(items)
    close = f"\n\n想看完整整理可以直接逛這裡：{SITE_URL}\n也歡迎追蹤粉絲頁一起挖好物：{FACEBOOK_PAGE_URL}"
    return intro + "\n\n" + body + close


def save_draft(message):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(os.path.join(OUTPUT_DIR, "facebook_post.txt"), "w", encoding="utf-8") as f:
        f.write(message)


def post_to_facebook(message):
    import requests
    if not FACEBOOK_PAGE_ID or not FACEBOOK_PAGE_ACCESS_TOKEN:
        print("[Facebook] 未設定 PAGE_ID / ACCESS_TOKEN，已僅產生草稿")
        return False

    url = f"https://graph.facebook.com/v22.0/{FACEBOOK_PAGE_ID}/feed"
    payload = {
        "message": message,
        "link": SITE_URL,
        "access_token": FACEBOOK_PAGE_ACCESS_TOKEN,
    }
    resp = requests.post(url, data=payload, timeout=20)
    print(f"[Facebook] HTTP {resp.status_code}")
    if resp.status_code == 200:
        print("[Facebook] 貼文發佈成功")
        return True
    print(resp.text[:300])
    return False


def main():
    records = load_latest_records()
    if not records:
        print("[Facebook] 無最新 log，略過")
        return
    message = build_post(records)
    save_draft(message)
    post_to_facebook(message)


if __name__ == "__main__":
    main()