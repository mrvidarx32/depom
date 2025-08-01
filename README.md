# depom
depom

## Funding Rate Monitor

Görev: Binance Futures perpetual coinlerin funding rate oranı -0.0500 (≈ -0.05 %) seviyesinin altına düştüğünde Telegram botuna bildirim göndermek.

### Kurulum

1. Aşağıdaki bağımlılığı yükleyin:

```bash
pip install -r requirements.txt
```

2. Telegram’da bir bot oluşturun ([@BotFather](https://t.me/BotFather)) ve `TELEGRAM_BOT_TOKEN` değerini alın.
3. Botu mesaj göndereceği gruba/private chate ekleyin ve `TELEGRAM_CHAT_ID` değerini alın (örn. `-1001234567890` veya kullanıcı ID’si).
4. Çevre değişkenlerini ayarlayın:

```bash
export TELEGRAM_BOT_TOKEN=<token>
export TELEGRAM_CHAT_ID=<chat_id>
# Opsiyonel ayarlar
export FUNDING_THRESHOLD=-0.0005   # -0.05 %
export POLL_INTERVAL=60            # saniye
```

### Çalıştırma

```bash
python funding_rate_monitor.py
```

Script her dakika Binance API’sinden funding rate verilerini alır ve eşik değerinin (varsayılan `-0.05 %`) altındaki coinleri Telegram üzerinden bildirir.
