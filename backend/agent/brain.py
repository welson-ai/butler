"""
What this file does: Claude API integration for processing user instructions
What it receives as input: User commands and context from the interface
What it returns as output: Structured actions for the executor to perform
"""

import anthropic
import os
from dotenv import load_dotenv
import json
import time

load_dotenv()

class ButlerBrain:
    def __init__(self):
        """
        Initialize ButlerBrain with Anthropic API key
        """
        self.client = anthropic.Anthropic(
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )
        self.model = "claude-sonnet-4-6"
    
    def _retry_api_call(self, func, *args, **kwargs):
        """
        Retry wrapper for API calls with exponential backoff
        """
        max_retries = 3
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except anthropic.APIError as e:
                if e.error_type == 'overloaded_error' and attempt < max_retries - 1:
                    print(f"API overloaded, retrying in 3 seconds... (attempt {attempt + 1}/{max_retries})")
                    time.sleep(3)
                    continue
                else:
                    raise e
            except Exception as e:
                raise e
        return None
    
    def parse_instruction(self, user_message, wallet_address):
        """
        Parse user instruction into structured JSON using Claude API
        """
        try:
            def _call_api():
                return self.client.messages.create(
                    model=self.model,
                    max_tokens=1000,
                    system="You are a crypto butler assistant. Extract financial instructions from user messages and return ONLY a valid JSON object with these fields: usdc_total (float), send_amount (float), send_to_address (string), send_schedule (string), risk_level (string), yield_strategy (string), buffer_amount (float). Return ONLY JSON. No explanation. No markdown.",
                    messages=[{"role": "user", "content": user_message}]
                )
            
            message = self._retry_api_call(_call_api)
            return json.loads(message.content[0].text)
        except Exception as e:
            print(f"Error parsing instruction: {e}")
            return {"error": str(e)}
    
    def generate_response(self, action_taken, user_id):
        """
        Generate friendly natural language response for completed action
        """
        try:
            def _call_api():
                return self.client.messages.create(
                    model=self.model,
                    max_tokens=200,
                    system="You are a friendly crypto butler. Summarize what you just did in 2 sentences maximum. Be warm, clear, and reassuring. No technical jargon.",
                    messages=[{"role": "user", "content": str(action_taken)}]
                )
            
            message = self._retry_api_call(_call_api)
            return message.content[0].text
        except Exception as e:
            return f"Your funds are being managed safely. Error: {str(e)}"
    
    def assess_risk(self, yield_data, user_rules):
        """
        Assess risk and provide recommendations based on yield data and user rules
        """
        try:
            def _call_api():
                return self.client.messages.create(
                    model=self.model,
                    max_tokens=500,
                    system="You are a DeFi risk analyst. Return ONLY a JSON with: recommended_protocol (string), recommended_apy (float), risk_flag (boolean), reason (string)",
                    messages=[{"role": "user", "content": f"Yield data: {yield_data}. User rules: {user_rules}"}]
                )
            
            message = self._retry_api_call(_call_api)
            return json.loads(message.content[0].text)
        except Exception as e:
            return {"error": str(e)}

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
