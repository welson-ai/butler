"""
What this file does: Defines all Flask API endpoints for frontend communication
What it receives as input: HTTP requests from frontend
What it returns as output: JSON responses with data and status
"""

from flask import Flask, request, jsonify, Blueprint
from flask_cors import CORS
from typing import Dict, Any
import sys
import os
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agent.brain import ButlerBrain
from users.rules_engine import RulesEngine
from users.user_store import UserStore
from agent.executor import ButlerExecutor
from agent.payment_parser import payment_parser
from agent.action_executor import action_executor
from protocols.mock_yields import MockYieldEngine
from protocols.aave import AaveProtocol

# Create Flask Blueprint
api = Blueprint('api', __name__)

# Initialize components
brain = ButlerBrain()
rules_engine = RulesEngine()
user_store = UserStore()
executor = ButlerExecutor()
yield_engine = MockYieldEngine()
aave = AaveProtocol()

@api.route('/api/chat', methods=['POST'])
def chat():
    """
    Chat endpoint for processing user messages
    """
    try:
        data = request.get_json()
        wallet_address = data.get('wallet_address')
        message = data.get('message')
        
        brain = ButlerBrain()
        rules = RulesEngine()
        store = UserStore()
        
        # Get user data for conversation context
        user = store.get_user(wallet_address)
        
        # Check if this is a setup instruction (old flow) or conversational (new flow)
        setup_keywords = ['have', 'send', 'every', 'grow', 'deposit', 'pay']
        is_setup_instruction = any(keyword in message.lower() for keyword in setup_keywords)
        
        if is_setup_instruction:
            # Use old setup flow for explicit instructions
            parsed = brain.parse_instruction(message, wallet_address)
            print(f"DEBUG parsed: {parsed}")
            
            if 'error' in parsed or parsed.get('usdc_total', 0) == 0:
                return jsonify({
                    'reply': "To get started tell me: how much USDC you have, where to send payments, and how often. For example: I have 20 USDC. Send 5 to wallet 0xABC123 every Friday and grow the rest safely.",
                    'plan': None,
                    'status': 'awaiting_instruction'
                })
            
            plan = rules.build_plan(parsed, wallet_address)
            print(f"DEBUG plan: {plan}")
            
            is_valid = rules.validate_plan(plan)
            store.save_user(wallet_address, plan)

            # If yield requested and capital available - deploy automatically
            if plan.get('yield_requested', False) and plan.get('aave_deposit', 0) > 0:
                try:
                    from protocols.vault import ButlerVault
                    from protocols.mock_yields import MockYieldEngine
                    vault = ButlerVault()
                    yields = MockYieldEngine()

                    balance = vault.get_user_balance(wallet_address)
                    deploy_amount = plan.get('aave_deposit', 0)

                    if balance['vault_balance'] >= deploy_amount:
                        tx_hash = vault.deploy_to_aave(wallet_address, deploy_amount)
                        best_protocol, best_apy = yields.get_best_yield(plan.get('risk_level', 'moderate'))
                        print(f" Auto deployed {deploy_amount} USDC to {best_protocol} at {best_apy}% - tx: {tx_hash}")
                        plan['yield_tx'] = tx_hash
                        plan['protocol'] = best_protocol
                        plan['apy'] = best_apy
                        
                        # Log the auto-deployment to activity feed
                        store.log_transaction(
                            wallet_address=wallet_address,
                            tx_type='deposit',
                            amount=deploy_amount,
                            tx_hash=tx_hash
                        )
                    else:
                        print(f" Insufficient vault balance for auto-deploy")
                except Exception as e:
                    print(f"Auto yield deploy error: {e}")

            reply = brain.generate_response(plan, wallet_address)
            return jsonify({
                'reply': reply,
                'plan': plan,
                'status': 'plan_created'
            })
        
        # Use new conversation flow for everything else
        # Initialize fallback data
        vault_data = {
            'usdc_balance': 'unavailable',
            'vault_balance': 0,
            'aave_deposit': 0,
            'payment_reserve': 0,
            'buffer': 0,
            'yield_earned': 0,
            'data_available': False
        }
        yield_data = {
            'protocols': {
                'aave': {'current_apy': 6.2, 'withdrawal_time': 'instant'},
                'curve': {'current_apy': 5.8, 'withdrawal_time': 'instant'},
                'pendle': {'current_apy': 8.5, 'withdrawal_time': '2-3 days'}
            },
            'data_available': False
        }
        
        # Try to fetch real data, but continue even if it fails
        try:
            from protocols.aave import AaveProtocol
            from agent.executor import ButlerExecutor
            from protocols.mock_yields import MockYieldEngine
            from agent.yield_monitor import YieldMonitor
            
            aave = AaveProtocol()
            executor = ButlerExecutor()
            yield_engine = MockYieldEngine()
            yield_monitor = YieldMonitor()
            
            # Try to get current balances and yield data
            try:
                usdc_balance = aave.get_usdc_balance(wallet_address)
                vault_data['usdc_balance'] = usdc_balance
                vault_data['data_available'] = True
                print(f"✅ Successfully fetched USDC balance: {usdc_balance}")
            except Exception as e:
                print(f"⚠️ Failed to fetch USDC balance: {e}")
                vault_data['usdc_balance'] = 'unavailable'
            
            try:
                vault_balance = executor.get_user_balance(wallet_address)
                if isinstance(vault_balance, dict):
                    vault_data.update({
                        'vault_balance': vault_balance.get('vault_balance', 0),
                        'aave_deposit': vault_balance.get('aave_balance', 0),
                        'payment_reserve': vault_balance.get('payment_reserve', 0),
                        'buffer': vault_balance.get('buffer', 0),
                        'yield_earned': vault_balance.get('yield_earned', 0),
                        'data_available': True
                    })
                    print(f"✅ Successfully fetched vault balance: {vault_balance}")
                else:
                    print(f"⚠️ Vault balance returned unexpected format: {vault_balance}")
            except Exception as e:
                print(f"⚠️ Failed to fetch vault balance: {e}")
            
            try:
                real_yield_data = yield_engine.get_all_yields()
                if isinstance(real_yield_data, dict):
                    yield_data = real_yield_data
                    yield_data['data_available'] = True
                    print(f"✅ Successfully fetched yield data: {list(real_yield_data.keys())}")
                else:
                    print(f"⚠️ Yield data returned unexpected format: {real_yield_data}")
            except Exception as e:
                print(f"⚠️ Failed to fetch yield data: {e}")
            
        except Exception as e:
            print(f"⚠️ Data fetching initialization failed: {e}")
        
        # Always attempt to get a conversational response, even with fallback data
        try:
            response = brain.get_financial_advice(message, wallet_address, user, vault_data, yield_data)
            
            return jsonify({
                'reply': response,
                'plan': None,
                'status': 'conversational_response',
                'context': {
                    'vault_data': vault_data,
                    'user_data': user,
                    'yield_data': yield_data
                }
            })
            
        except Exception as e:
            print(f"❌ Even fallback conversation failed: {e}")
            # Last resort - provide a helpful canned response based on message type
            message_lower = message.lower()
            
            if any(word in message_lower for word in ['budget', 'manage', 'help me', 'what should i do']):
                fallback_response = "Got it! To help you budget, first tell me — do you have any upcoming payments like payroll or bills?"
            elif any(word in message_lower for word in ['yield', 'earning', 'apy', 'protocol']):
                fallback_response = "Current rates are around 6-8% APY depending on the protocol. Since I can't access your balance right now, how much USDC are you looking to put to work?"
            elif any(word in message_lower for word in ['pay', 'payment', 'send']):
                fallback_response = "I can help set up payments! Tell me who you're paying, how much, and how often. For example: 'Pay my workers 5 USDC every Friday'."
            else:
                fallback_response = "I'm here to help manage your crypto! Tell me what you'd like to do - set up payments, optimize yield, or create a budget plan?"
            
            return jsonify({
                'reply': fallback_response,
                'plan': None,
                'status': 'fallback_response'
            })
    except Exception as e:
        print(f"DEBUG error: {e}")
        return jsonify({'error': str(e)}), 500

@api.route('/api/balance/<wallet_address>', methods=['GET'])
def get_balance(wallet_address):
    """
    Get balance information for wallet
    """
    try:
        # Get USDC balance
        usdc_balance = aave.get_usdc_balance(wallet_address)
        
        # Get user from UserStore
        user = user_store.get_user(wallet_address)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'usdc_balance': usdc_balance,
            'aave_deposit': user.get('aave_deposit', 0),
            'yield_earned': user.get('yield_earned', 0),
            'buffer': user.get('buffer', 0),
            'payment_reserve': user.get('payment_reserve', 0)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/api/activity/<wallet_address>', methods=['GET'])
def get_activity(wallet_address):
    """
    Get transaction history for wallet
    """
    try:
        # Get transaction history from UserStore
        history = user_store.get_transaction_history(wallet_address)
        
        return jsonify({
            'transactions': history[-20:] if len(history) > 20 else history
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/api/yields', methods=['GET'])
def get_yields():
    """
    Get current yield rates from all protocols
    """
    try:
        # Get current yields from MockYieldEngine
        yields = yield_engine.get_current_yields()
        
        return jsonify(yields)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/api/users/register', methods=['POST'])
def register_user():
    """
    Register or login user
    """
    try:
        data = request.get_json()
        wallet_address = data.get('wallet_address')
        
        if not wallet_address:
            return jsonify({'error': 'Missing wallet_address'}), 400
        
        # Check if user exists
        existing_user = user_store.get_user(wallet_address)
        
        if existing_user:
            return jsonify({
                'message': f'Your current plan is active.',
                'plan': existing_user,
                'status': 'existing'
            })
        else:
            # Create new user with empty plan
            empty_plan = {
                'usdc_total': 0,
                'aave_deposit': 0,
                'payment_reserve': 0,
                'buffer': 0,
                'send_to_address': '',
                'send_schedule': 'weekly',
                'risk_level': 'moderate',
                'yield_strategy': 'aave_lending'
            }
            
            user_store.save_user(wallet_address, empty_plan)
            
            return jsonify({
                'message': 'Let\'s set up your automation plan.',
                'plan': empty_plan,
                'status': 'new'
            })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/api/send', methods=['POST'])
def send_now():
    try:
        data = request.get_json()
        from_address = data.get('wallet_address')
        to_address = data.get('to_address')
        amount = float(data.get('amount', 0))

        if not from_address or not to_address or amount <= 0:
            return jsonify({'error': 'Missing required fields: wallet_address, to_address, amount'}), 400

        from protocols.vault import ButlerVault
        vault = ButlerVault()

        balance = vault.get_user_balance(from_address)
        print(f"Vault balance: {balance}")

        if balance['vault_balance'] < amount:
            return jsonify({
                'success': False,
                'error': f"Vault balance is {balance['vault_balance']} USDC. Need {amount} USDC.",
                'vault_balance': balance['vault_balance']
            })

        tx_hash = vault.execute_payment(from_address)
        return jsonify({
            'success': True,
            'tx_hash': tx_hash,
            'amount': amount,
            'to': to_address,
            'basescan': f'https://sepolia.basescan.org/tx/{tx_hash}'
        })
    except Exception as e:
        print(f"Send error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@api.route('/api/deploy-yield', methods=['POST'])
def deploy_yield():
    try:
        data = request.get_json()
        wallet_address = data.get('wallet_address')
        amount = float(data.get('amount', 0))

        from protocols.vault import ButlerVault
        from protocols.mock_yields import MockYieldEngine

        vault = ButlerVault()
        yields = MockYieldEngine()

        balance = vault.get_user_balance(wallet_address)
        print(f"DEBUG balance before deploy: {balance}")

        if balance['vault_balance'] < amount:
            return jsonify({
                'success': False,
                'error': f"Only {balance['vault_balance']} USDC in vault"
            })

        tx_hash = vault.deploy_to_aave(wallet_address, amount)

        best_protocol, best_apy = yields.get_best_yield('moderate')
        daily_yield = yields.calculate_daily_yield(amount, best_apy)

        return jsonify({
            'success': True,
            'tx_hash': tx_hash,
            'amount_deployed': amount,
            'protocol': best_protocol,
            'apy': best_apy,
            'daily_yield': daily_yield,
            'monthly_estimate': round(daily_yield * 30, 6),
            'yearly_estimate': round(amount * best_apy / 100, 4),
            'basescan': f'https://sepolia.basescan.org/tx/{tx_hash}'
        })
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 500

@api.route('/api/yield-status/<wallet_address>', methods=['GET'])
def yield_status(wallet_address):
    try:
        from protocols.vault import ButlerVault
        from protocols.mock_yields import MockYieldEngine
        from users.user_store import UserStore
        import datetime

        vault = ButlerVault()
        yields = MockYieldEngine()
        store = UserStore()

        balance = vault.get_user_balance(wallet_address)
        user = store.get_user(wallet_address)
        best_protocol, best_apy = yields.get_best_yield('moderate')

        aave_balance = balance['aave_balance']
        vault_balance = balance['vault_balance']

        # Calculate time running
        created_at = user.get('created_at') if user else None
        if created_at:
            start_time = datetime.datetime.fromisoformat(created_at)
            now = datetime.datetime.now()
            elapsed = now - start_time
            hours_running = round(elapsed.total_seconds() / 3600, 2)
            days_running = round(elapsed.total_seconds() / 86400, 4)
        else:
            hours_running = 0
            days_running = 0

        # Calculate yield earned so far
        yield_earned = user.get('yield_earned', 0) if user else 0

        # Calculate projections
        daily_rate = best_apy / 100 / 365
        daily_yield = round(aave_balance * daily_rate, 6)
        weekly_yield = round(daily_yield * 7, 4)
        monthly_yield = round(daily_yield * 30, 4)
        yearly_yield = round(aave_balance * best_apy / 100, 4)

        # Per second rate
        per_second = round(aave_balance * daily_rate / 86400, 10)

        return jsonify({
            'wallet': wallet_address,
            'status': 'active' if aave_balance > 0 else 'not_deployed',
            'protocol': best_protocol,
            'apy': best_apy,
            'capital_deployed': aave_balance,
            'vault_idle': vault_balance,
            'yield_earned_total': yield_earned,
            'hours_running': hours_running,
            'days_running': days_running,
            'per_second': per_second,
            'daily_yield': daily_yield,
            'weekly_yield': weekly_yield,
            'monthly_yield': monthly_yield,
            'yearly_yield': yearly_yield,
            'last_updated': datetime.datetime.now().isoformat()
        })
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@api.route('/api/status', methods=['GET'])
def get_status():
    """
    Get server status
    """
    try:
        # Get all users to count connected wallets
        all_users = user_store.get_all_users()
        connected_wallets = len([u for u in all_users if u.get('wallet_address')])
        
        # Get current day from scheduler (if available)
        current_day = 0
        try:
            # This is a simple way to get scheduler state
            import importlib.util
            spec = importlib.util.spec_from_file_location("scheduler", "agent/scheduler.py")
            scheduler_module = importlib.util.module_from_spec(spec)
            # We can't easily access scheduler instance from here, so return 0
        except:
            pass
        
        return jsonify({
            'server_status': 'running',
            'connected_wallets': connected_wallets,
            'current_day': current_day,
            'timestamp': str(datetime.now())
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/api/payment-popup-submit', methods=['POST'])
def submit_payment_popup():
    """Handle payment popup form submission"""
    try:
        data = request.get_json()
        wallet_address = data.get('wallet_address')
        payments = data.get('payments', [])
        total_budget = data.get('total_budget', 100)
        
        if not wallet_address:
            return jsonify({'error': 'Missing wallet_address'}), 400
        
        if not payments:
            return jsonify({'error': 'No payments provided'}), 400
        
        # Generate summary for chat
        summary = payment_parser.generate_summary_from_user_input(payments)
        
        # Generate financial advice
        advice = payment_parser.generate_financial_advice(payments, total_budget)
        
        # Save emails and recipient data
        for payment in payments:
            if payment.get('recipient_email'):
                notification_manager.save_recipient_email(
                    wallet_address,
                    payment.get('wallet_address', ''),
                    payment.get('recipient_email', ''),
                    payment.get('recipient_name', 'Recipient')
                )
        
        return jsonify({
            'status': 'payment_plan_ready',
            'summary': summary,
            'advice': advice,
            'payments': payments,
            'total_committed': sum(p.get('amount', 0) for p in payments),
            'remaining_for_yield': total_budget - sum(p.get('amount', 0) for p in payments)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/api/activate-payment-plan', methods=['POST'])
def activate_payment_plan():
    """Activate payment plan after user approval"""
    try:
        data = request.get_json()
        wallet_address = data.get('wallet_address')
        payments = data.get('payments', [])
        
        if not wallet_address:
            return jsonify({'error': 'Missing wallet_address'}), 400
        
        # Convert to operational plan format
        total_amount = sum(p.get('amount', 0) for p in payments)
        
        # Create plan for first payment (simplified for demo)
        if payments:
            first_payment = payments[0]
            plan_data = {
                'usdc_total': total_amount,
                'send_amount': first_payment.get('amount', 0),
                'send_to_address': first_payment.get('wallet_address', ''),
                'send_schedule': first_payment.get('frequency', 'weekly'),
                'yield_requested': True,
                'risk_level': 'conservative'
            }
            
            # Build and save operational plan
            plan = rules_engine.build_plan(plan_data, wallet_address)
            is_valid = rules_engine.validate_plan(plan)
            
            if is_valid:
                user_store.save_user(wallet_address, plan)
                
                # Send notifications to all recipients
                for payment in payments:
                    if payment.get('recipient_email'):
                        notification_manager.trigger_payment_scheduled(
                            wallet_address,
                            payment.get('recipient_name', 'Recipient'),
                            payment.get('amount', 0),
                            payment.get('frequency', 'weekly'),
                            datetime.now()
                        )
                
                return jsonify({
                    'status': 'plan_activated',
                    'message': 'Payment plan activated successfully! All schedules are now active.',
                    'plan': plan
                })
            else:
                return jsonify({
                    'status': 'validation_failed',
                    'message': 'Plan validation failed. Please check payment details.'
                })
        else:
            return jsonify({'error': 'No payments to activate'}), 400
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/api/execute-action', methods=['POST'])
def execute_action():
    """Execute a confirmed action"""
    try:
        data = request.get_json()
        wallet_address = data.get('wallet_address')
        action = data.get('action')
        
        if not wallet_address or not action:
            return jsonify({'error': 'Missing wallet_address or action'}), 400
        
        # Execute the action
        result = action_executor.execute_action(action, wallet_address)
        
        if result.get('success'):
            return jsonify({
                'status': 'action_executed',
                'message': result.get('message'),
                'tx_hash': result.get('tx_hash'),
                'action_type': action.get('type')
            })
        else:
            return jsonify({
                'status': 'action_failed',
                'message': result.get('message'),
                'error': result.get('error')
            }), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500
