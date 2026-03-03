"""
What this file does: Provides simulated yield data for demo purposes
What it receives as input: Protocol names and time parameters
What it returns as output: Mock yield data for testing and demonstration
"""

import random
import datetime

class MockYieldEngine:
    def __init__(self):
        """
        Initialize MockYieldEngine
        """
        # Base protocol rates with risk levels
        self.PROTOCOLS = {
            "aave": {"base_apy": 6.0, "risk": "low"},
            "compound": {"base_apy": 4.0, "risk": "low"},
            "pendle": {"base_apy": 11.0, "risk": "medium"},
            "curve": {"base_apy": 8.0, "risk": "low"}
        }
        self.risk_flag = False
    
    def get_current_yields(self) -> dict:
        """
        Get current yields with slight randomization
        
        Returns:
            Dictionary of protocol name to current APY
        """
        yields = {}
        for protocol, data in self.PROTOCOLS.items():
            # Vary each by plus or minus 0.5% randomly to simulate real market movement
            base_apy = data["base_apy"]
            variation = random.uniform(-0.5, 0.5)
            current_apy = round(base_apy + variation, 2)
            yields[protocol] = current_apy
        
        return yields
    
    def get_best_yield(self, risk_level: str) -> tuple:
        """
        Get best yield for risk level
        
        Args:
            risk_level: User's risk preference (conservative, moderate, aggressive)
            
        Returns:
            Tuple of (protocol_name, apy) with best rate
        """
        yields = self.get_current_yields()
        
        if risk_level.lower() == "conservative":
            # Only consider aave and compound
            conservative_protocols = {k: v for k, v in yields.items() if k in ["aave", "compound"]}
            if not conservative_protocols:
                return "aave", self.PROTOCOLS["aave"]["base_apy"]
            best_protocol = max(conservative_protocols, key=lambda k: conservative_protocols[k])
            return best_protocol, conservative_protocols[best_protocol]
        
        elif risk_level.lower() == "moderate":
            # Consider aave, compound, curve
            moderate_protocols = {k: v for k, v in yields.items() if k in ["aave", "compound", "curve"]}
            if not moderate_protocols:
                return "aave", self.PROTOCOLS["aave"]["base_apy"]
            best_protocol = max(moderate_protocols, key=lambda k: moderate_protocols[k])
            return best_protocol, moderate_protocols[best_protocol]
        
        elif risk_level.lower() == "aggressive":
            # Consider all protocols
            if not yields:
                return "aave", self.PROTOCOLS["aave"]["base_apy"]
            best_protocol = max(yields, key=lambda k: yields[k])
            return best_protocol, yields[best_protocol]
        
        else:
            # Default to moderate
            return self.get_best_yield("moderate")
    
    def calculate_daily_yield(self, principal: float, apy: float) -> float:
        """
        Calculate daily yield earnings
        
        Args:
            principal: Principal amount in USDC
            apy: Annual percentage yield
            
        Returns:
            Daily yield amount earned
        """
        daily_rate = (apy / 365) / 100
        return round(principal * daily_rate, 6)
    
    def inject_risk_event(self) -> str:
        """
        Simulate a protocol risk event
        
        Returns:
            Warning message about risk event
        """
        # Drop aave APY to 0.5% suddenly
        self.PROTOCOLS["aave"]["base_apy"] = 0.5
        self.risk_flag = True
        
        return "Risk detected on Aave. APY dropped to 0.5%. Moving funds to safety."
    
    def resolve_risk_event(self) -> str:
        """
        Resolve simulated risk event
        
        Returns:
            Recovery message
        """
        # Reset aave APY back to normal
        self.PROTOCOLS["aave"]["base_apy"] = 6.0
        self.risk_flag = False
        
        return "Risk event resolved. Aave APY restored to 6.0%"

# Test at bottom
if __name__ == "__main__":
    try:
        engine = MockYieldEngine()
        
        # Print current yields
        current_yields = engine.get_current_yields()
        print("Current Yields:")
        for protocol, apy in current_yields.items():
            print(f"  {protocol}: {apy}%")
        
        print(f"\nRisk Flag: {engine.risk_flag}")
        
        # Get best yield for each risk level
        for risk in ["conservative", "moderate", "aggressive"]:
            best_protocol, best_apy = engine.get_best_yield(risk)
            print(f"\nBest {risk} yield: {best_protocol} at {best_apy}%")
        
        # Calculate daily yield on 13 USDC at 6% APY
        daily_yield = engine.calculate_daily_yield(13.0, 6.0)
        print(f"\nDaily yield on 13 USDC at 6% APY: ${daily_yield}")
        
        # Inject risk event
        print(f"\nInjecting risk event...")
        warning = engine.inject_risk_event()
        print(f"WARNING: {warning}")
        
        # Show new yields after risk event
        new_yields = engine.get_current_yields()
        print(f"\nYields after risk event:")
        for protocol, apy in new_yields.items():
            print(f"  {protocol}: {apy}%")
        
        # Resolve risk event
        print(f"\nResolving risk event...")
        recovery = engine.resolve_risk_event()
        print(f"INFO: {recovery}")
        
        # Final yields
        final_yields = engine.get_current_yields()
        print(f"\nFinal yields:")
        for protocol, apy in final_yields.items():
            print(f"  {protocol}: {apy}%")
        
    except Exception as e:
        print(f"Test failed: {e}")
