import re
from typing import Dict, List, Any

class PaymentParser:
    def __init__(self):
        self.payment_keywords = ['rent', 'workers', 'payroll', 'salary', 'weekly', 'monthly', 'every', 'send', 'transfer']
        self.frequency_patterns = {
            'weekly': 604800,  # 7 days
            'biweekly': 1209600,  # 14 days  
            'monthly': 2419200,  # 28 days
            'daily': 86400  # 1 day
        }
    
    def parse_payment_intent(self, message: str) -> Dict[str, Any]:
        """
        Parse payment intent from user message and extract structured data
        
        Returns:
            Dict with detected payments and extracted information
        """
        payments = []
        message_lower = message.lower()
        
        # Extract amounts with regex
        amounts = re.findall(r'(\d+)\s*(?:usdc|usd|\$)?', message_lower)
        
        # Extract wallet addresses
        wallet_addresses = re.findall(r'0x[a-fA-F0-9]{40}', message)
        
        # Extract frequencies
        frequencies = []
        for freq in self.frequency_patterns.keys():
            if freq in message_lower:
                frequencies.append(freq)
        
        # Detect payment types
        payment_types = []
        if 'rent' in message_lower:
            payment_types.append('rent')
        if any(word in message_lower for word in ['workers', 'payroll', 'salary']):
            payment_types.append('workers')
        if 'transfer' in message_lower or ('send' in message_lower and not payment_types):
            payment_types.append('transfer')
        
        # Create payment objects
        if payment_types and amounts:
            for i, payment_type in enumerate(payment_types):
                payment = {
                    'type': payment_type,
                    'name': self._get_payment_name(payment_type),
                    'amount': amounts[i] if i < len(amounts) else amounts[0] if amounts else 0,
                    'wallet_address': wallet_addresses[i] if i < len(wallet_addresses) else wallet_addresses[0] if wallet_addresses else '',
                    'frequency': frequencies[0] if frequencies else 'weekly',
                    'purpose': self._get_purpose(payment_type, message_lower)
                }
                payments.append(payment)
        
        return {
            'detected_payments': payments,
            'total_amounts': amounts,
            'wallet_addresses': wallet_addresses,
            'frequencies': frequencies,
            'message': message,
            'requires_popup': len(payments) > 0
        }
    
    def _get_payment_name(self, payment_type: str) -> str:
        """Get display name for payment type"""
        names = {
            'rent': 'Rent',
            'workers': 'Workers', 
            'payroll': 'Payroll',
            'salary': 'Salary',
            'transfer': 'Weekly Transfer'
        }
        return names.get(payment_type, 'Payment')
    
    def _get_purpose(self, payment_type: str, message: str) -> str:
        """Extract purpose from message"""
        if payment_type == 'rent':
            return 'Rent'
        elif payment_type in ['workers', 'payroll', 'salary']:
            return 'Payroll'
        elif payment_type == 'transfer':
            return 'Transfer'
        else:
            return 'Payment'
    
    def generate_popup_data(self, parsed_data: Dict) -> Dict:
        """
        Generate structured data for popup form
        
        Args:
            parsed_data: Output from parse_payment_intent
            
        Returns:
            Structured data for frontend popup
        """
        payments = parsed_data.get('detected_payments', [])
        
        popup_payments = []
        for i, payment in enumerate(payments):
            popup_payment = {
                'id': i + 1,
                'name': payment['name'],
                'recipient_name': '',
                'wallet_address': payment['wallet_address'],
                'recipient_email': '',
                'amount': payment['amount'],
                'due_date': '',
                'frequency': payment['frequency'],
                'purpose': payment['purpose']
            }
            popup_payments.append(popup_payment)
        
        return {
            'title': f'Butler detected {len(payments)} payment(s)',
            'payments': popup_payments,
            'total_detected': len(payments),
            'message': parsed_data.get('message', '')
        }
    
    def generate_summary_from_user_input(self, user_submitted_payments: List[Dict]) -> str:
        """
        Generate chat summary from user-submitted popup data
        
        Args:
            user_submitted_payments: List of payment objects from popup
            
        Returns:
            Formatted summary string for chat
        """
        if not user_submitted_payments:
            return "No payments provided."
        
        summary_lines = ["Here's your payment plan:"]
        total_committed = 0
        
        for payment in user_submitted_payments:
            amount = payment.get('amount', 0)
            recipient = payment.get('recipient_name', 'Unknown')
            frequency = payment.get('frequency', 'weekly')
            wallet = payment.get('wallet_address', '')
            
            total_committed += amount
            
            # Format frequency display
            freq_display = {
                'weekly': 'Every Friday',
                'biweekly': 'Every other Friday', 
                'monthly': '1st of every month',
                'daily': 'Every day'
            }.get(frequency, frequency)
            
            # Get emoji for payment type
            emoji_map = {
                'rent': '🏠',
                'workers': '👷',
                'payroll': '💼', 
                'salary': '💰',
                'transfer': '💸'
            }
            emoji = emoji_map.get(payment.get('purpose', '').lower(), '💳')
            
            summary_lines.append(f"{emoji} {recipient} — {amount} USDC — {freq_display} → {wallet[:8]}...")
        
        summary_lines.append(f"\nTotal committed: {total_committed} USDC")
        
        # Calculate remaining (assuming 100 USDC budget for demo)
        remaining = max(0, 100 - total_committed)
        if remaining > 0:
            summary_lines.append(f"Remaining for yield: {remaining} USDC")
        
        summary_lines.append("\nShould I proceed with this plan?")
        
        return "\n".join(summary_lines)
    
    def generate_financial_advice(self, user_submitted_payments: List[Dict], total_budget: float) -> str:
        """
        Generate financial advice based on payment plan
        
        Args:
            user_submitted_payments: List of payment objects
            total_budget: Total USDC amount available
            
        Returns:
            Financial advice string
        """
        total_committed = sum(p.get('amount', 0) for p in user_submitted_payments)
        remaining = total_budget - total_committed
        
        advice_lines = ["Based on your schedule, here's what I recommend:"]
        
        if remaining > 0:
            # Calculate estimated yield (using 8.24% APY as example)
            monthly_yield = (remaining * 0.0824) / 12
            weekly_yield = monthly_yield / 4
            
            advice_lines.append(f"• Put {remaining} USDC in Curve at 8.24% APY")
            advice_lines.append(f"• I'll withdraw funds 24h before each payment")
            advice_lines.append(f"• Estimated monthly yield: ${monthly_yield:.2f}")
        else:
            advice_lines.append("• All funds allocated to payments - no yield available")
            advice_lines.append("• Consider reducing payments to enable savings")
        
        advice_lines.append("\nAre you happy with this? I'll activate everything once you approve.")
        
        return "\n".join(advice_lines)

# Singleton instance
payment_parser = PaymentParser()
