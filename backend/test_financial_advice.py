#!/usr/bin/env python3
"""
Test script for enhanced financial advice functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.brain import ButlerBrain
from protocols.mock_yields import MockYieldEngine
from users.user_store import UserStore

def test_financial_advice():
    """Test the enhanced financial advice capabilities"""
    
    # Initialize components
    brain = ButlerBrain()
    yield_engine = MockYieldEngine()
    user_store = UserStore()
    
    # Test data
    wallet_address = "0x1234567890123456789012345678901234567890"
    
    # Mock user data
    user_data = {
        "wallet_address": wallet_address,
        "rules": {
            "send_amount": 10,
            "interval_seconds": 604800,  # weekly
            "risk_level": "moderate"
        },
        "aave_deposit": 75,
        "payment_reserve": 10,
        "buffer": 15
    }
    
    # Mock vault data
    vault_data = {
        'usdc_balance': 25.5,
        'vault_balance': 75.0,
        'aave_deposit': 75.0,
        'payment_reserve': 10.0,
        'buffer': 15.0,
        'yield_earned': 2.35
    }
    
    # Get yield data
    yield_data = yield_engine.get_all_yields()
    
    print("🧠 ENHANCED CRYPTO BUTLER FINANCIAL ADVICE TEST")
    print("=" * 50)
    
    # Test different types of questions
    test_questions = [
        "Should I keep earning yield or withdraw now?",
        "Where is my money right now?",
        "What's the best protocol for my situation?",
        "How much am I earning daily?",
        "Is Aave safe for my weekly payments?"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n📝 Question {i}: {question}")
        print("-" * 40)
        
        try:
            response = brain.get_financial_advice(
                question, 
                wallet_address, 
                user_data, 
                vault_data, 
                yield_data
            )
            print(f"💬 Butler Response: {response}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print()
    
    print("📊 Current Yield Data:")
    print("-" * 30)
    for protocol, data in yield_data["protocols"].items():
        print(f"{protocol}: {data['current_apy']}% APY ({data['risk']} risk)")
    
    print(f"\n📈 Market Summary:")
    print(f"Average APY: {yield_data['market_summary']['average_apy']}%")
    print(f"Highest APY: {yield_data['market_summary']['highest_apy']}%")
    print(f"Lowest APY: {yield_data['market_summary']['lowest_apy']}%")

if __name__ == "__main__":
    test_financial_advice()
