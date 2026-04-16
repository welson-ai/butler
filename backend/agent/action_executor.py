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
        if any(word in message_lower for word in ['earn yield', 'deposit', 'put to work', 'grow', 'invest', 'take']):
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
                # Return wallet approval action instead of executing directly
                return {
                    "success": True,
                    "requires_wallet_approval": True,
                    "action_type": "deposit_yield",
                    "amount": action.get('amount', 0),
                    "protocol": action.get('protocol', 'Aave'),
                    "message": f"Please approve deposit of {action.get('amount', 0)} USDC to {action.get('protocol', 'Aave')} in your wallet.",
                    "wallet_action": {
                        "type": "deposit",
                        "amount": action.get('amount', 0),
                        "protocol": action.get('protocol', 'Aave'),
                        "apy": action.get('apy', 6.2)
                    }
                }
            
            elif action_type == "withdraw":
                # Return wallet approval action instead of executing directly
                return {
                    "success": True,
                    "requires_wallet_approval": True,
                    "action_type": "withdraw",
                    "amount": action.get('amount', 0),
                    "protocol": action.get('protocol', 'Aave'),
                    "message": f"Please approve withdrawal of {action.get('amount', 0)} USDC from {action.get('protocol', 'Aave')} in your wallet.",
                    "wallet_action": {
                        "type": "withdraw",
                        "amount": action.get('amount', 0),
                        "protocol": action.get('protocol', 'Aave')
                    }
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
        try:
            # Validate action dict
            if not isinstance(action, dict):
                return {
                    "message": "Invalid action format.",
                    "action": None
                }
            
            # Build action object safely
            action_obj = {
                "type": action.get('type'),
                "amount": action.get('amount', 0),
                "protocol": action.get('protocol', 'Aave'),
                "recipient": action.get('recipient'),
                "apy": action.get('apy')
            }
            
            # Remove None values to prevent frontend issues
            action_obj = {k: v for k, v in action_obj.items() if v is not None}
            
            return {
                "message": action.get('message', 'Confirm this action?'),
                "action": action_obj
            }
        except Exception as e:
            return {
                "message": f"Error formatting action: {str(e)}",
                "action": None
            }

# Singleton instance
action_executor = ActionExecutor()
