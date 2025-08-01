#!/usr/bin/env python3
"""
Test script for the funding rate monitor
"""

import json
import requests
from datetime import datetime
from funding_rate_monitor import BinanceFundingRateMonitor

def test_binance_api():
    """Test Binance API connection"""
    print("🧪 Testing Binance API connection...")
    
    try:
        url = "https://fapi.binance.com/fapi/v1/premiumIndex"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        print(f"✅ Binance API connection successful")
        print(f"📊 Retrieved {len(data)} contracts")
        
        # Show some sample data
        if data:
            sample = data[0]
            print(f"📋 Sample contract: {sample.get('symbol', 'N/A')}")
            print(f"💰 Sample funding rate: {sample.get('lastFundingRate', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Binance API connection failed: {e}")
        return False

def test_funding_rate_filtering():
    """Test funding rate filtering logic"""
    print("\n🧪 Testing funding rate filtering...")
    
    # Create monitor instance
    monitor = BinanceFundingRateMonitor()
    
    # Get funding rates
    funding_data = monitor.get_funding_rates()
    if not funding_data:
        print("❌ No funding data available for testing")
        return False
    
    # Test filtering
    perpetual_contracts = monitor.filter_perpetual_contracts(funding_data)
    
    print(f"📊 Total contracts: {len(funding_data)}")
    print(f"📉 Contracts below threshold ({monitor.threshold}): {len(perpetual_contracts)}")
    
    if perpetual_contracts:
        print("\n📋 Contracts below threshold:")
        for contract in perpetual_contracts[:5]:  # Show first 5
            symbol = contract['symbol']
            rate = contract['funding_rate']
            print(f"   {symbol}: {rate:.4f} ({rate*100:.2f}%)")
    
    return True

def test_message_formatting():
    """Test message formatting"""
    print("\n🧪 Testing message formatting...")
    
    # Create monitor instance
    monitor = BinanceFundingRateMonitor()
    
    # Mock data for testing
    mock_contracts = [
        {
            'symbol': 'BTCUSDT',
            'funding_rate': -0.0523,
            'mark_price': '42350.50',
            'next_funding_time': '1642233600000',
            'index_price': '42345.20'
        },
        {
            'symbol': 'ETHUSDT',
            'funding_rate': -0.0612,
            'mark_price': '2580.75',
            'next_funding_time': '1642233600000',
            'index_price': '2578.90'
        }
    ]
    
    # Test message formatting
    message = monitor.format_message(mock_contracts)
    print("📱 Formatted message preview:")
    print("-" * 50)
    print(message)
    print("-" * 50)
    
    return True

def test_telegram_connection():
    """Test Telegram bot connection (if configured)"""
    print("\n🧪 Testing Telegram connection...")
    
    monitor = BinanceFundingRateMonitor()
    
    if not monitor.bot_token:
        print("⚠️  TELEGRAM_BOT_TOKEN not configured - skipping Telegram test")
        return True
    
    if not monitor.chat_id:
        print("⚠️  TELEGRAM_CHAT_ID not configured - skipping Telegram test")
        return True
    
    try:
        # Test with a simple message
        test_message = f"🧪 Test message from funding rate monitor\n⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        success = monitor.send_telegram_message(test_message)
        
        if success:
            print("✅ Telegram connection test successful")
        else:
            print("❌ Telegram connection test failed")
        
        return success
        
    except Exception as e:
        print(f"❌ Telegram connection test error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Funding Rate Monitor Test Suite")
    print("=" * 50)
    
    tests = [
        ("Binance API Connection", test_binance_api),
        ("Funding Rate Filtering", test_funding_rate_filtering),
        ("Message Formatting", test_message_formatting),
        ("Telegram Connection", test_telegram_connection),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n📊 Test Results Summary")
    print("=" * 30)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! Your bot is ready to use.")
    else:
        print("⚠️  Some tests failed. Please check your configuration.")

if __name__ == "__main__":
    main()