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

    def _call_claude(self, system_prompt, user_message, max_tokens=1000):
        # Debug: Print the actual system prompt being used
        print(f"\n[DEBUG] System Prompt being sent to Claude:")
        print(f"[DEBUG] {system_prompt[:200]}...")
        print(f"[DEBUG] User message: {user_message}")
        
        for attempt in range(3):
            try:
                message = self.client.messages.create(
                    model=self.model,
                    max_tokens=max_tokens,
                    system=system_prompt,
                    messages=[{"role": "user", "content": user_message}]
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
            String response with financial advice
        """
        try:
            # Check if this is a follow-up response in an ongoing conversation
            if user_data and 'conversation_flow' in user_data:
                return self._handle_conversation_flow(user_message, wallet_address, user_data, vault_data, yield_data)
            
            # Detect which conversation flow to start
            flow_type = self._detect_conversation_flow(user_message)
            
            if flow_type == 'budget':
                return self._start_budget_flow(user_message, wallet_address, user_data, vault_data, yield_data)
            elif flow_type == 'yield':
                return self._handle_yield_inquiry(user_message, wallet_address, user_data, vault_data, yield_data)
            elif flow_type == 'payments':
                return self._start_payment_flow(user_message, wallet_address, user_data, vault_data, yield_data)
            elif flow_type == 'advice':
                return self._handle_advice_request(user_message, wallet_address, user_data, vault_data, yield_data)
            elif flow_type == 'gas':
                return self._handle_gas_inquiry(user_message, wallet_address, user_data, vault_data, yield_data)
            else:
                return self._handle_general_inquiry(user_message, wallet_address, user_data, vault_data, yield_data)
            
        except Exception as e:
            return f"I'm having trouble accessing your financial data right now. Error: {str(e)}"
    
    def _detect_conversation_flow(self, user_message):
        """Detect which conversation flow to use based on user message"""
        message_lower = user_message.lower()
        
        # FLOW 1 - Budget/Management
        budget_keywords = ['budget', 'manage', 'help me', 'what should i do with', 'put to work']
        if any(keyword in message_lower for keyword in budget_keywords):
            return 'budget'
        
        # FLOW 2 - Yield Inquiry
        yield_keywords = ['where is my money', 'yield', 'earning', 'apy', 'which protocol', 'protocol']
        if any(keyword in message_lower for keyword in yield_keywords):
            return 'yield'
        
        # FLOW 3 - Payment Setup
        payment_keywords = ['pay', 'send', 'payment', 'workers', 'bills', 'payroll']
        if any(keyword in message_lower for keyword in payment_keywords):
            return 'payments'
        
        # FLOW 4 - Advice Request
        advice_keywords = ['should i', 'what\'s better', 'recommend', 'best rate']
        if any(keyword in message_lower for keyword in advice_keywords):
            return 'advice'
        
        # FLOW 5 - Gas/Fees
        gas_keywords = ['gas', 'fees', 'cost', 'expensive']
        if any(keyword in message_lower for keyword in gas_keywords):
            return 'gas'
        
        return 'general'
    
    def _start_budget_flow(self, user_message, wallet_address, user_data, vault_data, yield_data):
        """FLOW 1 - Budget/Management conversation"""
        # Check if user already has payments scheduled
        has_payments = user_data and user_data.get('rules', {}).get('send_amount', 0) > 0
        
        if has_payments:
            # User already has payments - ask about allocation
            response = "Got it! I see you have payments set up. What portion of your funds is for payments vs savings?"
        else:
            # No payments yet - ask about recurring payments
            response = "Nice, let's put that to work! First question - do you have any payments coming up soon, like payroll or bills?"
        
        # Save conversation state
        conversation_state = {
            'flow': 'budget',
            'step': 1,
            'original_message': user_message
        }
        
        if user_data:
            user_data['conversation_flow'] = conversation_state
            from users.user_store import UserStore
            store = UserStore()
            store.save_user(wallet_address, user_data)
        
        return response
    
    def _handle_yield_inquiry(self, user_message, wallet_address, user_data, vault_data, yield_data):
        """FLOW 2 - Yield information response"""
        
        # Get current protocol info
        protocols = yield_data.get('protocols', {})
        data_available = yield_data.get('data_available', False)
        
        # Determine where funds are currently deployed
        current_protocol = 'Aave'  # Default for now
        current_apy = protocols.get('aave', {}).get('current_apy', 6.2)
        aave_deposit = vault_data.get('aave_deposit', 0)
        usdc_balance = vault_data.get('usdc_balance', 'unavailable')
        
        # Build response
        if not data_available or usdc_balance == 'unavailable':
            response = "I can't access your balance right now, but here are current yield rates:\n\n"
            
            # Compare with other protocols
            for name, data in protocols.items():
                withdrawal_time = data.get('withdrawal_time', 'unknown')
                response += f"  {name.title()}: {data.get('current_apy', 0)}% APY ({withdrawal_time} withdrawals)\n"
            
            response += "\nHow much USDC are you looking to put to work?"
            return response
        
        if aave_deposit > 0:
            response = f"Your {aave_deposit} USDC is in {current_protocol} earning {current_apy}% APY.\n\n"
            response += f"That's about ${aave_deposit * current_apy / 100 / 52:.2f} per week.\n\n"
        else:
            response = "Your funds aren't earning yield yet.\n\n"
        
        # Compare with other protocols
        response += "Current rates:\n"
        for name, data in protocols.items():
            withdrawal_time = data.get('withdrawal_time', 'unknown')
            response += f"  {name.title()}: {data.get('current_apy', 0)}% APY ({withdrawal_time} withdrawals)\n"
        
        response += "\nWithdrawal speed matters if you have payments coming up."
        
        return response
    
    def _start_payment_flow(self, user_message, wallet_address, user_data, vault_data, yield_data):
        """FLOW 3 - Payment setup conversation"""
        response = "Who are you paying? (workers, rent, supplier?)"
        
        # Save conversation state
        conversation_state = {
            'flow': 'payments',
            'step': 1,
            'original_message': user_message
        }
        
        if user_data:
            user_data['conversation_flow'] = conversation_state
            from users.user_store import UserStore
            store = UserStore()
            store.save_user(wallet_address, user_data)
        
        return response
    
    def _handle_advice_request(self, user_message, wallet_address, user_data, vault_data, yield_data):
        """FLOW 4 - Advice request with payment check"""
        
        # Check for upcoming payments
        has_payments = user_data and user_data.get('rules', {}).get('send_amount', 0) > 0
        
        if not has_payments:
            # Ask about upcoming payments first
            response = "Before I recommend anything - do you have any payments coming up in the next few days?"
            
            # Save conversation state
            conversation_state = {
                'flow': 'advice',
                'step': 'payment_check',
                'original_message': user_message
            }
            
            if user_data:
                user_data['conversation_flow'] = conversation_state
                from users.user_store import UserStore
                store = UserStore()
                store.save_user(wallet_address, user_data)
            
            return response
        
        # Get best rates and provide recommendation
        protocols = yield_data.get('protocols', {})
        best_rates = sorted([(name, data.get('current_apy', 0)) for name, data in protocols.items()], 
                          key=lambda x: x[1], reverse=True)
        
        # Recommend based on timing
        response = "Here are your options:\n"
        for name, apy in best_rates[:3]:
            protocol_info = protocols.get(name, {})
            withdrawal_time = protocol_info.get('withdrawal_time', 'unknown')
            response += f"  {name.title()}: {apy}% APY ({withdrawal_time})\n"
        
        response += "\nIf you have payments in less than 48 hours, stick with instant withdrawal options."
        
        return response
    
    def _handle_gas_inquiry(self, user_message, wallet_address, user_data, vault_data, yield_data):
        """FLOW 5 - Gas/fees information"""
        return "We're on Base network - gas fees are fractions of a cent. Transactions are cheap and fast (about 2 seconds). No worries about costs here."
    
    def _handle_conversation_flow(self, user_message, wallet_address, user_data, vault_data, yield_data):
        """Handle ongoing conversation flows"""
        conversation = user_data.get('conversation_flow', {})
        flow = conversation.get('flow')
        step = conversation.get('step')
        
        if flow == 'budget':
            return self._continue_budget_flow(user_message, wallet_address, user_data, vault_data, yield_data, step)
        elif flow == 'payments':
            return self._continue_payment_flow(user_message, wallet_address, user_data, vault_data, yield_data, step)
        elif flow == 'advice':
            return self._continue_advice_flow(user_message, wallet_address, user_data, vault_data, yield_data, step)
        
        return self._handle_general_inquiry(user_message, wallet_address, user_data, vault_data, yield_data)
    
    def _continue_budget_flow(self, user_message, wallet_address, user_data, vault_data, yield_data, step):
        """Continue budget conversation flow"""
        
        if step == 1:
            # User answered about payments
            if any(word in user_message.lower() for word in ['yes', 'payroll', 'rent', 'bills', 'suppliers']):
                response = "Who do you pay and when? Share the wallet address and amount if you have it."
                user_data['conversation_flow']['step'] = 2
            else:
                response = "And roughly what portion of your funds is for payments vs savings?"
                user_data['conversation_flow']['step'] = 3
                
        elif step == 2:
            # User provided payment details
            response = "And roughly what portion of your funds is for payments vs savings?"
            user_data['conversation_flow']['step'] = 3
            
        elif step == 3:
            # User provided allocation - build budget breakdown
            usdc_balance = vault_data.get('usdc_balance', 'unavailable')
            aave_deposit = vault_data.get('aave_deposit', 0)
            data_available = vault_data.get('data_available', False)
            
            # Parse percentages from user response
            import re
            percentages = re.findall(r'(\d+)%', user_message)
            
            if percentages:
                payments_pct = int(percentages[0])
                savings_pct = int(percentages[1]) if len(percentages) > 1 else 100 - payments_pct
                
                response = f"Here's your budget breakdown:\n"
                response += f"  {payments_pct}% -> payments (auto-pay scheduled)\n"
                response += f"  {savings_pct}% -> yield (earning on Aave)\n"
                response += f"  {100 - payments_pct - savings_pct}% -> liquid buffer\n\n"
                
                if data_available and usdc_balance != 'unavailable':
                    total_balance = usdc_balance + aave_deposit
                    response += f"Total balance: {total_balance} USDC"
                else:
                    response += "I'll need your balance to calculate the exact amounts. How much USDC do you have?"
            else:
                response = "Thanks! I'll keep that in mind for your budget planning."
            
            # Clear conversation state
            del user_data['conversation_flow']
        
        # Save updated state
        from users.user_store import UserStore
        store = UserStore()
        store.save_user(wallet_address, user_data)
        
        return response
    
    def _continue_payment_flow(self, user_message, wallet_address, user_data, vault_data, yield_data, step):
        """Continue payment setup conversation flow"""
        
        if step == 1:
            # User said who they're paying
            response = "What's the wallet address?"
            user_data['conversation_flow']['step'] = 2
            user_data['conversation_flow']['payment_type'] = user_message
            
        elif step == 2:
            # User provided address
            response = "How much and how often?"
            user_data['conversation_flow']['step'] = 3
            user_data['conversation_flow']['address'] = user_message
            
        elif step == 3:
            # User provided amount and frequency
            payment_type = user_data['conversation_flow'].get('payment_type', 'payment')
            address = user_data['conversation_flow'].get('address', 'address')
            
            response = f"Got it - I'll keep funds earning yield and automatically withdraw + send to {address} on schedule. Shall I activate this plan?"
            user_data['conversation_flow']['step'] = 4
        
        elif step == 4:
            # User confirmed - DON'T execute, just acknowledge
            response = "Perfect! I've noted your payment plan. When you're ready to activate it, just say 'activate payments'."
            
            # Clear conversation state
            del user_data['conversation_flow']
        
        # Save updated state
        from users.user_store import UserStore
        store = UserStore()
        store.save_user(wallet_address, user_data)
        
        return response
    
    def _continue_advice_flow(self, user_message, wallet_address, user_data, vault_data, yield_data, step):
        """Continue advice conversation flow"""
        
        if step == 'payment_check':
            # User answered about upcoming payments
            if any(word in user_message.lower() for word in ['yes', 'payment', 'bill', 'due', 'soon']):
                response = "If payment is in less than 48 hours, I recommend keeping funds liquid. If 3+ days away, yield protocols are better. When is your payment due?"
            else:
                # No upcoming payments - recommend best yield
                protocols = yield_data.get('protocols', {})
                best_protocol = max(protocols.items(), key=lambda x: x[1].get('current_apy', 0))
                name, data = best_protocol
                response = f"Since no payments are coming up, I recommend {name.title()} at {data.get('current_apy', 0)}% APY. {data.get('withdrawal_time', 'Unknown')} withdrawals."
            
            # Clear conversation state
            del user_data['conversation_flow']
        
        # Save updated state
        from users.user_store import UserStore
        store = UserStore()
        store.save_user(wallet_address, user_data)
        
        return response
    
    def _handle_general_inquiry(self, user_message, wallet_address, user_data, vault_data, yield_data):
        """Handle general inquiries that don't fit specific flows"""
        
        usdc_balance = vault_data.get('usdc_balance', 'unavailable')
        aave_deposit = vault_data.get('aave_deposit', 0)
        data_available = vault_data.get('data_available', False)
        
        if not data_available or usdc_balance == 'unavailable':
            response = "I can't access your balance right now, but I'm here to help!\n\n"
            response += "How can I help you manage your crypto? I can:\n"
            response += "  Set up automated payments\n"
            response += "  Optimize yield earnings\n"
            response += "  Create a budget plan\n"
            response += "  Track your finances\n\n"
            response += "What would you like to do? You can also tell me your balance if you know it."
        else:
            balance = usdc_balance + aave_deposit
            response = f"Your current balance: {balance} USDC\n\n"
            response += "How can I help you manage it? I can:\n"
            response += "  Set up automated payments\n"
            response += "  Optimize yield earnings\n"
            response += "  Create a budget plan\n"
            response += "  Track your finances\n\n"
            response += "What would you like to do?"
        
        return response

if __name__ == "__main__":
    brain = ButlerBrain()
    result = brain.parse_instruction(
        "Butler I have 20 USDC. Send 5 USDC to wallet 0xABC123 every Friday. Grow the rest safely.",
        "0xTEST123"
    )
    print(json.dumps(result, indent=2))
