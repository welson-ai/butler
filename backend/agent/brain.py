"""
What this file does: Claude API integration for processing user instructions
What it receives as input: User commands and context from the interface
What it returns as output: Structured actions for the executor to perform
"""

import anthropic
import time
import json
import os
from dotenv import load_dotenv

load_dotenv()

class ButlerBrain:
    def __init__(self):
        self.client = anthropic.Anthropic(
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )
        self.model = "claude-sonnet-4-6"

    def _call_claude(self, system_prompt, user_message, max_tokens=1000):
        for attempt in range(3):
            try:
                message = self.client.messages.create(
                    model=self.model,
                    max_tokens=max_tokens,
                    system=system_prompt,
                    messages=[{"role": "user", "content": user_message}]
                )
                return message.content[0].text
            except anthropic.OverloadedError:
                print(f"Claude overloaded. Attempt {attempt + 1}/3. Waiting 3 seconds...")
                time.sleep(3)
            except Exception as e:
                raise e
        raise Exception("Claude API overloaded after 3 attempts")

    def parse_instruction(self, user_message, wallet_address):
        try:
            system = "You are a crypto butler assistant. Extract financial instructions from user messages and return ONLY a valid JSON object with these fields: usdc_total (float), send_amount (float), send_to_address (string), send_schedule (string), risk_level (string), yield_strategy (string), buffer_amount (float). Return ONLY JSON. No explanation. No markdown."
            result = self._call_claude(system, user_message)
            return json.loads(result)
        except Exception as e:
            print(f"Error parsing instruction: {e}")
            return {"error": str(e)}

    def generate_response(self, action_taken, user_id):
        try:
            system = "You are a friendly crypto butler. Summarize what you just did in 2 sentences maximum. Be warm, clear, and reassuring. No technical jargon."
            return self._call_claude(system, str(action_taken), max_tokens=200)
        except Exception as e:
            return "Your funds are being managed safely."

    def assess_risk(self, yield_data, user_rules):
        try:
            system = "You are a DeFi risk analyst. Return ONLY a JSON with: recommended_protocol (string), recommended_apy (float), risk_flag (boolean), reason (string)"
            result = self._call_claude(system, f"Yield data: {yield_data}. User rules: {user_rules}")
            return json.loads(result)
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
