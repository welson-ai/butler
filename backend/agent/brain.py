"""
What this file does: Claude API integration for processing user instructions
What it receives as input: User commands and context from the interface
What it returns as output: Structured actions for the executor to perform
"""

import anthropic
import os
from dotenv import load_dotenv
import json

load_dotenv()

class ButlerBrain:
    def __init__(self, api_key: str = None):
        """
        Initialize ButlerBrain with Anthropic API key
        
        Args:
            api_key: Anthropic API key (defaults to environment variable)
        """
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")
        self.client = anthropic.Anthropic(api_key=self.api_key)
    
    def parse_instruction(self, user_message: str, wallet_address: str) -> dict:
        """
        Parse user instruction into structured JSON using Claude API
        
        Args:
            user_message: User's natural language instruction
            wallet_address: User's wallet address for context
            
        Returns:
            Structured JSON object with extracted instructions
        """
        try:
            system_prompt = """You are a crypto butler assistant. Extract financial instructions from user messages and return ONLY a valid JSON object with these fields: usdc_total (float), send_amount (float), send_to_address (string), send_schedule (string — daily/weekly/monday/friday/first_of_month), risk_level (string — conservative/moderate/aggressive), yield_strategy (string — simple description), buffer_amount (float — always 10% of total). If any field is unclear use these defaults: risk_level=moderate, buffer_amount=10% of total, yield_strategy=aave_lending. Return ONLY the JSON. No explanation. No markdown."""
            
            response = self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1000,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_message}
                ]
            )
            
            # Extract and parse JSON response
            content = response.content[0].text.strip()
            if content.startswith('```json'):
                content = content.replace('```json', '').replace('```', '').strip()
            
            parsed_json = json.loads(content)
            return parsed_json
            
        except Exception as e:
            print(f"Error parsing instruction: {e}")
            return {
                "usdc_total": 0,
                "send_amount": 0,
                "send_to_address": "",
                "send_schedule": "weekly",
                "risk_level": "moderate",
                "yield_strategy": "aave_lending",
                "buffer_amount": 0,
                "error": str(e)
            }
    
    def generate_response(self, action_taken: str, user_id: str) -> str:
        """
        Generate friendly natural language response for completed action
        
        Args:
            action_taken: Description of action that was completed
            user_id: User's unique identifier
            
        Returns:
            Natural language response string
        """
        try:
            system_prompt = "You are a friendly crypto butler. Summarize what you just did in 2 sentences maximum. Be warm, clear, and reassuring. No technical jargon."
            
            response = self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=200,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": f"I just completed this action: {action_taken}"}
                ]
            )
            
            return response.content[0].text.strip()
            
        except Exception as e:
            print(f"Error generating response: {e}")
            return f"I've completed your request. Your crypto is working for you."
    
    def assess_risk(self, yield_data: dict, user_rules: dict) -> dict:
        """
        Assess risk and provide recommendations based on yield data and user rules
        
        Args:
            yield_data: Current yield data from protocols
            user_rules: User's risk preferences and rules
            
        Returns:
            Risk assessment JSON with recommendations
        """
        try:
            system_prompt = "You are a DeFi risk analyst. Given current yield rates and user risk profile, return ONLY a JSON with: recommended_protocol (string), recommended_apy (float), risk_flag (boolean), reason (string)"
            
            user_context = f"Current yields: {json.dumps(yield_data)}\nUser rules: {json.dumps(user_rules)}"
            
            response = self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=500,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_context}
                ]
            )
            
            content = response.content[0].text.strip()
            if content.startswith('```json'):
                content = content.replace('```json', '').replace('```', '').strip()
            
            return json.loads(content)
            
        except Exception as e:
            print(f"Error assessing risk: {e}")
            return {
                "recommended_protocol": "aave",
                "recommended_apy": 5.0,
                "risk_flag": False,
                "reason": "Using default safe option due to analysis error",
                "error": str(e)
            }

# Test at bottom
if __name__ == "__main__":
    try:
        brain = ButlerBrain()
        test_message = "Butler I have 20 USDC. Send 5 USDC to wallet 0xABC123 every Friday. Grow the rest safely."
        result = brain.parse_instruction(test_message, "0xTEST123")
        print("Test Result:")
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"Test failed: {e}")
        print("Make sure ANTHROPIC_API_KEY is set in your .env file")
