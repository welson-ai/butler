import anthropic
import time
import json
import os
from dotenv import load_dotenv
from .payment_parser import payment_parser
from .action_executor import action_executor

load_dotenv()

# Server-side conversation history storage
_conversation_history = {}

class ButlerBrain:
    def __init__(self):
        self.client = anthropic.Anthropic(
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )
        self.model = "claude-sonnet-4-6"
        
        # Print system prompt on startup for debugging
        print("=" * 60)
        print("CRYPTO BUTLER SYSTEM PROMPTS LOADED:")
        print("=" * 60)
        print("1. Budget/Management Flow - Friendly CFO personality")
        print("2. Yield Inquiry Flow - Real APY data with withdrawal times")
        print("3. Payment Setup Flow - Step-by-step payment configuration")
        print("4. Advice Request Flow - Payment timing checks first")
        print("5. Gas/Fees Flow - Base network awareness (cents, not $)")
        print("=" * 60)
    
    def get_server_conversation_history(self, wallet_address):
        """Get conversation history from server-side storage"""
        global _conversation_history
        return _conversation_history.get(wallet_address, [])
    
    def save_server_conversation_history(self, wallet_address, user_message, assistant_response):
        """Save conversation history to server-side storage"""
        global _conversation_history
        
        if wallet_address not in _conversation_history:
            _conversation_history[wallet_address] = []
        
        # Add new messages to history
        _conversation_history[wallet_address].append({
            "role": "user", 
            "content": user_message
        })
        _conversation_history[wallet_address].append({
            "role": "assistant", 
            "content": assistant_response
        })
        
        # Keep only last 20 messages to avoid token limits
        if len(_conversation_history[wallet_address]) > 20:
            _conversation_history[wallet_address] = _conversation_history[wallet_address][-20:]
        
        # Also save to database for persistence
        self.save_conversation_history(wallet_address, user_message, assistant_response)

    def _call_claude(self, system_prompt, user_message, max_tokens=1000, conversation_history=None):
        # Debug: Print the actual system prompt being used
        print(f"\n[DEBUG] System Prompt being sent to Claude:")
        print(f"[DEBUG] {system_prompt[:200]}...")
        print(f"[DEBUG] User message: {user_message}")
        print(f"[DEBUG] Conversation history: {len(conversation_history) if conversation_history else 0} messages")
        
        # Build messages array with conversation history
        messages = []
        if conversation_history:
            messages.extend(conversation_history)
        messages.append({"role": "user", "content": user_message})
        
        for attempt in range(3):
            try:
                message = self.client.messages.create(
                    model=self.model,
                    max_tokens=max_tokens,
                    system=system_prompt,
                    messages=messages
                )
                result = message.content[0].text
                print(f"[DEBUG] Claude response: {result[:200]}...")
                return result
            except anthropic.OverloadedError:
                print(f"Claude overloaded. Attempt {attempt + 1}/3. Waiting 3 seconds...")
                time.sleep(3)
            except Exception as e:
                raise e
        raise Exception("Claude API overloaded after 3 attempts")
    
    def get_conversation_history(self, wallet_address):
        """Get conversation history for a user"""
        from users.user_store import UserStore
        store = UserStore()
        user = store.get_user(wallet_address)
        return user.get('conversation_history', []) if user else []
    
    def save_conversation_history(self, wallet_address, user_message, assistant_response):
        """Save conversation history for a user"""
        from users.user_store import UserStore
        store = UserStore()
        user = store.get_user(wallet_address) or {}
        
        if 'conversation_history' not in user:
            user['conversation_history'] = []
        
        # Add new messages to history
        user['conversation_history'].append({
            "role": "user", 
            "content": user_message
        })
        user['conversation_history'].append({
            "role": "assistant", 
            "content": assistant_response
        })
        
        # Keep only last 20 messages to avoid token limits
        if len(user['conversation_history']) > 20:
            user['conversation_history'] = user['conversation_history'][-20:]
        
        # Preserve other user data like conversation_flow
        updated_user = user.copy()
        store.save_user_data(wallet_address, updated_user)

    def parse_instruction(self, user_message, wallet_address):
        try:
            system = """You are a crypto butler assistant.
You ONLY manage exactly what user gives you - never more.
Read instructions precisely and literally.

Rules:
- usdc_total = ONLY amount user explicitly gives you to manage
- If user says "take 3 USDC" then usdc_total = 3 NOT their total wallet balance
- If user says "don't touch the rest" then only manage what they gave you
- If user does not mention yield or growing money then yield_requested = false
- Extract payment interval in seconds from natural language:
  "every 10 seconds" = 10
  "every minute" = 60
  "every friday" = 604800
  "every day" = 86400
  "every month" = 2592000
- Extract total duration if mentioned:
  "for 30 seconds" = 30
  "for 1 week" = 604800
  "forever" = -1

Return ONLY this exact JSON - no markdown no backticks:
{
    "usdc_total": <float - ONLY what user gave you>,
    "send_amount": <float>,
    "send_to_address": "<string>",
    "interval_seconds": <int - payment frequency in seconds>,
    "duration_seconds": <int - total run time, -1 if forever>,
    "risk_level": "<conservative|moderate|aggressive>",
    "yield_requested": <boolean - only true if user explicitly asked to grow money>,
    "yield_strategy": "<aave_lending|none>",
    "buffer_amount": <float - 10 percent of usdc_total, or 0 if no yield requested>
}"""
            result = self._call_claude(system, user_message)
            print(f"DEBUG raw claude response: {repr(result)}")
            result = result.strip()
            if result.startswith("```"):
                result = result.split("```")[1]
                if result.startswith("json"):
                    result = result[4:]
            result = result.strip()
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
    
    def get_financial_advice(self, user_message, wallet_address, user_data, vault_data, yield_data):
        """
        Provide financial advice following specific conversation flows
        
        Args:
            user_message: The user's question
            wallet_address: User's wallet address
            user_data: User's plan and rules
            vault_data: Current vault balances and status
            yield_data: Current yield rates and protocol data
            
        Returns:
            String response with financial advice or action response
        """
        try:
            # FIRST: Check for action confirmations (yes/no responses)
            confirmations = ['yes', 'confirm', 'ok', 'sure', 'do it', 'yeah', 'yep', 'yeas', 'yas', 'y']
            if user_message.lower().strip() in confirmations:
                # Check if there was a recent action in conversation history
                history = self.get_server_conversation_history(wallet_address)
                recent_messages = history[-4:] if len(history) >= 4 else history
                
                # Look for recent action response
                for msg in reversed(recent_messages):
                    if msg.get('role') == 'assistant' and isinstance(msg.get('content'), dict):
                        # Found a pending action, execute it
                        action = msg.get('content', {}).get('action')
                        if action:
                            result = action_executor.execute_action(action, wallet_address)
                            
                            self.save_server_conversation_history(wallet_address, user_message, result)
                            return result
                
                # No pending action found, proceed with normal flow
                pass
            
            # SECOND: Check for clear action intents
            action = action_executor.parse_action_intent(user_message, wallet_address)
            if action:
                # Return structured action response for frontend
                action_response = action_executor.format_action_response(action)
                # Validate response format to prevent frontend crashes
                if not isinstance(action_response, dict):
                    action_response = {
                        'message': action_response if isinstance(action_response, str) else str(action_response),
                        'action': None
                    }
                # Ensure required fields exist
                if 'message' not in action_response:
                    action_response['message'] = 'Action ready to execute.'
                if 'action' not in action_response:
                    action_response['action'] = action
                
                # Save conversation history - store full action response for confirmation tracking
                self.save_server_conversation_history(wallet_address, user_message, action_response)
                return action_response
            
            # Get conversation history from server-side storage
            conversation_history = self.get_server_conversation_history(wallet_address)
            
            # All messages go to Claude - no conversation flow interception
            # Removed all hardcoded conversation flow logic
            response = self._handle_general_inquiry(user_message, wallet_address, user_data, vault_data, yield_data)
            
            # Save conversation history to server-side storage
            self.save_server_conversation_history(wallet_address, user_message, response)
            
            return response
            
        except Exception as e:
            return f"I'm having trouble accessing your financial data right now. Error: {str(e)}"
    
    def _handle_general_inquiry(self, user_message, wallet_address, user_data, vault_data, yield_data):
        """Handle general inquiries - all messages go to Claude"""
        system = "You are Crypto Butler, a friendly but professional financial assistant. You're helping a user with their crypto funds."
        
        response = self._call_claude(system, user_message, max_tokens=200, conversation_history=self.get_server_conversation_history(wallet_address))
        
        return response
    
