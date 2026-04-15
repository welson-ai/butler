#!/usr/bin/env python3
"""
Test script for real-time yield session functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.yield_monitor import YieldMonitor
from protocols.mock_yields import MockYieldEngine
from datetime import datetime

def test_yield_session():
    """Test the real-time yield session tracking"""
    
    # Initialize components
    yield_monitor = YieldMonitor()
    yield_engine = MockYieldEngine()
    
    print("📊 REAL-TIME YIELD SESSION TEST")
    print("=" * 50)
    
    # Test user data
    wallet_address = "0x1234567890123456789012345678901234567890"
    deposit_amount = 75.0
    protocol = "aave"
    current_apy = 6.2
    
    print(f"🏦 Testing yield session for {deposit_amount} USDC in {protocol}")
    print(f"📈 Current APY: {current_apy}%")
    print()
    
    # Test real-time earnings calculation
    earnings_data = yield_monitor.calculate_real_time_earnings(
        wallet_address, deposit_amount, protocol, current_apy
    )
    
    print("💰 REAL-TIME EARNINGS BREAKDOWN:")
    print("-" * 40)
    print(f"Deposit Amount: {earnings_data['deposit_amount']} USDC")
    print(f"Protocol: {earnings_data['protocol']}")
    print(f"Current APY: {earnings_data['current_apy']}%")
    print(f"Time Elapsed: {earnings_data['days_elapsed']} days ({earnings_data['hours_elapsed']} hours)")
    print()
    
    print("📊 EARNINGS:")
    print(f"So Far: ${earnings_data['earnings_so_far']:.4f} USDC")
    print(f"Daily: ${earnings_data['daily_earnings']:.4f} USDC")
    print(f"Monthly: ${earnings_data['monthly_earnings']:.2f} USDC")
    print(f"Yearly: ${earnings_data['yearly_earnings']:.2f} USDC")
    print()
    
    print("⏱️ REAL-TIME RATES:")
    print(f"Per Second: ${earnings_data['daily_earnings']/86400:.8f} USDC")
    print(f"Per Minute: ${earnings_data['daily_earnings']/1440:.6f} USDC")
    print(f"Per Hour: ${earnings_data['daily_earnings']/24:.4f} USDC")
    print()
    
    # Test with different time scenarios
    print("🕒 TIME PROJECTIONS:")
    print("-" * 30)
    
    scenarios = [
        (1, "1 hour from now"),
        (24, "1 day from now"),
        (168, "1 week from now"),
        (720, "1 month from now")
    ]
    
    for hours, description in scenarios:
        future_earnings = deposit_amount * (current_apy / 100 / 365) * (hours / 24)
        print(f"{description}: ${future_earnings:.2f} USDC")
    
    print()
    
    # Test yield session data aggregation
    deposit_data = {
        'aave_deposit': deposit_amount,
        'protocol': protocol
    }
    
    current_rates = yield_engine.get_current_yields()
    session_data = yield_monitor.get_yield_session_data(wallet_address, deposit_data, current_rates)
    
    print("📋 SESSION SUMMARY:")
    print("-" * 25)
    print(f"Total Deposited: {session_data['total_deposited']} USDC")
    print(f"Total Earnings: {session_data['total_earnings']:.4f} USDC")
    print(f"Session Start: {session_data['session_start']}")
    print(f"Last Updated: {session_data['last_updated']}")
    print()
    
    print("🎯 EXAMPLE RESPONSE FOR FRONTEND:")
    print("-" * 45)
    print("Your funds are currently in Aave earning 6.2% APY.")
    print(f"Deposited: {deposit_amount} USDC")
    print(f"Earned so far: {session_data['total_earnings']:.4f} USDC")
    print(f"Daily earnings: ${earnings_data['daily_earnings']:.4f} USDC")
    print("Real-time tracking active - earnings update every second! 🚀")

if __name__ == "__main__":
    test_yield_session()
