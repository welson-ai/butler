"""
What this file does: Converts user instructions into executable automation rules
What it receives as input: Natural language instructions and user context
What it returns as output: Structured automation rules and action plans
"""

import json
import os
from datetime import datetime

class RulesEngine:
    def __init__(self):
        """
        Initialize RulesEngine
        """
        pass
    
    def build_plan(self, parsed_instruction: dict, wallet_address: str) -> dict:
        """
        Build operational plan from parsed instruction
        
        Args:
            parsed_instruction: JSON output from brain.py
            wallet_address: User's wallet address
            
        Returns:
            Operational plan dictionary with calculated buckets
        """
        try:
            usdc_total = float(parsed_instruction.get('usdc_total', 0))
            send_amount = float(parsed_instruction.get('send_amount', 0))
            buffer_amount = float(parsed_instruction.get('buffer_amount', 0))
            
            # If buffer is zero default to 10% of total
            if buffer_amount == 0:
                buffer_amount = round(usdc_total * 0.1, 2)
            
            aave_deposit = round(usdc_total - send_amount - buffer_amount, 2)
            
            # Safety check — aave deposit cannot be negative
            if aave_deposit < 0:
                aave_deposit = 0
                buffer_amount = round(usdc_total - send_amount, 2)
            
            plan = {
                'wallet_address': wallet_address,
                'usdc_total': usdc_total,
                'aave_deposit': aave_deposit,
                'payment_reserve': send_amount,
                'buffer': buffer_amount,
                'send_to_address': parsed_instruction.get('send_to_address', ''),
                'send_to': parsed_instruction.get('send_to_address', ''),
                'send_amount': send_amount,
                'send_schedule': parsed_instruction.get('send_schedule', 'weekly'),
                'risk_level': parsed_instruction.get('risk_level', 'moderate'),
                'yield_strategy': parsed_instruction.get('yield_strategy', 'aave_lending'),
                'created_at': datetime.now().isoformat(),
                'status': 'active'
            }
            return plan
        except Exception as e:
            raise ValueError(f"Failed to build plan: {str(e)}")
    
    def get_next_payment_day(self, schedule: str) -> int:
        """
        Calculate test cycles until next payment
        
        Args:
            schedule: Payment schedule string
            
        Returns:
            Number of test cycles (1 cycle = 1 day)
        """
        schedule_map = {
            'friday': 7,
            'monday': 7,
            'first_of_month': 30,
            'daily': 1
        }
        
        return schedule_map.get(schedule.lower(), 7)  # Default to weekly
    
    def validate_plan(self, plan: dict) -> bool:
        """
        Validate operational plan
        
        Args:
            plan: Operational plan to validate
            
        Returns:
            True if valid, raises ValueError if not
        """
        if plan.get('aave_deposit', 0) <= 0:
            raise ValueError("Aave deposit must be greater than zero")
        if not plan.get('send_to_address') and not plan.get('send_to'):
            raise ValueError("Recipient address is required")
        return True

# Test at bottom
if __name__ == "__main__":
    try:
        engine = RulesEngine()
        
        # Sample parsed instruction matching brain.py output
        sample_instruction = {
            "usdc_total": 20.0,
            "send_amount": 5.0,
            "send_to_address": "0xABC123",
            "send_schedule": "friday",
            "risk_level": "conservative",
            "yield_strategy": "aave_lending",
            "buffer_amount": 2.0
        }
        
        # Build plan
        plan = engine.build_plan(sample_instruction, "0xTEST123")
        
        # Validate plan
        engine.validate_plan(plan)
        
        # Print result cleanly
        print("Plan Result:")
        print(json.dumps(plan, indent=2))
        
        # Test next payment day calculation
        next_payment = engine.get_next_payment_day(plan['send_schedule'])
        print(f"\nNext payment in {next_payment} test cycles")
        
    except Exception as e:
        print(f"Test failed: {e}")
