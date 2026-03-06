"""
What this file does: Handles all Aave protocol interactions for Base Sepolia
What it receives as input: Transaction parameters and wallet credentials
What it returns as output: Aave transaction results and position data
"""

from web3 import Web3
from typing import Dict, Any, List
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ABIs
ERC20_ABI = [
    {"name": "approve", "type": "function", "inputs": [{"name": "spender", "type": "address"}, {"name": "amount", "type": "uint256"}], "outputs": [{"name": "", "type": "bool"}], "stateMutability": "nonpayable"},
    {"name": "balanceOf", "type": "function", "inputs": [{"name": "account", "type": "address"}], "outputs": [{"name": "", "type": "uint256"}], "stateMutability": "view"},
    {"name": "transfer", "type": "function", "inputs": [{"name": "to", "type": "address"}, {"name": "amount", "type": "uint256"}], "outputs": [{"name": "", "type": "bool"}], "stateMutability": "nonpayable"}
]

AAVE_POOL_ABI = [
    {"name": "supply", "type": "function", "inputs": [{"name": "asset", "type": "address"}, {"name": "amount", "type": "uint256"}, {"name": "onBehalfOf", "type": "address"}, {"name": "referralCode", "type": "uint16"}], "outputs": [], "stateMutability": "nonpayable"},
    {"name": "withdraw", "type": "function", "inputs": [{"name": "asset", "type": "address"}, {"name": "amount", "type": "uint256"}, {"name": "to", "type": "address"}], "outputs": [{"name": "", "type": "uint256"}], "stateMutability": "nonpayable"}
]

AUSDC_ABI = [
    {
        "name": "balanceOf",
        "type": "function",
        "inputs": [{"name": "account", "type": "address"}],
        "outputs": [{"name": "", "type": "uint256"}],
        "stateMutability": "view"
    }
]

class AaveProtocol:
    def __init__(self):
        """
        Initialize Aave protocol handler
        """
        # Connect to Base Sepolia via Web3
        self.rpc_url = os.getenv('BASE_SEPOLIA_RPC_URL')
        self.web3 = Web3(Web3.HTTPProvider(self.rpc_url))
        
        # Load contracts
        self.usdc_address = os.getenv('USDC_SEPOLIA_ADDRESS')
        self.aave_pool_address = os.getenv('AAVE_POOL_SEPOLIA_ADDRESS')
        
        self.usdc_contract = self.web3.eth.contract(
            address=self.usdc_address,
            abi=ERC20_ABI
        )
        
        self.aave_pool_contract = self.web3.eth.contract(
            address=self.aave_pool_address,
            abi=AAVE_POOL_ABI
        )
        
        print(f"Connected to Base Sepolia: {self.web3.is_connected()}")
    
    def get_usdc_balance(self, wallet_address: str) -> float:
        """
        Get USDC balance for wallet address
        
        Args:
            wallet_address: Wallet address to check
            
        Returns:
            USDC balance as float (human readable)
        """
        try:
            balance = self.usdc_contract.functions.balanceOf(wallet_address).call()
            # Convert from 6 decimals to human readable
            return float(balance / 10**6)
        except Exception as e:
            print(f"Error getting USDC balance: {e}")
            return 0.0
    
    def approve_aave(self, wallet_address: str, private_key: str, amount: float) -> str:
        """
        Approve Aave Pool to spend USDC
        
        Args:
            wallet_address: User's wallet address
            private_key: Private key for signing
            amount: Amount to approve (human readable)
            
        Returns:
            Transaction hash
        """
        try:
            # Convert amount to 6 decimal units
            amount_wei = int(amount * 10**6)
            
            # Build approve transaction
            nonce = self.web3.eth.get_transaction_count(wallet_address)
            tx = self.usdc_contract.functions.approve(
                self.aave_pool_address,
                amount_wei
            ).build_transaction({
                'from': wallet_address,
                'nonce': nonce,
                'gas': 200000,
                'gasPrice': self.web3.eth.gas_price,
                'chainId': 84532  # Base Sepolia
            })
            
            # Sign and send transaction
            signed_tx = self.web3.eth.account.sign_transaction(tx, private_key)
            tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            return self.web3.to_hex(tx_hash)
            
        except Exception as e:
            print(f"Error approving Aave: {e}")
            return ""
    
    def deposit(self, wallet_address: str, private_key: str, amount: float) -> str:
        """
        Deposit USDC into Aave
        
        Args:
            wallet_address: User's wallet address
            private_key: Private key for signing
            amount: Amount to deposit (human readable)
            
        Returns:
            Transaction hash
        """
        try:
            # First approve Aave to spend USDC
            approve_hash = self.approve_aave(wallet_address, private_key, amount)
            if not approve_hash:
                return ""
            
            # Wait for approval to confirm
            self.web3.eth.wait_for_transaction_receipt(approve_hash, timeout=60)
            
            # Convert amount to 6 decimal units
            amount_wei = int(amount * 10**6)
            
            # Build supply transaction
            nonce = self.web3.eth.get_transaction_count(wallet_address)
            tx = self.aave_pool_contract.functions.supply(
                self.usdc_address,
                amount_wei,
                wallet_address,
                0  # referral code
            ).build_transaction({
                'from': wallet_address,
                'nonce': nonce + 1,
                'gas': 500000,
                'gasPrice': self.web3.eth.gas_price,
                'chainId': 84532  # Base Sepolia
            })
            
            # Sign and send transaction
            signed_tx = self.web3.eth.account.sign_transaction(tx, private_key)
            tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            return self.web3.to_hex(tx_hash)
            
        except Exception as e:
            print(f"Error depositing to Aave: {e}")
            return ""
    
    def withdraw(self, wallet_address: str, private_key: str, amount: float) -> str:
        """
        Withdraw USDC from Aave
        
        Args:
            wallet_address: User's wallet address
            private_key: Private key for signing
            amount: Amount to withdraw (human readable)
            
        Returns:
            Transaction hash
        """
        try:
            # Convert amount to 6 decimal units
            amount_wei = int(amount * 10**6)
            
            # Build withdraw transaction
            nonce = self.web3.eth.get_transaction_count(wallet_address)
            tx = self.aave_pool_contract.functions.withdraw(
                self.usdc_address,
                amount_wei,
                wallet_address
            ).build_transaction({
                'from': wallet_address,
                'nonce': nonce,
                'gas': 500000,
                'gasPrice': self.web3.eth.gas_price,
                'chainId': 84532  # Base Sepolia
            })
            
            # Sign and send transaction
            signed_tx = self.web3.eth.account.sign_transaction(tx, private_key)
            tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            return self.web3.to_hex(tx_hash)
            
        except Exception as e:
            print(f"Error withdrawing from Aave: {e}")
            return ""
    
    def send_usdc(self, from_address: str, private_key: str, to_address: str, amount: float) -> str:
        """
        Send USDC to another address
        
        Args:
            from_address: Sender's wallet address
            private_key: Private key for signing
            to_address: Recipient's wallet address
            amount: Amount to send (human readable)
            
        Returns:
            Transaction hash
        """
        try:
            # Convert amount to 6 decimal units
            amount_wei = int(amount * 10**6)
            
            # Build transfer transaction
            nonce = self.web3.eth.get_transaction_count(from_address)
            tx = self.usdc_contract.functions.transfer(
                to_address,
                amount_wei
            ).build_transaction({
                'from': from_address,
                'nonce': nonce,
                'gas': 200000,
                'gasPrice': self.web3.eth.gas_price,
                'chainId': 84532  # Base Sepolia
            })
            
            # Sign and send transaction
            signed_tx = self.web3.eth.account.sign_transaction(tx, private_key)
            tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            return self.web3.to_hex(tx_hash)
            
        except Exception as e:
            print(f"Error sending USDC: {e}")
            return ""
    
    def get_atoken_balance(self, wallet_address):
        try:
            ausdc_address = os.getenv('AUSDC_SEPOLIA_ADDRESS', '0x96C8394a3D1B80b07A4a614C2B2A5e8BF6b9DEF')
            ausdc = self.web3.eth.contract(
                address=Web3.to_checksum_address(ausdc_address),
                abi=AUSDC_ABI
            )
            balance = ausdc.functions.balanceOf(
                Web3.to_checksum_address(wallet_address)
            ).call()
            return round(balance / 1e6, 6)
        except Exception as e:
            print(f"aToken balance error: {e}")
            return 0

# Test at bottom
if __name__ == "__main__":
    try:
        # Create AaveProtocol instance
        aave = AaveProtocol()
        
        # Test connection and balance reading
        test_address = "0x1234567890123456789012345678901234567890"  # Test address
        balance = aave.get_usdc_balance(test_address)
        print(f"USDC balance for {test_address}: ${balance}")
        
    except Exception as e:
        print(f"Test failed: {e}")
