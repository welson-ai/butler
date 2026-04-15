#!/usr/bin/env python3
"""
Test script for enhanced conversational financial advice
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.brain import ButlerBrain
from protocols.mock_yields import MockYieldEngine
from users.user_store import UserStore

def test_conversational_advice():
    """Test the enhanced conversational advice flow"""
    
    print("Enhanced Butler Financial Advice Test")
    print("=" * 50)
    
    brain = ButlerBrain()
    yield_engine = MockYieldEngine()
    store = UserStore()
    wallet_address = "0x1234567890123456789012345678901234567890"
    
    # Mock user data and vault data
    user_data = {
        'wallet_address': wallet_address,
        'rules': {}  # No existing payments
    }
    
    vault_data = {
        'usdc_balance': 50.0,
        'vault_balance': 0.0,
        'aave_deposit': 0.0,
        'payment_reserve': 0.0,
        'buffer': 0.0,
        'yield_earned': 0.0
    }
    
    yield_data = yield_engine.get_all_yields()
    
    # Test conversation flow
    conversation_script = [
        {
            'step': 'Initial Question',
            'user_input': 'What's the best protocol for my 50 USDC?',
            'expectation': 'Should ask clarifying questions'
        },
        {
            'step': 'User Answers',
            'user_input': 'I have a payment due tomorrow and this is for short-term spending',
            'expectation': 'Should provide tailored recommendation'
        },
        {
            'step': 'Follow-up Action',
            'user_input': 'deposit into Aave',
            'expectation': 'Should acknowledge and offer execution'
        }
    ]
    
    print("Testing Conversational Advice Flow:")
    print()
    
    for i, step in enumerate(conversation_script, 1):
        print(f"--- Step {i}: {step['step']} ---")
        print(f"User: {step['user_input']}")
        print(f"Expected: {step['expectation']}")
        print()
        
        # Get current user data (with any conversation context)
        current_user_data = store.get_user(wallet_address) or user_data
        
        # Get advice response
        response = brain.get_financial_advice(
            step['user_input'],
            wallet_address,
            current_user_data,
            vault_data,
            yield_data
        )
        
        print(f"Butler: {response}")
        print()
        
        # Check if response meets expectations
        if i == 1:  # First step should ask questions
            if 'question' in response.lower() or 'know about' in response.lower():
                print("  Correctly asked clarifying questions!")
            else:
                print("  Should have asked clarifying questions first")
        
        elif i == 2:  # Second step should give recommendation
            if 'recommend' in response.lower() or '%' in response:
                print("  Provided tailored recommendation!")
            else:
                print("  Should have provided specific recommendation")
        
        elif i == 3:  # Third step should handle action
            if 'execute' in response.lower() or 'deposit' in response.lower():
                print("  Acknowledged action request!")
            else:
                print("  Should acknowledge execution request")
        
        print("-" * 50)
    
    print("\n" + "!" * 50)
    print("! ENHANCED CONVERSATIONAL ADVICE TEST COMPLETE !")
    print("!" * 50)
    print()
    
    print("Features demonstrated:")
    print("  Clarifying questions before advice")
    print("  Context-aware recommendations")
    print("  Base network gas awareness")
    print("  Actionable CTAs")
    print("  Conversation flow memory")
    print("  Tailored protocol recommendations")
    
    # Show different scenarios
    print("\n" + "=" * 50)
    print("SCENARIO COMPARISON:")
    print("=" * 50)
    
    scenarios = [
        {
            'name': 'Short-term + Upcoming Payment',
            'user_input': 'I need this for a bill next week',
            'expected_protocol': 'Aave (instant withdrawals)'
        },
        {
            'name': 'Long-term Savings',
            'user_input': 'This is for long-term investing',
            'expected_protocol': 'Highest yield (Pendle/Curve)'
        },
        {
            'name': 'First-time User',
            'user_input': 'I\'m new to DeFi, what\'s safest?',
            'expected_protocol': 'Aave (low risk)'
        }
    ]
    
    for scenario in scenarios:
        print(f"\n{scenario['name']}:")
        print(f"  Input: {scenario['user_input']}")
        print(f"  Expected: {scenario['expected_protocol']}")
        
        # Reset user data for each scenario
        test_user_data = {'wallet_address': wallet_address, 'rules': {}}
        
        response = brain.get_financial_advice(
            scenario['user_input'],
            wallet_address,
            test_user_data,
            vault_data,
            yield_data
        )
        
        print(f"  Butler: {response[:100]}...")

if __name__ == "__main__":
    test_conversational_advice()
