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
            if user_message.lower().strip() in ['yes', 'confirm', 'ok', 'sure', 'do it']:
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
                            if result.get('success'):
                                response = f"Success! {result.get('message')}"
                            else:
                                response = f"Error: {result.get('message')}"
                            
                            self.save_server_conversation_history(wallet_address, user_message, response)
                            return response
                
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
            
            # Check if this is a follow-up response in an ongoing conversation
            if user_data and 'conversation_flow' in user_data:
                response = self._handle_conversation_flow(user_message, wallet_address, user_data, vault_data, yield_data)
            else:
                # Detect which conversation flow to start
                flow_type = self._detect_conversation_flow(user_message)
                
                if flow_type == 'budget':
                    response = self._start_budget_flow(user_message, wallet_address, user_data, vault_data, yield_data)
                elif flow_type == 'yield':
                    response = self._handle_yield_inquiry(user_message, wallet_address, user_data, vault_data, yield_data)
                elif flow_type == 'payments':
                    response = self._start_payment_flow(user_message, wallet_address, user_data, vault_data, yield_data)
                elif flow_type == 'advice':
                    response = self._handle_advice_request(user_message, wallet_address, user_data, vault_data, yield_data)
                elif flow_type == 'gas':
                    response = self._handle_gas_inquiry(user_message, wallet_address, user_data, vault_data, yield_data)
                else:
                    response = self._handle_general_inquiry(user_message, wallet_address, user_data, vault_data, yield_data)
            
            # Save conversation history to server-side storage
            self.save_server_conversation_history(wallet_address, user_message, response)
            
            return response
            
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
        # Get conversation history from server-side storage
        conversation_history = self.get_server_conversation_history(wallet_address)
        
        # Check if user already has payments scheduled
        has_payments = user_data and user_data.get('rules', {}).get('send_amount', 0) > 0
        
        if has_payments:
            # User already has payments - ask about allocation
            system = """You are Crypto Butler, a friendly but professional financial assistant. You're helping a user budget their crypto funds.

Current context: User already has payments set up. Ask what portion of their funds is for payments vs savings.

Personality:
- Friendly but professional, like a smart CFO friend
- Ask ONE question at a time
- Never confirm actions you haven't executed
- Keep responses concise and actionable

Respond with just your question, no extra context."""
            
            response = self._call_claude(system, user_message, max_tokens=200, conversation_history=conversation_history)
        else:
            # No payments yet - ask about recurring payments
            system = """You are Crypto Butler, a friendly but professional financial assistant. You're helping a user budget their crypto funds.

Current context: User wants to budget their money. Ask if they have any upcoming payments like payroll or bills.

Personality:
- Friendly but professional, like a smart CFO friend
- Ask ONE question at a time
- Never confirm actions you haven't executed
- Keep responses concise and actionable

Respond with just your question, no extra context."""
            
            response = self._call_claude(system, user_message, max_tokens=200, conversation_history=conversation_history)
        
        # Save conversation state
        conversation_state = {
            'flow': 'budget',
            'step': 1,
            'original_message': user_message
        }
        
        # Ensure user_data exists and save conversation state
        if not user_data:
            user_data = {}
        
        from users.user_store import UserStore
        store = UserStore()
        
        # Get current user data to preserve conversation history
        current_user = store.get_user(wallet_address) or {}
        if 'conversation_history' in current_user:
            user_data['conversation_history'] = current_user['conversation_history']
        
        user_data['conversation_flow'] = conversation_state
        store.save_user_data(wallet_address, user_data)
        
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
        
        # Check if this is a complex payment request that needs popup
        parsed = payment_parser.parse_payment_intent(user_message)
        
        if parsed.get('requires_popup') and len(parsed.get('detected_payments', [])) > 0:
            # Generate popup data for frontend
            popup_data = payment_parser.generate_popup_data(parsed)
            
            response = {
                'type': 'payment_popup',
                'data': popup_data,
                'message': f"I detected {len(parsed['detected_payments'])} payment(s) in your message. Please review and confirm the details."
            }
            return response
        
        # Simple payment setup - continue with normal flow
        response = "Who are you paying? (workers, rent, supplier?)"
        
        # Save conversation state
        conversation_state = {
            'flow': 'payments',
            'step': 1,
            'original_message': user_message
        }
        
        # Ensure user_data exists and save conversation state
        if not user_data:
            user_data = {}
        
        from users.user_store import UserStore
        store = UserStore()
        
        # Get current user data to preserve conversation history
        current_user = store.get_user(wallet_address) or {}
        if 'conversation_history' in current_user:
            user_data['conversation_history'] = current_user['conversation_history']
        
        user_data['conversation_flow'] = conversation_state
        store.save_user_data(wallet_address, user_data)
        
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
            
            # Ensure user_data exists and save conversation state
            if not user_data:
                user_data = {}
            
            user_data['conversation_flow'] = conversation_state
            from users.user_store import UserStore
            store = UserStore()
            store.save_user_data(wallet_address, user_data)
            
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
        
        # Get conversation history from server-side storage
        conversation_history = self.get_server_conversation_history(wallet_address)
        
        if flow == 'budget':
            return self._continue_budget_flow(user_message, wallet_address, user_data, vault_data, yield_data, step, conversation_history)
        elif flow == 'payments':
            return self._continue_payment_flow(user_message, wallet_address, user_data, vault_data, yield_data, step, conversation_history)
        elif flow == 'advice':
            return self._continue_advice_flow(user_message, wallet_address, user_data, vault_data, yield_data, step, conversation_history)
        
        return self._handle_general_inquiry(user_message, wallet_address, user_data, vault_data, yield_data)
    
    def _continue_budget_flow(self, user_message, wallet_address, user_data, vault_data, yield_data, step, conversation_history):
        """Continue budget conversation flow"""
        
        if step == 1:
            # User answered about payments
            if any(word in user_message.lower() for word in ['yes', 'payroll', 'rent', 'bills', 'suppliers']):
                system = """You are Crypto Butler, continuing a budget conversation.

Current context: User confirmed they have payments. Ask who they pay and when, requesting wallet address and amount.

Personality:
- Friendly but professional, like a smart CFO friend
- Ask ONE question at a time
- Never confirm actions you haven't executed
- Keep responses concise and actionable

Respond with just your question, no extra context."""
                
                response = self._call_claude(system, user_message, max_tokens=200, conversation_history=conversation_history)
                user_data['conversation_flow']['step'] = 2
            else:
                system = """You are Crypto Butler, continuing a budget conversation.

Current context: User said no to upcoming payments. Ask what portion of their funds is for payments vs savings.

Personality:
- Friendly but professional, like a smart CFO friend
- Ask ONE question at a time
- Never confirm actions you haven't executed
- Keep responses concise and actionable

Respond with just your question, no extra context."""
                
                response = self._call_claude(system, user_message, max_tokens=200, conversation_history=conversation_history)
                user_data['conversation_flow']['step'] = 3
                
        elif step == 2:
            # User provided payment details
            system = """You are Crypto Butler, continuing a budget conversation.

Current context: User provided payment details. Ask what portion of their funds is for payments vs savings.

Personality:
- Friendly but professional, like a smart CFO friend
- Ask ONE question at a time
- Never confirm actions you haven't executed
- Keep responses concise and actionable

Respond with just your question, no extra context."""
            
            response = self._call_claude(system, user_message, max_tokens=200, conversation_history=conversation_history)
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
                    response += f"Total balance: {total_balance} USDC\n\n"
                else:
                    response += "I'll need your balance to calculate the exact amounts. How much USDC do you have?\n\n"
                
                # Ask for email for notifications
                response += "Last thing - what's your email? I'll send you notifications when payments fire and when your money moves."
                user_data['conversation_flow']['step'] = 4
            else:
                response = "Thanks! I'll keep that in mind for your budget planning."
                # Clear conversation state
                del user_data['conversation_flow']
        
        if step == 4:
            # User provided email - save it and ask about recipient emails
            import re
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            emails = re.findall(email_pattern, user_message)
            
            if emails:
                user_email = emails[0]
                # Save user email
                from notifications.notification_manager import notification_manager
                notification_manager.save_user_email(wallet_address, user_email)
                
                response = f"Perfect! I'll send notifications to {user_email}.\n\n"
                response += "Does your recipient have an email? I'll notify them when payments land."
                user_data['conversation_flow']['step'] = 5
            else:
                response = "I didn't catch that email address. Could you provide it again?"
        
        elif step == 5:
            # User provided recipient email info
            import re
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            emails = re.findall(email_pattern, user_message)
            
            if emails:
                recipient_email = emails[0]
                # Extract recipient name from conversation
                recipient_name = user_data.get('conversation_flow', {}).get('recipient_name', 'Recipient')
                
                # Save recipient email
                from notifications.notification_manager import notification_manager
                payment_info = user_data.get('conversation_flow', {})
                recipient_wallet = payment_info.get('address', 'unknown')
                
                notification_manager.save_recipient_email(
                    wallet_address, recipient_wallet, recipient_email, recipient_name
                )
                
                response = f"Great! I'll notify {recipient_name} at {recipient_email} when payments arrive.\n\n"
                response += "Your budget plan is all set! I'll keep you updated on all activity."
                
                # Clear conversation state
                del user_data['conversation_flow']
            else:
                response = "I didn't catch that email address. Could you provide it again?"
        
        # Save updated state
        from users.user_store import UserStore
        store = UserStore()
        store.save_user_data(wallet_address, user_data)
        
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
            # User confirmed - ask for email notifications
            response = "Perfect! Last thing — what's your email? I'll send you notifications when payments fire."
            user_data['conversation_flow']['step'] = 5
            
        elif step == 5:
            # User provided email - save it and ask about recipient email
            import re
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            emails = re.findall(email_pattern, user_message)
            
            if emails:
                user_email = emails[0]
                # Save user email
                from notifications.notification_manager import notification_manager
                notification_manager.save_user_email(wallet_address, user_email)
                
                response = f"Got it! I'll send notifications to {user_email}.\n\n"
                response += "Does your recipient have an email? I'll notify them when payments land."
                user_data['conversation_flow']['step'] = 6
            else:
                response = "I didn't catch that email address. Could you provide it again?"
        
        elif step == 6:
            # User provided recipient email info
            import re
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            emails = re.findall(email_pattern, user_message)
            
            if emails:
                recipient_email = emails[0]
                # Extract recipient info from conversation
                payment_info = user_data.get('conversation_flow', {})
                recipient_name = payment_info.get('payment_type', 'Recipient')
                recipient_wallet = payment_info.get('address', 'unknown')
                
                # Save recipient email
                from notifications.notification_manager import notification_manager
                notification_manager.save_recipient_email(
                    wallet_address, recipient_wallet, recipient_email, recipient_name
                )
                
                response = f"Great! I'll notify {recipient_name} at {recipient_email} when payments arrive.\n\n"
                response += "Your payment plan is all set! When you're ready to activate it, just say 'activate payments'."
                
                # Clear conversation state
                del user_data['conversation_flow']
            else:
                response = "I didn't catch that email address. Could you provide it again?"
            
            # Clear conversation state for step 4 (no email case)
            if step == 4 and 'emails' not in locals():
                del user_data['conversation_flow']
        
        # Save updated state
        from users.user_store import UserStore
        store = UserStore()
        store.save_user_data(wallet_address, user_data)
        
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
        store.save_user_data(wallet_address, user_data)
        
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
