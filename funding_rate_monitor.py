import os
import time
import logging
import schedule
from datetime import datetime
from typing import Dict, List, Optional
import requests
from dotenv import load_dotenv
from telegram import Bot
from telegram.error import TelegramError

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('funding_rate_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BinanceFundingRateMonitor:
    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')
        self.threshold = float(os.getenv('FUNDING_RATE_THRESHOLD', '-0.0500'))
        self.check_interval = int(os.getenv('CHECK_INTERVAL_MINUTES', '1'))
        
        # Binance API configuration
        self.api_key = os.getenv('BINANCE_API_KEY')
        self.secret_key = os.getenv('BINANCE_SECRET_KEY')
        
        # Initialize Telegram bot
        if self.bot_token:
            self.telegram_bot = Bot(token=self.bot_token)
        else:
            logger.error("TELEGRAM_BOT_TOKEN not found in environment variables")
            self.telegram_bot = None
            
        # Store previous funding rates to track changes
        self.previous_rates: Dict[str, float] = {}
        
        # Binance API endpoints
        self.base_url = "https://fapi.binance.com"
        
        logger.info(f"Funding Rate Monitor initialized with threshold: {self.threshold}")
        logger.info(f"Check interval: {self.check_interval} minutes")

    def get_funding_rates(self) -> List[Dict]:
        """Fetch current funding rates from Binance Futures API"""
        try:
            url = f"{self.base_url}/fapi/v1/premiumIndex"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching funding rates: {e}")
            return []

    def filter_perpetual_contracts(self, funding_data: List[Dict]) -> List[Dict]:
        """Filter only perpetual contracts with funding rates below threshold"""
        perpetual_contracts = []
        
        for contract in funding_data:
            symbol = contract.get('symbol', '')
            funding_rate = float(contract.get('lastFundingRate', '0'))
            
            # Only include perpetual contracts (not delivery contracts)
            if symbol and funding_rate <= self.threshold:
                perpetual_contracts.append({
                    'symbol': symbol,
                    'funding_rate': funding_rate,
                    'next_funding_time': contract.get('nextFundingTime', ''),
                    'mark_price': contract.get('markPrice', ''),
                    'index_price': contract.get('indexPrice', '')
                })
        
        return perpetual_contracts

    def format_message(self, contracts: List[Dict]) -> str:
        """Format the message for Telegram"""
        if not contracts:
            return "No perpetual contracts found with funding rate below threshold."
        
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f"🚨 **Funding Rate Alert** 🚨\n"
        message += f"⏰ Time: {current_time}\n"
        message += f"📊 Threshold: {self.threshold:.4f}\n\n"
        
        for contract in contracts:
            symbol = contract['symbol']
            rate = contract['funding_rate']
            mark_price = contract['mark_price']
            
            # Check if rate has changed
            previous_rate = self.previous_rates.get(symbol)
            change_indicator = ""
            if previous_rate is not None:
                if rate < previous_rate:
                    change_indicator = "📉"
                elif rate > previous_rate:
                    change_indicator = "📈"
            
            message += f"{change_indicator} **{symbol}**\n"
            message += f"   💰 Funding Rate: {rate:.4f} ({rate*100:.2f}%)\n"
            message += f"   💵 Mark Price: ${float(mark_price):,.2f}\n\n"
        
        return message

    def send_telegram_message(self, message: str) -> bool:
        """Send message to Telegram"""
        if not self.telegram_bot or not self.chat_id:
            logger.error("Telegram bot or chat ID not configured")
            return False
            
        try:
            self.telegram_bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='Markdown'
            )
            logger.info("Telegram message sent successfully")
            return True
            
        except TelegramError as e:
            logger.error(f"Error sending Telegram message: {e}")
            return False

    def check_funding_rates(self):
        """Main function to check funding rates and send alerts"""
        logger.info("Checking funding rates...")
        
        # Get current funding rates
        funding_data = self.get_funding_rates()
        if not funding_data:
            logger.warning("No funding rate data received")
            return
        
        # Filter perpetual contracts below threshold
        perpetual_contracts = self.filter_perpetual_contracts(funding_data)
        
        if perpetual_contracts:
            # Format and send message
            message = self.format_message(perpetual_contracts)
            self.send_telegram_message(message)
            
            # Update previous rates
            for contract in perpetual_contracts:
                self.previous_rates[contract['symbol']] = contract['funding_rate']
        else:
            logger.info("No perpetual contracts found below threshold")

    def start_monitoring(self):
        """Start the monitoring process"""
        logger.info("Starting funding rate monitoring...")
        
        # Schedule the job to run every X minutes
        schedule.every(self.check_interval).minutes.do(self.check_funding_rates)
        
        # Run initial check
        self.check_funding_rates()
        
        # Keep the script running
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute for scheduled tasks
            except KeyboardInterrupt:
                logger.info("Monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                time.sleep(60)

def main():
    """Main function"""
    monitor = BinanceFundingRateMonitor()
    
    # Validate configuration
    if not monitor.bot_token:
        logger.error("Please set TELEGRAM_BOT_TOKEN in your .env file")
        return
    
    if not monitor.chat_id:
        logger.error("Please set TELEGRAM_CHAT_ID in your .env file")
        return
    
    # Start monitoring
    monitor.start_monitoring()

if __name__ == "__main__":
    main()