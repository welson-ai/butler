"""
What this file does: Manages scheduled payments and automated tasks
What it receives as input: User payment schedules and timing rules
What it returns as output: Triggered actions at specified intervals
"""

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import json
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from users.user_store import UserStore
from protocols.mock_yields import MockYieldEngine
from users.rules_engine import RulesEngine

# Constants
TEST_CLOCK_INTERVAL = 180  # 3 minutes = 1 day
RISK_EVENT_DAY = 8         # inject risk on day 8
RESOLVE_EVENT_DAY = 9      # resolve on day 9

class ButlerScheduler:
    def __init__(self):
        """
        Initialize ButlerScheduler
        """
        self.scheduler = BackgroundScheduler()
        self.yield_engine = MockYieldEngine()
        self.user_store = UserStore()
        self.current_day = 0
        self.activity_log = []
        
        print("🤖 Butler Scheduler initialized")
    
    def log_activity(self, message: str, event_type: str):
        """
        Log activity with timestamp and day number
        
        Args:
            message: Activity description
            event_type: Type of event (yield, payment, risk, info)
        """
        activity = {
            "day": self.current_day,
            "timestamp": datetime.now().isoformat(),
            "message": message,
            "event_type": event_type
        }
        self.activity_log.append(activity)
        
        # Print to console with emoji
        emoji_map = {
            "yield": "📈",
            "payment": "💸",
            "risk": "⚠️",
            "info": "ℹ️"
        }
        emoji = emoji_map.get(event_type, "📋")
        print(f"Day {self.current_day}: {emoji} {message}")
    
    def run_daily_cycle(self):
        """
        Execute one daily cycle of operations
        """
        self.current_day += 1
        self.log_activity(f"Day {self.current_day} beginning", "info")
        
        # Get all users from UserStore
        all_users = self.user_store.get_all_users()
        
        for user in all_users:
            if not user.get("wallet_address"):
                continue
                
            wallet_address = user["wallet_address"]
            rules = user.get("rules", {})
            risk_level = rules.get("risk_level", "moderate")
            
            # Get best yield for user risk level
            best_protocol, best_apy = self.yield_engine.get_best_yield(risk_level)
            
            # Calculate daily yield on their aave deposit
            aave_deposit = user.get("aave_deposit", 0)
            daily_yield = self.yield_engine.calculate_daily_yield(aave_deposit, best_apy)
            
            # Update user balance with earned yield
            self.user_store.update_balance(wallet_address, aave_deposit, daily_yield)
            
            # Log yield event
            self.log_activity(f"Yield earned: ${daily_yield} from {best_protocol} @ {best_apy}%", "yield")
            
            # Check if today is their payment day
            payment_schedule = rules.get("send_schedule", "weekly")
            next_payment_day = self.get_next_payment_day(payment_schedule)
            
            if self.current_day == next_payment_day:
                self.process_payment(user)
        
        # Inject risk event on day 8
        if self.current_day == RISK_EVENT_DAY:
            self.inject_risk_event()
        
        # Resolve risk event on day 9
        if self.current_day == RESOLVE_EVENT_DAY:
            self.resolve_risk_event()
    
    def get_next_payment_day(self, schedule: str) -> int:
        """
        Calculate next payment day for user
        
        Args:
            schedule: Payment schedule string
            
        Returns:
            Day number when next payment is due
        """
        schedule_map = {
            "friday": 7,
            "monday": 7,
            "first_of_month": 30,
            "daily": 1
        }
        
        base_day = schedule_map.get(schedule.lower(), 7)
        return (self.current_day % 7) + base_day if self.current_day % 7 != 0 else base_day
    
    def process_payment(self, user: dict):
        """
        Process scheduled payment for user
        
        Args:
            user: User dictionary with payment details
        """
        wallet_address = user["wallet_address"]
        rules = user.get("rules", {})
        send_amount = rules.get("send_amount", 0)
        send_to = rules.get("send_to", "")
        
        if send_amount <= 0 or not send_to:
            self.log_activity(f"Skipping payment - invalid amount or recipient", "info")
            return
        
        # Log payment firing
        self.log_activity(f"Sending {send_amount} USDC to {send_to}", "payment")
        
        # Log transaction (mock tx hash for demo)
        tx_hash = f"0x{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.user_store.log_transaction(wallet_address, "payment", send_amount, tx_hash)
        
        # Log confirmation
        self.log_activity(f"Payment sent successfully - tx: {tx_hash}", "payment")
        
        # Deduct from payment reserve and add to aave deposit for next cycle
        current_aave = user.get("aave_deposit", 0)
        current_reserve = user.get("payment_reserve", 0)
        
        new_aave = current_aave + current_reserve
        new_reserve = 0
        
        # Update user data
        user["aave_deposit"] = new_aave
        user["payment_reserve"] = new_reserve
        
        self.log_activity(f"Refilled payment reserve: {current_reserve} → aave", "info")
    
    def inject_risk_event(self):
        """
        Inject risk event across all users
        """
        warning = self.yield_engine.inject_risk_event()
        self.log_activity(warning, "risk")
        
        # Log risk event for all users
        all_users = self.user_store.get_all_users()
        for user in all_users:
            wallet_address = user.get("wallet_address", "")
            if wallet_address:
                self.log_activity(f"Risk event for {wallet_address}: Moving funds to safety", "risk")
    
    def resolve_risk_event(self):
        """
        Resolve risk event across all users
        """
        recovery = self.yield_engine.resolve_risk_event()
        self.log_activity(recovery, "info")
        
        # Log recovery for all users
        all_users = self.user_store.get_all_users()
        for user in all_users:
            wallet_address = user.get("wallet_address", "")
            if wallet_address:
                self.log_activity(f"Risk resolved for {wallet_address}: Redeploying funds", "info")
    
    def get_activity_log(self, limit: int = 20) -> list:
        """
        Get recent activity log entries
        
        Args:
            limit: Maximum number of entries to return
            
        Returns:
            List of recent activity log entries
        """
        return self.activity_log[-limit:] if self.activity_log else []
    
    def start(self):
        """
        Start the scheduler with daily cycle job
        """
        # Add daily cycle job
        self.scheduler.add_job(
            func=self.run_daily_cycle,
            trigger="interval",
            seconds=TEST_CLOCK_INTERVAL,
            id="daily_cycle"
        )
        
        self.log_activity("Butler is awake. Managing wallets.", "info")
        
        try:
            self.scheduler.start()
            print("⏰ Scheduler started. Running daily cycles every 3 minutes.")
            print("Press Ctrl+C to stop.")
            
            # Keep main thread alive
            while True:
                import time
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n⏹ Butler going to sleep.")
            self.scheduler.shutdown()

# Test at bottom
if __name__ == "__main__":
    try:
        # Create a test user first
        store = UserStore()
        test_plan = {
            "usdc_total": 20.0,
            "aave_deposit": 13.0,
            "payment_reserve": 5.0,
            "buffer": 2.0,
            "send_to_address": "0xABC123",
            "send_schedule": "friday",
            "risk_level": "conservative",
            "yield_strategy": "aave_lending"
        }
        
        # Save test user
        result = store.save_user("0xTEST123", test_plan)
        print(f"Setup: {result}")
        
        # Create and start scheduler
        scheduler = ButlerScheduler()
        scheduler.start()
        
    except Exception as e:
        print(f"Test failed: {e}")
