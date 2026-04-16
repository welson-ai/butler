from protocols.vault import ButlerVault
from protocols.mock_yields import MockYieldEngine
from users.user_store import UserStore
from notifications.notification_manager import notification_manager
import os
from dotenv import load_dotenv

load_dotenv()

class ButlerExecutor:
    def __init__(self):
        self.vault = ButlerVault()
        self.yield_engine = MockYieldEngine()
        self.store = UserStore()
        print('✅ Executor ready — using ButlerVault')

    def execute_deposit_to_aave(self, user_address, amount):
        try:
            tx_hash = self.vault.deploy_to_aave(user_address, amount)
            self.store.log_transaction(user_address, 'aave_deposit', amount, tx_hash)
            
            # Trigger notification
            notification_manager.trigger_funds_moved_to_yield(
                wallet_address=user_address,
                amount=amount,
                protocol='Aave',
                apy=6.2  # Get from yield engine in real implementation
            )
            
            return {'success': True, 'tx_hash': tx_hash, 'amount': amount, 'protocol': 'aave'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def execute_withdrawal_from_aave(self, user_address, amount):
        try:
            tx_hash = self.vault.withdraw_from_aave(user_address, amount)
            self.store.log_transaction(user_address, 'aave_withdraw', amount, tx_hash)
            return {'success': True, 'tx_hash': tx_hash, 'amount': amount}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def execute_payment(self, user_address):
        try:
            # Get payment details before execution
            user = self.store.get_user(user_address)
            rules = user.get('rules', {}) if user else {}
            
            tx_hash = self.vault.execute_payment(user_address)
            self.store.log_transaction(user_address, 'payment', 0, tx_hash)
            
            # Trigger payment notifications
            notification_manager.trigger_payment_executed(
                wallet_address=user_address,
                amount=rules.get('send_amount', 0),
                recipient_wallet=rules.get('send_to_address', ''),
                tx_hash=tx_hash
            )
            
            return {'success': True, 'tx_hash': tx_hash}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def execute_emergency_withdrawal(self, user_address):
        try:
            balance = self.vault.get_user_balance(user_address)
            return {'success': True, 'balance': balance}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_user_balance(self, user_address):
        try:
            return self.vault.get_user_balance(user_address)
        except Exception as e:
            return {'error': str(e)}

    def get_transaction_history(self, user_address):
        try:
            return self.store.get_transaction_history(user_address)
        except Exception as e:
            return []

if __name__ == '__main__':
    executor = ButlerExecutor()
    balance = executor.get_user_balance('0x9d304a71Fe97d58d00D86C8ED6e5161f11Ea8608')
    print(f'Balance: {balance}')
