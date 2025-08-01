#!/usr/bin/env python3
"""
Helper script to set up Telegram bot and get chat ID
"""

import os
import requests
from dotenv import load_dotenv

def create_telegram_bot():
    """Guide user through creating a Telegram bot"""
    print("🤖 Telegram Bot Setup Guide")
    print("=" * 40)
    print("1. Open Telegram and search for @BotFather")
    print("2. Send /newbot command")
    print("3. Follow the instructions to create your bot")
    print("4. Copy the bot token (looks like: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz)")
    print("5. Add the token to your .env file as TELEGRAM_BOT_TOKEN")
    print()

def get_chat_id(bot_token):
    """Get chat ID by sending a message to the bot"""
    print("📱 Getting Chat ID")
    print("=" * 40)
    print("1. Find your bot in Telegram (using the username you created)")
    print("2. Send any message to the bot (e.g., /start)")
    print("3. Wait a moment and press Enter to continue...")
    input()
    
    try:
        # Get updates from bot
        url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
        response = requests.get(url)
        data = response.json()
        
        if data['ok'] and data['result']:
            for update in data['result']:
                if 'message' in update:
                    chat_id = update['message']['chat']['id']
                    chat_type = update['message']['chat']['type']
                    chat_title = update['message']['chat'].get('title', 'Private Chat')
                    
                    print(f"✅ Found chat: {chat_title} (Type: {chat_type})")
                    print(f"📋 Chat ID: {chat_id}")
                    print(f"💡 Add this to your .env file as TELEGRAM_CHAT_ID={chat_id}")
                    return chat_id
        else:
            print("❌ No messages found. Make sure you sent a message to your bot.")
            return None
            
    except Exception as e:
        print(f"❌ Error getting chat ID: {e}")
        return None

def test_bot_connection(bot_token, chat_id):
    """Test if the bot can send messages"""
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = {
            'chat_id': chat_id,
            'text': '✅ Bot connection test successful! Your funding rate monitor is ready to use.'
        }
        response = requests.post(url, data=data)
        
        if response.status_code == 200:
            print("✅ Bot connection test successful!")
            return True
        else:
            print(f"❌ Bot connection test failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing bot connection: {e}")
        return False

def main():
    """Main setup function"""
    load_dotenv()
    
    print("🚀 Binance Futures Funding Rate Monitor Setup")
    print("=" * 50)
    
    # Check if bot token exists
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if not bot_token:
        print("❌ TELEGRAM_BOT_TOKEN not found in .env file")
        create_telegram_bot()
        return
    
    print(f"✅ Bot token found: {bot_token[:10]}...")
    
    if not chat_id:
        print("❌ TELEGRAM_CHAT_ID not found in .env file")
        chat_id = get_chat_id(bot_token)
        if chat_id:
            print(f"\n💡 Add this line to your .env file:")
            print(f"TELEGRAM_CHAT_ID={chat_id}")
        return
    
    print(f"✅ Chat ID found: {chat_id}")
    
    # Test connection
    print("\n🧪 Testing bot connection...")
    if test_bot_connection(bot_token, chat_id):
        print("\n🎉 Setup complete! You can now run the funding rate monitor.")
        print("Run: python funding_rate_monitor.py")
    else:
        print("\n❌ Setup incomplete. Please check your configuration.")

if __name__ == "__main__":
    main()