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
        
        parsed = brain.parse_instruction(message, wallet_address)
        print(f"DEBUG parsed: {parsed}")
        
        if 'error' in parsed or parsed.get('usdc_total', 0) == 0:
            return jsonify({
                'reply': "Hello! To get started tell me: how much USDC you have, where to send payments, and how often. For example: I have 20 USDC. Send 5 to wallet 0xABC123 every Friday and grow the rest safely.",
                'plan': None,
                'status': 'awaiting_instruction'
            })
        
        plan = rules.build_plan(parsed, wallet_address)
        print(f"DEBUG plan: {plan}")
        
        is_valid = rules.validate_plan(plan)
        store.save_user(wallet_address, plan)
        reply = brain.generate_response(plan, wallet_address)
        
        return jsonify({
            'reply': reply,
            'plan': plan,
            'status': 'active'
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
                'message': f'Welcome back! Your current plan is active.',
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
                'message': 'Welcome to Crypto Butler! Let\'s set up your automation plan.',
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
