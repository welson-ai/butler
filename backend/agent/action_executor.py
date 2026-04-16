from typing import Dict, Any, Optional
import json
import re
from protocols.aave import AaveProtocol
from agent.executor import ButlerExecutor

class ActionExecutor:
    def __init__(self):
        self.aave = AaveProtocol()
        self.executor = ButlerExecutor()
        
    def parse_action_intent(self, user_message: str, wallet_address: str) -> Optional[Dict[str, Any]]:
        """
        Parse user message for clear action intents and return structured action
        
        Returns:
            Dict with action details or None if no clear action
        """
        message_lower = user_message.lower()
        
        # Parse amounts
        amounts = re.findall(r'(\d+\.?\d*)\s*(?:usdc|usd|\$)?', message_lower)
        amount = float(amounts[0]) if amounts else 0
        
        # Check for yield/deposit intent
        if any(word in message_lower for word in ['earn yield', 'deposit', 'put to work', 'grow', 'invest']):
            return {
                "type": "deposit_yield",
                "amount": amount,
                "protocol": "Aave",
                "apy": 6.2,  # Get from yield engine in real implementation
                "message": f"I'll deposit {amount} USDC into Aave at 6.2% APY. Confirm?"
            }
        
        # Check for withdrawal intent
        if any(word in message_lower for word in ['withdraw', 'take out', 'remove']):
            return {
                "type": "withdraw",
                "amount": amount,
                "protocol": "Aave",
                "message": f"I'll withdraw {amount} USDC from Aave. Confirm?"
            }
        
        # Check for payment intent
        if any(word in message_lower for word in ['send', 'pay', 'transfer']):
            # Extract wallet address
            wallet_match = re.search(r'0x[a-fA-F0-9]{40}', user_message)
            recipient = wallet_match.group(0) if wallet_match else ''
            
            return {
                "type": "send_payment",
                "amount": amount,
                "recipient": recipient,
                "message": f"I'll send {amount} USDC to {recipient[:8]}... Confirm?"
            }
        
        return None
    
    def execute_action(self, action: Dict[str, Any], wallet_address: str) -> Dict[str, Any]:
        """
        Execute the structured action
        
        Args:
            action: Structured action dict
            wallet_address: User's wallet address
            
        Returns:
            Execution result
        """
        action_type = action.get('type')
        
        try:
            if action_type == "deposit_yield":
                result = self.executor.execute_deposit_to_aave(
                    wallet_address, 
                    action.get('amount', 0)
                )
                return {
                    "success": result.get('success', False),
                    "tx_hash": result.get('tx_hash'),
                    "message": f"Deposited {action.get('amount', 0)} USDC to Aave successfully!",
                    "error": result.get('error') if not result.get('success') else None
                }
            
            elif action_type == "withdraw":
                result = self.executor.execute_withdrawal_from_aave(
                    wallet_address,
                    action.get('amount', 0)
                )
                return {
                    "success": result.get('success', False),
                    "tx_hash": result.get('tx_hash'),
                    "message": f"Withdrew {action.get('amount', 0)} USDC from Aave successfully!",
                    "error": result.get('error') if not result.get('success') else None
                }
            
            elif action_type == "send_payment":
                # This would need payment setup first, for now just return error
                return {
                    "success": False,
                    "message": "Payment setup required first. Use the payment setup flow to configure recipients.",
                    "error": "Payment not configured"
                }
            
            else:
                return {
                    "success": False,
                    "message": f"Unknown action type: {action_type}",
                    "error": "Invalid action"
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to execute {action_type}: {str(e)}",
                "error": str(e)
            }
    
    def format_action_response(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format action response for frontend
        
        Args:
            action: Structured action dict
            
        Returns:
            Formatted response with action field
        """
        return {
            "message": action.get('message', 'Confirm this action?'),
            "action": {
                "type": action.get('type'),
                "amount": action.get('amount'),
                "protocol": action.get('protocol'),
                "recipient": action.get('recipient'),
                "apy": action.get('apy')
            }
        }

# Singleton instance
action_executor = ActionExecutor()
