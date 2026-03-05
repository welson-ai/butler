from web3 import Web3
from eth_account import Account
import os
import json
from dotenv import load_dotenv

load_dotenv()

VAULT_ABI = [
    {
        "name": "deposit",
        "type": "function",
        "inputs": [{"name": "amount", "type": "uint256"}],
        "outputs": [],
        "stateMutability": "nonpayable"
    },
    {
        "name": "deployToAave",
        "type": "function",
        "inputs": [
            {"name": "user", "type": "address"},
            {"name": "amount", "type": "uint256"}
        ],
        "outputs": [],
        "stateMutability": "nonpayable"
    },
    {
        "name": "withdrawFromAave",
        "type": "function",
        "inputs": [
            {"name": "user", "type": "address"},
            {"name": "amount", "type": "uint256"}
        ],
        "outputs": [],
        "stateMutability": "nonpayable"
    },
    {
        "name": "executePayment",
        "type": "function",
        "inputs": [{"name": "user", "type": "address"}],
        "outputs": [],
        "stateMutability": "nonpayable"
    },
    {
        "name": "setPaymentRule",
        "type": "function",
        "inputs": [
            {"name": "recipient", "type": "address"},
            {"name": "amount", "type": "uint256"},
            {"name": "schedule", "type": "string"}
        ],
        "outputs": [],
        "stateMutability": "nonpayable"
    },
    {
        "name": "setPaymentRuleForUser",
        "type": "function",
        "inputs": [
            {"name": "user", "type": "address"},
            {"name": "recipient", "type": "address"},
            {"name": "amount", "type": "uint256"},
            {"name": "schedule", "type": "string"}
        ],
        "outputs": [],
        "stateMutability": "nonpayable"
    },
    {
        "name": "getUserBalance",
        "type": "function",
        "inputs": [{"name": "user", "type": "address"}],
        "outputs": [
            {"name": "vaultBalance", "type": "uint256"},
            {"name": "aaveBalance", "type": "uint256"},
            {"name": "paymentReserve", "type": "uint256"},
            {"name": "isActive", "type": "bool"}
        ],
        "stateMutability": "view"
    },
    {
        "name": "emergencyWithdraw",
        "type": "function",
        "inputs": [],
        "outputs": [],
        "stateMutability": "nonpayable"
    }
]

ERC20_ABI = [
    {
        "name": "approve",
        "type": "function",
        "inputs": [
            {"name": "spender", "type": "address"},
            {"name": "amount", "type": "uint256"}
        ],
        "outputs": [{"name": "", "type": "bool"}],
        "stateMutability": "nonpayable"
    },
    {
        "name": "balanceOf",
        "type": "function",
        "inputs": [{"name": "account", "type": "address"}],
        "outputs": [{"name": "", "type": "uint256"}],
        "stateMutability": "view"
    }
]

class ButlerVault:
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider(os.getenv('BASE_SEPOLIA_RPC_URL')))
        self.vault_address = os.getenv('BUTLER_VAULT_ADDRESS')
        self.usdc_address = os.getenv('USDC_SEPOLIA_ADDRESS')
        self.agent_private_key = os.getenv('AGENT_PRIVATE_KEY')
        self.agent_address = Account.from_key(self.agent_private_key).address
        
        self.vault = self.w3.eth.contract(
            address=Web3.to_checksum_address(self.vault_address),
            abi=VAULT_ABI
        )
        self.usdc = self.w3.eth.contract(
            address=Web3.to_checksum_address(self.usdc_address),
            abi=ERC20_ABI
        )
        print(f'Vault connected: {self.vault_address}')

    def _send_transaction(self, func, private_key=None):
        key = private_key or self.agent_private_key
        account = Account.from_key(key)
        tx = func.build_transaction({
            'from': account.address,
            'nonce': self.w3.eth.get_transaction_count(account.address),
            'gas': 300000,
            'gasPrice': self.w3.eth.gas_price
        })
        signed = self.w3.eth.account.sign_transaction(tx, key)
        tx_hash = self.w3.eth.send_raw_transaction(signed.raw_transaction)
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        return tx_hash.hex()

    def get_user_balance(self, user_address):
        result = self.vault.functions.getUserBalance(
            Web3.to_checksum_address(user_address)
        ).call()
        return {
            'vault_balance': result[0] / 1e6,
            'aave_balance': result[1] / 1e6,
            'payment_reserve': result[2] / 1e6,
            'is_active': result[3]
        }

    def deploy_to_aave(self, user_address, amount):
        amount_units = int(amount * 1e6)
        func = self.vault.functions.deployToAave(
            Web3.to_checksum_address(user_address),
            amount_units
        )
        return self._send_transaction(func)

    def withdraw_from_aave(self, user_address, amount):
        amount_units = int(amount * 1e6)
        func = self.vault.functions.withdrawFromAave(
            Web3.to_checksum_address(user_address),
            amount_units
        )
        return self._send_transaction(func)

    def execute_payment(self, user_address):
        func = self.vault.functions.executePayment(
            Web3.to_checksum_address(user_address)
        )
        return self._send_transaction(func)

    def set_payment_rule(self, user_address, recipient, amount, schedule, private_key):
        amount_units = int(amount * 1e6)
        func = self.vault.functions.setPaymentRule(
            Web3.to_checksum_address(recipient),
            amount_units,
            schedule
        )
        return self._send_transaction(func, private_key)

    def set_payment_rule_for_user(self, user_address, recipient, amount, schedule):
        amount_units = int(amount * 1e6)
        func = self.vault.functions.setPaymentRuleForUser(
            Web3.to_checksum_address(user_address),
            Web3.to_checksum_address(recipient),
            amount_units,
            schedule
        )
        return self._send_transaction(func)

if __name__ == '__main__':
    vault = ButlerVault()
    print('Vault ready')
