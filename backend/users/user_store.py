"""
What this file does: Manages user data storage and retrieval operations
What it receives as input: User data and query parameters
What it returns as output: User information and configuration data
"""

import json
import os
from datetime import datetime

class UserStore:
    def __init__(self, data_file: str = "backend/data/users.json"):
        """
        Initialize user data store
        
        Args:
            data_file: Path to user data JSON file
        """
        self.data_file = data_file
        self.ensure_data_file_exists()
    
    def ensure_data_file_exists(self):
        """
        Ensure data file exists with proper structure
        """
        if not os.path.exists(self.data_file):
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            with open(self.data_file, 'w') as f:
                json.dump({"users": []}, f, indent=2)
    
    def load_data(self) -> dict:
        """
        Load data from JSON file
        
        Returns:
            Loaded data dictionary
        """
        try:
            with open(self.data_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"users": []}
    
    def save_data(self, data: dict):
        """
        Save data to JSON file
        
        Args:
            data: Data dictionary to save
        """
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def save_user(self, wallet_address: str, plan: dict) -> str:
        """
        Save or update user with their operational plan
        
        Args:
            wallet_address: User's wallet address
            plan: Operational plan from rules_engine
            
        Returns:
            Success message
        """
        data = self.load_data()
        users = data.get('users', [])
        
        # Find existing user or create new one
        existing_user = None
        for user in users:
            if user.get('wallet_address') == wallet_address:
                existing_user = user
                break
        
        if existing_user:
            # Update existing user
            existing_user.update({
                'wallet_address': wallet_address,
                'usdc_balance': plan.get('usdc_total', 0),
                'aave_deposit': plan.get('aave_deposit', 0),
                'buffer': plan.get('buffer', 0),
                'payment_reserve': plan.get('payment_reserve', 0),
                'yield_earned': existing_user.get('yield_earned', 0),  # Preserve existing yield
                'rules': {
                    'send_amount': plan.get('payment_reserve', 0),
                    'send_to': plan.get('send_to_address', ''),
                    'send_schedule': plan.get('send_schedule', 'weekly'),
                    'risk_level': plan.get('risk_level', 'moderate')
                }
            })
            message = f"Updated existing user {wallet_address}"
        else:
            # Add new user
            new_user = {
                'user_id': f"user_{len(users) + 1:03d}",
                'wallet_address': wallet_address,
                'usdc_balance': plan.get('usdc_total', 0),
                'aave_deposit': plan.get('aave_deposit', 0),
                'buffer': plan.get('buffer', 0),
                'payment_reserve': plan.get('payment_reserve', 0),
                'yield_earned': 0,
                'rules': {
                    'send_amount': plan.get('payment_reserve', 0),
                    'send_to': plan.get('send_to_address', ''),
                    'send_schedule': plan.get('send_schedule', 'weekly'),
                    'risk_level': plan.get('risk_level', 'moderate')
                }
            }
            users.append(new_user)
            message = f"Created new user {wallet_address}"
        
        self.save_data({"users": users})
        return message
    
    def save_user_data(self, wallet_address: str, user_data: dict) -> str:
        """
        Save or update user data including conversation flows and emails
        
        Args:
            wallet_address: User's wallet address
            user_data: User data dictionary with conversation flows, emails, etc.
            
        Returns:
            Success message
        """
        data = self.load_data()
        users = data.get('users', [])
        
        # Find existing user or create new one
        existing_user = None
        for user in users:
            if user.get('wallet_address') == wallet_address:
                existing_user = user
                break
        
        if existing_user:
            # Update existing user with new data
            existing_user.update(user_data)
            # Keep essential fields if not provided
            if 'wallet_address' not in user_data:
                existing_user['wallet_address'] = wallet_address
            if 'user_id' not in user_data:
                existing_user['user_id'] = existing_user.get('user_id', f"user_{len(users) + 1:03d}")
            message = f"Updated user data {wallet_address}"
        else:
            # Add new user
            new_user = user_data.copy()
            new_user.update({
                'user_id': f"user_{len(users) + 1:03d}",
                'wallet_address': wallet_address
            })
            users.append(new_user)
            message = f"Created new user data {wallet_address}"
        
        self.save_data({"users": users})
        return message
    
    def get_user(self, wallet_address: str) -> dict:
        """
        Get user data by wallet address
        
        Args:
            wallet_address: User's wallet address
            
        Returns:
            User data dictionary or None if not found
        """
        data = self.load_data()
        users = data.get('users', [])
        
        for user in users:
            if user.get('wallet_address') == wallet_address:
                return user
        
        return None
    
    def get_all_users(self) -> list:
        """
        Get all users in the system
        
        Returns:
            List of all user data
        """
        data = self.load_data()
        return data.get('users', [])
    
    def update_balance(self, wallet_address: str, new_aave_deposit: float, yield_earned: float = 0):
        """
        Update user's balance information
        
        Args:
            wallet_address: User's wallet address
            new_aave_deposit: New Aave deposit amount
            yield_earned: Additional yield earned
        """
        data = self.load_data()
        users = data.get('users', [])
        
        for user in users:
            if user.get('wallet_address') == wallet_address:
                user['aave_deposit'] = new_aave_deposit
                current_yield = user.get('yield_earned', 0)
                user['yield_earned'] = current_yield + yield_earned
                break
        
        self.save_data({"users": users})
    
    def log_transaction(self, wallet_address: str, tx_type: str, amount: float, tx_hash: str):
        """
        Log transaction to transactions file
        
        Args:
            wallet_address: User's wallet address
            tx_type: Transaction type
            amount: Transaction amount
            tx_hash: Blockchain transaction hash
        """
        tx_file = "backend/data/transactions.json"
        
        # Ensure transactions file exists
        if not os.path.exists(tx_file):
            os.makedirs(os.path.dirname(tx_file), exist_ok=True)
            with open(tx_file, 'w') as f:
                json.dump({"transactions": []}, f, indent=2)
        
        # Load existing transactions
        with open(tx_file, 'r') as f:
            data = json.load(f)
        
        transactions = data.get('transactions', [])
        
        # Add new transaction
        new_tx = {
            'wallet_address': wallet_address,
            'tx_type': tx_type,
            'amount': amount,
            'tx_hash': tx_hash,
            'timestamp': datetime.now().isoformat()
        }
        
        transactions.append(new_tx)
        
        # Save back
        with open(tx_file, 'w') as f:
            json.dump({"transactions": transactions}, f, indent=2)
    
    def get_transaction_history(self, wallet_address: str) -> list:
        """
        Get transaction history for wallet address
        
        Args:
            wallet_address: User's wallet address
            
        Returns:
            List of transactions for that wallet
        """
        tx_file = "backend/data/transactions.json"
        
        # Ensure transactions file exists
        if not os.path.exists(tx_file):
            return []
        
        # Load existing transactions
        with open(tx_file, 'r') as f:
            data = json.load(f)
        
        transactions = data.get('transactions', [])
        
        # Filter transactions for this wallet
        user_transactions = [
            tx for tx in transactions 
            if tx.get('wallet_address') == wallet_address
        ]
        
        # Sort by timestamp (newest first)
        user_transactions.sort(
            key=lambda x: x.get('timestamp', ''), 
            reverse=True
        )
        
        return user_transactions

# Test at bottom
if __name__ == "__main__":
    try:
        store = UserStore()
        
        # Save a test user
        test_plan = {
            'usdc_total': 20.0,
            'aave_deposit': 13.0,
            'payment_reserve': 5.0,
            'buffer': 2.0,
            'send_to_address': '0xABC123',
            'send_schedule': 'friday',
            'risk_level': 'conservative',
            'yield_strategy': 'aave_lending'
        }
        
        # Test save_user
        result = store.save_user("0xTEST123", test_plan)
        print(f"Save result: {result}")
        
        # Test get_user
        user = store.get_user("0xTEST123")
        print(f"Retrieved user: {json.dumps(user, indent=2) if user else 'Not found'}")
        
        # Test get_all_users
        all_users = store.get_all_users()
        print(f"Total users: {len(all_users)}")
        
        # Test update_balance
        store.update_balance("0xTEST123", 15.0, 0.5)
        updated_user = store.get_user("0xTEST123")
        print(f"Updated balance: {json.dumps(updated_user, indent=2)}")
        
        # Test log_transaction
        store.log_transaction("0xTEST123", "deposit", 13.0, "0xabc123def")
        print("Transaction logged successfully")
        
    except Exception as e:
        print(f"Test failed: {e}")
