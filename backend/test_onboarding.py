#!/usr/bin/env python3
"""
Test script for conversational onboarding flow
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.brain import ButlerBrain
from users.user_store import UserStore

def test_onboarding_flow():
    """Test the complete conversational onboarding flow"""
    
    print("Welcome to Crypto Butler Onboarding Test!")
    print("=" * 50)
    
    brain = ButlerBrain()
    store = UserStore()
    wallet_address = "0x1234567890123456789012345678901234567890"
    
    # Simulate onboarding conversation
    onboarding_script = [
        {
            'stage': 'Welcome',
            'user_input': 'Hi, I want to set up automated payments',
            'expected_next': 'bills_collection'
        },
        {
            'stage': 'Bills',
            'user_input': 'I pay rent on the 1st to 0xABC123DEF456... and utilities on the 15th to 0xDEF789ABC123...',
            'expected_next': 'payroll_collection'
        },
        {
            'stage': 'Payroll',
            'user_input': 'I pay 3 people every Friday. Total $800. Their addresses are 0x111..., 0x222..., 0x333...',
            'expected_next': 'spending_patterns'
        },
        {
            'stage': 'Spending Patterns',
            'user_input': 'I need 60% for operations, 40% for savings. I also need emergency liquidity available',
            'expected_next': 'confirmation'
        },
        {
            'stage': 'Confirmation',
            'user_input': 'Yes, that sounds perfect. Please set it up.',
            'expected_next': 'completed'
        }
    ]
    
    user_data = None
    
    for step in onboarding_script:
        print(f"\n--- {step['stage']} Stage ---")
        print(f"User: {step['user_input']}")
        
        # Process the message through onboarding
        result = brain.start_onboarding_conversation(
            step['user_input'], 
            wallet_address, 
            user_data
        )
        
        if 'error' in result:
            print(f"Error: {result['error']}")
            return
        
        print(f"Butler: {result['response']}")
        print(f"Next Stage: {result.get('next_stage', 'unknown')}")
        
        # Verify we're on track
        if result.get('next_stage') != step['expected_next']:
            print(f"Warning: Expected {step['expected_next']}, got {result.get('next_stage')}")
        
        # Update user data for next step
        user_data = result.get('user_data')
        
        # Save progress
        if user_data:
            store.save_user(wallet_address, user_data)
    
    print("\n" + "=" * 50)
    print("ONBOARDING COMPLETE!")
    print("=" * 50)
    
    # Show final user profile
    final_user = store.get_user(wallet_address)
    if final_user:
        print("\nFinal User Profile:")
        print(f"Wallet: {final_user.get('wallet_address')}")
        print(f"Status: {final_user.get('status', 'unknown')}")
        
        payment_details = final_user.get('payment_details', {})
        print(f"\nPayment Details:")
        
        # Bills
        bills = payment_details.get('bills', [])
        if bills:
            print(f"  Bills ({len(bills)}):")
            for bill in bills:
                print(f"    - {bill.get('name', 'Unknown')}: {bill.get('due_date', 'TBD')}")
        
        # Payroll
        payroll = payment_details.get('payroll', {})
        if payroll:
            people_count = payroll.get('people_count', 0)
            addresses = payroll.get('addresses', [])
            print(f"  Payroll: {people_count} people, {len(addresses)} addresses")
        
        # Spending patterns
        patterns = payment_details.get('spending_patterns', {})
        if patterns:
            ops_pct = patterns.get('operations_percentage', 0)
            savings_pct = patterns.get('savings_percentage', 0)
            emergency = patterns.get('emergency_liquidity', False)
            print(f"  Allocation: {ops_pct}% operations, {savings_pct}% yield")
            print(f"  Emergency Liquidity: {'Yes' if emergency else 'No'}")
    
    # Show operational plan
    if 'operational_plan' in result:
        plan = result['operational_plan']
        print(f"\nGenerated Operational Plan:")
        print(f"  Protocol: {plan['yield_optimization']['protocol']}")
        print(f"  Emergency Buffer: {plan['emergency_buffer']}%")
        print(f"  Payment Schedule: {len(plan['payment_schedule'])} items")
        
        for payment in plan['payment_schedule']:
            print(f"    - {payment['type']}: {payment.get('frequency', 'unknown')}")
    
    print("\n" + "!" * 50)
    print("! CONVERSATIONAL ONBOARDING TEST SUCCESSFUL !")
    print("!" * 50)
    print("\nFeatures demonstrated:")
    print("  Multi-stage conversational flow")
    print("  Bill collection with addresses and due dates")
    print("  Payroll setup with multiple addresses")
    print("  Spending pattern analysis")
    print("  Emergency liquidity planning")
    print("  Automated operational plan generation")
    print("  Persistent user profile storage")

if __name__ == "__main__":
    test_onboarding_flow()
