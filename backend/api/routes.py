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
        
        if not wallet_address or not message:
            return jsonify({'error': 'Missing wallet_address or message'}), 400
        
        # Parse instruction
        parsed = brain.parse_instruction(message, wallet_address)
        
        # Build plan
        plan = rules_engine.build_plan(parsed, wallet_address)
        
        # Validate plan
        validation = rules_engine.validate_plan(plan)
        
        # Save user
        user_store.save_user(wallet_address, plan)
        
        # Generate response
        response = brain.generate_response(str(plan), wallet_address)
        
        return jsonify({
            'reply': response,
            'plan': plan,
            'status': 'success' if validation.get('valid', False) else 'invalid'
        })
        
    except Exception as e:
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
