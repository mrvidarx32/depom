import os
import time
import requests
from datetime import datetime, timezone

"""
Funding-Rate Monitor for Binance Futures Perpetual Contracts
-----------------------------------------------------------
Sends a Telegram message every minute for each symbol whose **last funding rate**
falls below the configured negative threshold.

Setup:
1. Create a Telegram bot and obtain the *BOT_TOKEN*.
2. Add the bot to a chat (group or private) and obtain the *CHAT_ID* (as an integer).
3. Set the following **environment variables** (export in shell or use a dotenv loader):
   TELEGRAM_BOT_TOKEN  – Bot token received from BotFather
   TELEGRAM_CHAT_ID    – Numeric chat id the bot should post to
   FUNDING_THRESHOLD   – (optional) threshold as decimal, default "-0.0005" (-0.05 %)
   POLL_INTERVAL       – (optional) interval in seconds, default "60"

Run the script with:
    python funding_rate_monitor.py

Notes:
* Binance API: https://binance-docs.github.io/apidocs/futures/en/#get-premium-index
* Telegram  API: https://core.telegram.org/bots/api#sendmessage
"""

BINANCE_PREMIUM_URL = "https://fapi.binance.com/fapi/v1/premiumIndex"
TELEGRAM_API_BASE = "https://api.telegram.org/bot{token}/{method}"


def _env(key: str, default: str | None = None) -> str | None:
    """Small helper to read environment variables with an optional default."""
    return os.environ.get(key, default)


def fetch_premium_index() -> list[dict]:
    """Fetch premium index for **all** symbols from Binance Futures REST API."""
    try:
        resp = requests.get(BINANCE_PREMIUM_URL, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        # When called from a restricted location Binance may return an error JSON with keys code/msg
        if isinstance(data, dict) and "code" in data and data.get("code") != 200:
            raise RuntimeError(f"Binance error: {data.get('msg', data)}")
        return data  # list of dicts
    except Exception as exc:
        print(f"[ERROR] Failed to fetch premium index: {exc}")
        return []


def send_telegram_message(token: str, chat_id: str, text: str) -> None:
    """Send *text* message to Telegram chat via bot token."""
    url = TELEGRAM_API_BASE.format(token=token, method="sendMessage")
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True,
    }
    try:
        resp = requests.post(url, json=payload, timeout=10)
        resp.raise_for_status()
    except Exception as exc:
        print(f"[ERROR] Failed to send Telegram message: {exc}")


def build_alerts(data: list[dict], threshold: float) -> list[str]:
    """Return list of alert strings for symbols under *threshold* funding rate."""
    alerts: list[str] = []
    for entry in data:
        try:
            rate = float(entry.get("lastFundingRate", 0))
            if rate <= threshold:
                symbol = entry.get("symbol")
                alerts.append(f"*{symbol}* funding rate: {rate * 100:.4f}%")
        except (TypeError, ValueError):
            # skip malformed row
            continue
    return alerts


def main() -> None:
    bot_token = _env("TELEGRAM_BOT_TOKEN")
    chat_id = _env("TELEGRAM_CHAT_ID")
    if not bot_token or not chat_id:
        raise SystemExit("Please set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID environment variables.")

    threshold = float(_env("FUNDING_THRESHOLD", "-0.0005"))
    interval = int(float(_env("POLL_INTERVAL", "60")))

    print(f"[INFO] Starting funding-rate monitor: threshold={threshold}, interval={interval}s")

    while True:
        start_ts = time.time()
        data = fetch_premium_index()
        alerts = build_alerts(data, threshold)
        if alerts:
            time_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
            message = f"⚠️ *Binance Funding Rate Alert* (\< {threshold*100:.4f}%)\n{time_str}\n\n" + "\n".join(alerts)
            send_telegram_message(bot_token, chat_id, message)
            print(f"[INFO] Sent alert with {len(alerts)} symbol(s)")
        else:
            print("[DEBUG] No symbols below threshold this cycle")

        # Sleep for remainder of interval
        elapsed = time.time() - start_ts
        time.sleep(max(0, interval - elapsed))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[INFO] Monitor stopped by user")