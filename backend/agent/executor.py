"""
What this file does: Executes blockchain transactions based on brain instructions
What it receives as input: Structured action plans and wallet credentials
What it returns as output: Transaction results and on-chain confirmations
"""

from web3 import Web3
from typing import Dict, Any
from eth_account import Account
import sys
import os
from dotenv import load_dotenv
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from protocols.aave import AaveProtocol
from protocols.mock_yields import MockYieldEngine
from users.user_store import UserStore

# Load environment variables
load_dotenv()

class ButlerExecutor:
    def __init__(self):
        """
        Initialize ButlerExecutor with all required components
        """
        self.aave = AaveProtocol()
        self.yield_engine = MockYieldEngine()
        self.user_store = UserStore()
        print("✅ Executor ready")
    
    def execute_deposit(self, wallet_address: str, private_key: str, amount: float) -> Dict:
        """
        Execute deposit to Aave protocol
        
        Args:
            wallet_address: User's wallet address
            private_key: Private key for signing
            amount: Amount to deposit (human readable)
            
        Returns:
            Dict with success, tx_hash, amount, protocol
        """
        try:
            tx_hash = self.aave.deposit(wallet_address, private_key, amount)
            
            if tx_hash:
                # Log transaction to UserStore
                self.user_store.log_transaction(wallet_address, 'deposit', amount, tx_hash)
                return {
                    "success": True,
                    "tx_hash": tx_hash,
                    "amount": amount,
                    "protocol": "aave"
                }
            else:
                return {
                    "success": False,
                    "error": "Transaction failed",
                    "amount": amount,
                    "protocol": "aave"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "amount": amount,
                "protocol": "aave"
            }
    
    def execute_withdrawal(self, wallet_address: str, private_key: str, amount: float) -> Dict:
        """
        Execute withdrawal from Aave protocol
        
        Args:
            wallet_address: User's wallet address
            private_key: Private key for signing
            amount: Amount to withdraw (human readable)
            
        Returns:
            Dict with success, tx_hash, amount
        """
        try:
            tx_hash = self.aave.withdraw(wallet_address, private_key, amount)
            
            if tx_hash:
                # Log transaction to UserStore
                self.user_store.log_transaction(wallet_address, 'withdrawal', amount, tx_hash)
                return {
                    "success": True,
                    "tx_hash": tx_hash,
                    "amount": amount
                }
            else:
                return {
                    "success": False,
                    "error": "Transaction failed",
                    "amount": amount
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "amount": amount
            }
    
    def execute_payment(self, from_address: str, private_key: str, to_address: str, amount: float) -> Dict:
        """
        Execute USDC payment to another address
        
        Args:
            from_address: Sender's wallet address
            private_key: Private key for signing
            to_address: Recipient's wallet address
            amount: Amount to send (human readable)
            
        Returns:
            Dict with success, tx_hash, amount, to_address
        """
        try:
            tx_hash = self.aave.send_usdc(from_address, private_key, to_address, amount)
            
            if tx_hash:
                # Log transaction to UserStore with type=payment
                self.user_store.log_transaction(from_address, 'payment', amount, tx_hash)
                return {
                    "success": True,
                    "tx_hash": tx_hash,
                    "amount": amount,
                    "to_address": to_address
                }
            else:
                return {
                    "success": False,
                    "error": "Transaction failed",
                    "amount": amount,
                    "to_address": to_address
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "amount": amount,
                "to_address": to_address
            }
    
    def execute_rebalance(self, wallet_address: str, private_key: str, current_protocol: str, new_protocol: str, amount: float) -> Dict:
        """
        Execute rebalancing between protocols
        
        Args:
            wallet_address: User's wallet address
            private_key: Private key for signing
            current_protocol: Current protocol name
            new_protocol: New protocol name
            amount: Amount to rebalance (human readable)
            
        Returns:
            Dict with success, from_protocol, to_protocol, amount, reason
        """
        try:
            # Withdraw from current protocol
            withdraw_tx = self.aave.withdraw(wallet_address, private_key, amount)
            
            if not withdraw_tx:
                return {
                    "success": False,
                    "error": "Withdrawal failed",
                    "from_protocol": current_protocol,
                    "to_protocol": new_protocol,
                    "amount": amount,
                    "reason": "rebalance"
                }
            
            # Deposit into new protocol
            deposit_tx = self.aave.deposit(wallet_address, private_key, amount)
            
            if not deposit_tx:
                return {
                    "success": False,
                    "error": "Deposit failed",
                    "from_protocol": current_protocol,
                    "to_protocol": new_protocol,
                    "amount": amount,
                    "reason": "rebalance"
                }
            
            # Log both transactions
            self.user_store.log_transaction(wallet_address, 'withdrawal', amount, withdraw_tx)
            self.user_store.log_transaction(wallet_address, 'deposit', amount, deposit_tx)
            
            return {
                "success": True,
                "from_protocol": current_protocol,
                "to_protocol": new_protocol,
                "amount": amount,
                "reason": "rebalance"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "from_protocol": current_protocol,
                "to_protocol": new_protocol,
                "amount": amount,
                "reason": "rebalance"
            }
    
    def execute_emergency_withdrawal(self, wallet_address: str, private_key: str) -> Dict:
        """
        Execute emergency withdrawal of entire Aave deposit
        
        Args:
            wallet_address: User's wallet address
            private_key: Private key for signing
            
        Returns:
            Dict with success, amount_rescued, tx_hash
        """
        try:
            # Get user from UserStore
            user = self.user_store.get_user(wallet_address)
            if not user:
                return {
                    "success": False,
                    "error": "User not found"
                }
            
            # Withdraw entire aave_deposit immediately
            amount = user.get('aave_deposit', 0)
            if amount <= 0:
                return {
                    "success": False,
                    "error": "No funds to withdraw"
                }
            
            tx_hash = self.aave.withdraw(wallet_address, private_key, amount)
            
            if tx_hash:
                # Log as emergency event
                self.user_store.log_transaction(wallet_address, 'emergency_withdrawal', amount, tx_hash)
                return {
                    "success": True,
                    "amount_rescued": amount,
                    "tx_hash": tx_hash
                }
            else:
                return {
                    "success": False,
                    "error": "Emergency withdrawal failed",
                    "amount_rescued": amount
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_transaction_history(self, wallet_address: str) -> Dict:
        """
        Get transaction history for wallet address
        
        Args:
            wallet_address: Wallet address to check
            
        Returns:
            Dict with last 10 transactions for that wallet
        """
        try:
            # Read from backend/data/transactions.json
            transactions = self.user_store.get_transaction_history(wallet_address)
            
            return {
                "success": True,
                "transactions": transactions[-10:] if len(transactions) > 10 else transactions,
                "total_count": len(transactions)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "transactions": []
            }

# Test at bottom
if __name__ == "__main__":
    try:
        # Create ButlerExecutor
        executor = ButlerExecutor()
        
        # Test get_transaction_history with 0xTEST123
        history = executor.get_transaction_history("0xTEST123")
        print(f"Transaction history for 0xTEST123:")
        if history["success"]:
            for tx in history["transactions"]:
                print(f"  - {tx}")
        else:
            print(f"  Error: {history['error']}")
            
    except Exception as e:
        print(f"Test failed: {e}")
