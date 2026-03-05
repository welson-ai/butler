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
        try:
            usdc_total = float(parsed_instruction.get('usdc_total', 0))
            send_amount = float(parsed_instruction.get('send_amount', 0))
            yield_requested = parsed_instruction.get('yield_requested', False)
            interval_seconds = int(parsed_instruction.get('interval_seconds', 86400))
            duration_seconds = int(parsed_instruction.get('duration_seconds', -1))

            if yield_requested:
                buffer_amount = round(usdc_total * 0.1, 2)
                aave_deposit = round(usdc_total - send_amount - buffer_amount, 2)
            else:
                buffer_amount = 0
                aave_deposit = 0

            plan = {
                'wallet_address': wallet_address,
                'usdc_total': usdc_total,
                'aave_deposit': aave_deposit,
                'payment_reserve': send_amount,
                'buffer': buffer_amount,
                'send_to_address': parsed_instruction.get('send_to_address', ''),
                'send_to': parsed_instruction.get('send_to_address', ''),
                'send_amount': send_amount,
                'interval_seconds': interval_seconds,
                'duration_seconds': duration_seconds,
                'yield_requested': yield_requested,
                'risk_level': parsed_instruction.get('risk_level', 'moderate'),
                'yield_strategy': 'aave_lending' if yield_requested else 'none',
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
    
    def validate_plan(self, plan):
        if not plan.get('send_to_address'):
            raise ValueError("Recipient address is required")
        if plan.get('send_amount', 0) <= 0:
            raise ValueError("Send amount must be greater than zero")
        if plan.get('usdc_total', 0) <= 0:
            raise ValueError("USDC total must be greater than zero")
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
