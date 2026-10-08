#!/usr/bin/env python3
"""
Liputon Ticket Watcher — Suliko, Q-teatteri
============================================
Lähettää Telegram-ilmoituksen heti kun lippuja on myynnissä.
Maksimi 5 ilmoitusta, jonka jälkeen ohjelma sammuu.

Vaatimukset:
    pip install requests

Käyttö:
    python suliko_watcher.py
"""

import time
import requests

# ── Asetukset ──────────────────────────────────────────────────────────────────

EVENT_ID = 116661

TELEGRAM_BOT_TOKEN = "8522009815:AAH0vPp29WOT0_z2xUsgAXfERyHHafLZ7Gs"
TELEGRAM_CHAT_ID   = "801399738"

POLL_INTERVAL_SECONDS = 90
MAX_ALERTS = 5

# ── End configuration ──────────────────────────────────────────────────────────

API_DETAIL = f"https://api.liputon.fi/v1/events/{EVENT_ID}"
EVENT_PAGE = f"https://www.liputon.fi/events/{EVENT_ID}"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; ticket-watcher/1.0)",
    "Accept": "application/json",
    "Origin": "https://www.liputon.fi",
    "Referer": "https://www.liputon.fi/",
}


def send_telegram(message: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    try:
        r = requests.post(url, json={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        }, timeout=10)
        r.raise_for_status()
        print("  [Telegram ✓]")
    except Exception as e:
        print(f"  [Telegram ✗] {e}")


def fetch_tickets() -> list[dict]:
    r = requests.get(API_DETAIL, headers=HEADERS, timeout=15)
    r.raise_for_status()
    data = r.json()
    tickets = []
    for t in data.get("tickets", []):
        if t.get("status") == "FOR_SALE":
            tickets.append(t)
    for child in data.get("child_events", []):
        for t in child.get("tickets", []):
            if t.get("status") == "FOR_SALE":
                tickets.append(t)
    return tickets


def main():
    print("=" * 60)
    print("  Liputon Watcher — Suliko, Q-teatteri")
    print(f"  Tarkistaa {POLL_INTERVAL_SECONDS}s välein, max {MAX_ALERTS} ilmoitusta")
    print("=" * 60)
    send_telegram(
        "🔍 <b>Lippuvahti käynnistetty</b>\n"
        "Seurataan Suliko-näytelmän lippuja (Q-teatteri).\n"
        f"Maksimi ilmoituksia: {MAX_ALERTS}"
    )

    alerts_sent = 0

    while True:
        ts = time.strftime("%H:%M:%S")
        try:
            tickets = fetch_tickets()
            print(f"[{ts}] {len(tickets)} lippua myynnissä.")

            if tickets:
                send_telegram(
                    f"🎭 <b>{len(tickets)} lippu myynnissä — Suliko, Q-teatteri</b>\n\n"
                    f'👉 <a href="{EVENT_PAGE}">Osta Liputonista →</a>'
                )
                alerts_sent += 1
                print(f"       Ilmoituksia lähetetty: {alerts_sent}/{MAX_ALERTS}")
                if alerts_sent >= MAX_ALERTS:
                    send_telegram("🔕 Lippuvahti pysäytetty — maksimi ilmoitusmäärä täynnä.")
                    print("Maksimi ilmoituksia lähetetty. Lopetetaan.")
                    return

        except Exception as e:
            print(f"[{ts}] Virhe: {e}")

        time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
