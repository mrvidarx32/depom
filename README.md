# Binance Futures Funding Rate Monitor

Bu bot, Binance Futures borsasındaki perpetual coinlerin funding rate oranlarını takip eder ve -0.0500 oranının altına düştüklerinde Telegram üzerinden bildirim gönderir.

## Özellikler

- 🔄 Her dakika funding rate kontrolü
- 📊 -0.0500 eşiğinin altındaki tüm perpetual kontratları izleme
- 📱 Telegram üzerinden anlık bildirimler
- 📈 Funding rate değişimlerini takip etme
- 💰 Mark fiyat bilgilerini gösterme
- 📝 Detaylı log kayıtları

## Kurulum

### 1. Gereksinimler

```bash
pip install -r requirements.txt
```

### 2. Telegram Bot Oluşturma

1. Telegram'da @BotFather'ı bulun
2. `/newbot` komutunu gönderin
3. Bot adı ve kullanıcı adı belirleyin
4. Bot token'ını kopyalayın

### 3. Konfigürasyon

`.env.example` dosyasını `.env` olarak kopyalayın ve gerekli bilgileri doldurun:

```bash
cp .env.example .env
```

`.env` dosyasını düzenleyin:

```env
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

# Bot Configuration
FUNDING_RATE_THRESHOLD=-0.0500
CHECK_INTERVAL_MINUTES=1
```

### 4. Telegram Bot Kurulumu

Chat ID'nizi almak için kurulum scriptini çalıştırın:

```bash
python setup_telegram_bot.py
```

Bu script size adım adım rehberlik edecek ve chat ID'nizi otomatik olarak bulacaktır.

## Kullanım

### Botu Başlatma

```bash
python funding_rate_monitor.py
```

### Arka Planda Çalıştırma

```bash
nohup python funding_rate_monitor.py > bot.log 2>&1 &
```

### Docker ile Çalıştırma

```bash
docker build -t funding-rate-monitor .
docker run -d --env-file .env funding-rate-monitor
```

## Konfigürasyon Seçenekleri

| Değişken | Açıklama | Varsayılan |
|----------|----------|------------|
| `FUNDING_RATE_THRESHOLD` | Funding rate eşiği | -0.0500 |
| `CHECK_INTERVAL_MINUTES` | Kontrol aralığı (dakika) | 1 |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token'ı | Gerekli |
| `TELEGRAM_CHAT_ID` | Telegram chat ID'si | Gerekli |

## Örnek Telegram Mesajı

```
🚨 **Funding Rate Alert** 🚨
⏰ Time: 2024-01-15 14:30:25
📊 Threshold: -0.0500

📉 **BTCUSDT**
   💰 Funding Rate: -0.0523 (-5.23%)
   💵 Mark Price: $42,350.50

📉 **ETHUSDT**
   💰 Funding Rate: -0.0612 (-6.12%)
   💵 Mark Price: $2,580.75
```

## Log Dosyaları

Bot çalışırken aşağıdaki log dosyaları oluşturulur:

- `funding_rate_monitor.log` - Ana log dosyası
- Konsol çıktısı - Gerçek zamanlı durum bilgileri

## Sorun Giderme

### Bot Mesaj Göndermiyor
1. `.env` dosyasındaki token ve chat ID'yi kontrol edin
2. `python setup_telegram_bot.py` ile bağlantıyı test edin
3. Bot'un chat'e mesaj gönderme izni olduğundan emin olun

### API Hataları
1. İnternet bağlantınızı kontrol edin
2. Binance API'sinin çalışır durumda olduğunu kontrol edin
3. Rate limit aşımlarını kontrol edin

## Güvenlik

- Bot token'ınızı kimseyle paylaşmayın
- `.env` dosyasını git'e commit etmeyin
- Production ortamında güvenli bir sunucu kullanın

## Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit yapın (`git commit -m 'Add amazing feature'`)
4. Push yapın (`git push origin feature/amazing-feature`)
5. Pull Request oluşturun

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

## Sorumluluk Reddi

Bu bot sadece eğitim amaçlıdır. Finansal tavsiye niteliği taşımaz. Kripto para yatırımları risk içerir.
