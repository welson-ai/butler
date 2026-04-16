from datetime import datetime, timedelta
from typing import Dict, List, Optional
from .email_service import email_service
from users.user_store import UserStore

class NotificationManager:
    def __init__(self):
        self.store = UserStore()
        print("🔔 Notification Manager initialized")
    
    def trigger_payment_executed(self, wallet_address: str, amount: float, recipient_wallet: str, 
                              tx_hash: str) -> Dict[str, bool]:
        """Trigger payment notifications for both sender and recipient"""
        
        user = self.store.get_user(wallet_address)
        if not user:
            print(f"⚠️ No user found for wallet {wallet_address}")
            return {"sender": False, "recipient": False}
        
        # Get sender info
        sender_email = user.get('email')
        sender_name = user.get('name', 'User')
        
        # Get recipient info from payment rules
        recipient_info = self._get_recipient_info(wallet_address, recipient_wallet)
        recipient_email = recipient_info.get('email')
        recipient_name = recipient_info.get('name', 'Recipient')
        
        # Send notifications
        return email_service.notify_payment_executed(
            sender_email=sender_email,
            recipient_email=recipient_email,
            sender_name=sender_name,
            recipient_name=recipient_name,
            amount=amount,
            tx_hash=tx_hash,
            recipient_wallet=recipient_wallet
        )
    
    def trigger_payment_coming_soon(self, wallet_address: str) -> bool:
        """Check for payments in next 24 hours and send warnings"""
        
        user = self.store.get_user(wallet_address)
        if not user or not user.get('email'):
            return False
        
        rules = user.get('rules', {})
        if not rules.get('send_amount', 0):
            return False
        
        # Get next payment date (simplified - in real implementation, calculate from last payment)
        interval_seconds = rules.get('interval_seconds', 604800)  # Default 1 week
        last_payment = user.get('last_payment_date')
        
        if last_payment:
            next_payment = datetime.fromisoformat(last_payment) + timedelta(seconds=interval_seconds)
        else:
            next_payment = datetime.now() + timedelta(seconds=interval_seconds)
        
        # Check if payment is in next 24 hours
        if next_payment <= datetime.now() + timedelta(hours=24):
            return email_service.notify_payment_coming_soon(
                email=user['email'],
                user_name=user.get('name', 'User'),
                amount=rules['send_amount'],
                recipient_name=rules.get('recipient_name', 'Recipient'),
                payment_date=next_payment,
                current_balance=self._get_total_balance(wallet_address)
            )
        
        return False
    
    def trigger_funds_moved_to_yield(self, wallet_address: str, amount: float, 
                                   protocol: str, apy: float) -> bool:
        """Trigger notification when funds are moved to yield"""
        
        user = self.store.get_user(wallet_address)
        if not user or not user.get('email'):
            return False
        
        return email_service.notify_funds_moved_to_yield(
            email=user['email'],
            user_name=user.get('name', 'User'),
            amount=amount,
            protocol=protocol,
            apy=apy
        )
    
    def trigger_low_balance_alert(self, wallet_address: str, required_amount: float) -> bool:
        """Trigger low balance alert"""
        
        user = self.store.get_user(wallet_address)
        if not user or not user.get('email'):
            return False
        
        current_balance = self._get_total_balance(wallet_address)
        shortfall = required_amount - current_balance
        
        if shortfall > 0:
            return email_service.notify_low_balance(
                email=user['email'],
                user_name=user.get('name', 'User'),
                payment_amount=required_amount,
                current_balance=current_balance,
                shortall=shortfall
            )
        
        return False
    
    def trigger_payment_scheduled(self, wallet_address: str, recipient_name: str, 
                              amount: float, frequency: str, start_date: datetime) -> bool:
        """Trigger notification when payment is scheduled"""
        
        user = self.store.get_user(wallet_address)
        if not user or not user.get('email'):
            return False
        
        return email_service.notify_payment_scheduled(
            email=user['email'],
            user_name=user.get('name', 'User'),
            recipient_name=recipient_name,
            amount=amount,
            frequency=frequency,
            start_date=start_date
        )
    
    def save_user_email(self, wallet_address: str, email: str, name: str = None) -> bool:
        """Save user email to profile"""
        
        try:
            user = self.store.get_user(wallet_address) or {}
            user['email'] = email
            if name:
                user['name'] = name
            
            self.store.save_user(wallet_address, user)
            print(f"✅ Saved email for user {wallet_address}: {email}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to save email: {e}")
            return False
    
    def save_recipient_email(self, wallet_address: str, recipient_wallet: str, 
                           recipient_email: str, recipient_name: str) -> bool:
        """Save recipient email for payment notifications"""
        
        try:
            user = self.store.get_user(wallet_address) or {}
            
            if 'recipients' not in user:
                user['recipients'] = {}
            
            user['recipients'][recipient_wallet] = {
                'email': recipient_email,
                'name': recipient_name
            }
            
            self.store.save_user(wallet_address, user)
            print(f"✅ Saved recipient email: {recipient_name} -> {recipient_email}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to save recipient email: {e}")
            return False
    
    def _get_recipient_info(self, wallet_address: str, recipient_wallet: str) -> Dict:
        """Get recipient info from user profile"""
        
        user = self.store.get_user(wallet_address)
        if not user:
            return {}
        
        recipients = user.get('recipients', {})
        return recipients.get(recipient_wallet, {'name': 'Recipient'})
    
    def _get_total_balance(self, wallet_address: str) -> float:
        """Get total balance for user"""
        
        try:
            from protocols.aave import AaveProtocol
            from agent.executor import ButlerExecutor
            
            aave = AaveProtocol()
            executor = ButlerExecutor()
            
            usdc_balance = aave.get_usdc_balance(wallet_address)
            vault_balance = executor.get_user_balance(wallet_address)
            
            if isinstance(vault_balance, dict):
                return usdc_balance + vault_balance.get('vault_balance', 0)
            else:
                return usdc_balance
                
        except Exception as e:
            print(f"⚠️ Failed to get balance for notifications: {e}")
            return 0.0

# Singleton instance
notification_manager = NotificationManager()
