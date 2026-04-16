import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json

class EmailService:
    def __init__(self):
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', 587))
        self.sender_email = os.getenv('SENDER_EMAIL', '')
        self.sender_password = os.getenv('SENDER_PASSWORD', '')
        self.use_sendgrid = os.getenv('USE_SENDGRID', 'false').lower() == 'true'
        
        if self.use_sendgrid:
            self.sendgrid_api_key = os.getenv('SENDGRID_API_KEY', '')
        
        print(f"📧 Email Service initialized: {'SendGrid' if self.use_sendgrid else 'SMTP'}")
    
    def send_email(self, to_email: str, subject: str, body: str, recipient_name: str = None) -> bool:
        """Send email using either SendGrid or SMTP"""
        try:
            if self.use_sendgrid:
                return self._send_sendgrid(to_email, subject, body, recipient_name)
            else:
                return self._send_smtp(to_email, subject, body, recipient_name)
        except Exception as e:
            print(f"❌ Failed to send email to {to_email}: {e}")
            return False
    
    def _send_sendgrid(self, to_email: str, subject: str, body: str, recipient_name: str = None) -> bool:
        """Send email using SendGrid API"""
        try:
            import sendgrid
            from sendgrid.helpers.mail import Mail
            
            message = Mail(
                from_email=self.sender_email,
                to_emails=to_email,
                subject=subject,
                html_content=body
            )
            
            sg = sendgrid.SendGridAPIClient(api_key=self.sendgrid_api_key)
            response = sg.send(message)
            
            if response.status_code == 202:
                print(f"✅ SendGrid email sent to {to_email}: {subject}")
                return True
            else:
                print(f"❌ SendGrid error: {response.status_code} - {response.body}")
                return False
                
        except ImportError:
            print("❌ SendGrid not installed, falling back to SMTP")
            return self._send_smtp(to_email, subject, body, recipient_name)
        except Exception as e:
            print(f"❌ SendGrid error: {e}")
            return False
    
    def _send_smtp(self, to_email: str, subject: str, body: str, recipient_name: str = None) -> bool:
        """Send email using SMTP"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add personalization if recipient name is provided
            if recipient_name:
                body = body.replace(f"Hi {recipient_name}", f"Hi {recipient_name}")
            
            msg.attach(MIMEText(body, 'html'))
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            text = msg.as_string()
            server.sendmail(self.sender_email, to_email, text)
            server.quit()
            
            print(f"✅ SMTP email sent to {to_email}: {subject}")
            return True
            
        except Exception as e:
            print(f"❌ SMTP error: {e}")
            return False
    
    def notify_payment_executed(self, sender_email: str, recipient_email: str, sender_name: str, 
                            recipient_name: str, amount: float, tx_hash: str, 
                            recipient_wallet: str) -> Dict[str, bool]:
        """Send payment notifications to both sender and recipient"""
        
        base_scan_url = f"https://basescan.org/tx/{tx_hash}"
        results = {"sender": False, "recipient": False}
        
        # Sender notification
        if sender_email:
            sender_subject = f"Butler just paid {recipient_name or 'recipient'} {amount} USDC"
            sender_body = f"""
            <h2>Payment Executed Successfully ✅</h2>
            <p>Hi {sender_name},</p>
            <p>Your Butler has just executed a payment:</p>
            <ul>
                <li><strong>Amount:</strong> {amount} USDC</li>
                <li><strong>Recipient:</strong> {recipient_name or 'N/A'}</li>
                <li><strong>Wallet:</strong> {recipient_wallet}</li>
                <li><strong>Transaction:</strong> <a href="{base_scan_url}">View on BaseScan</a></li>
                <li><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</li>
            </ul>
            <p>Your funds are being managed safely.</p>
            <p>Best,<br>Crypto Butler</p>
            """
            
            results["sender"] = self.send_email(sender_email, sender_subject, sender_body, sender_name)
        
        # Recipient notification
        if recipient_email:
            recipient_subject = f"You just received {amount} USDC from {sender_name}"
            recipient_body = f"""
            <h2>Payment Received! 💰</h2>
            <p>Hi {recipient_name},</p>
            <p>You've just received a payment:</p>
            <ul>
                <li><strong>Amount:</strong> {amount} USDC</li>
                <li><strong>From:</strong> {sender_name}</li>
                <li><strong>Transaction:</strong> <a href="{base_scan_url}">View on BaseScan</a></li>
                <li><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</li>
            </ul>
            <p>The funds are now available in your wallet.</p>
            <p>Best,<br>Crypto Butler</p>
            """
            
            results["recipient"] = self.send_email(recipient_email, recipient_subject, recipient_body, recipient_name)
        
        return results
    
    def notify_payment_coming_soon(self, email: str, user_name: str, amount: float, 
                                recipient_name: str, payment_date: datetime, 
                                current_balance: float) -> bool:
        """Send 24-hour payment warning"""
        
        subject = f"Upcoming payment tomorrow — {amount} USDC to {recipient_name}"
        body = f"""
        <h2>Payment Reminder ⏰</h2>
        <p>Hi {user_name},</p>
        <p>You have a payment coming up tomorrow:</p>
        <ul>
            <li><strong>Amount:</strong> {amount} USDC</li>
            <li><strong>Recipient:</strong> {recipient_name}</li>
            <li><strong>Date:</strong> {payment_date.strftime('%Y-%m-%d')}</li>
            <li><strong>Current Balance:</strong> {current_balance} USDC</li>
        </ul>
        <p>✅ Funds are ready and the payment will be executed automatically.</p>
        <p>Best,<br>Crypto Butler</p>
        """
        
        return self.send_email(email, subject, body, user_name)
    
    def notify_funds_moved_to_yield(self, email: str, user_name: str, amount: float, 
                                  protocol: str, apy: float) -> bool:
        """Send notification when funds are moved to yield"""
        
        weekly_earnings = (amount * apy / 100) / 52
        
        subject = f"Your USDC is now earning {apy}% APY"
        body = f"""
        <h2>Yield Activated 📈</h2>
        <p>Hi {user_name},</p>
        <p>Your funds have been deployed to earn yield:</p>
        <ul>
            <li><strong>Amount:</strong> {amount} USDC</li>
            <li><strong>Protocol:</strong> {protocol}</li>
            <li><strong>APY:</strong> {apy}%</li>
            <li><strong>Estimated Weekly:</strong> ${weekly_earnings:.2f}</li>
            <li><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</li>
        </ul>
        <p>Your money is now working for you!</p>
        <p>Best,<br>Crypto Butler</p>
        """
        
        return self.send_email(email, subject, body, user_name)
    
    def notify_low_balance(self, email: str, user_name: str, payment_amount: float, 
                         current_balance: float, shortfall: float) -> bool:
        """Send low balance alert"""
        
        subject = "⚠️ Butler Alert — insufficient funds for upcoming payment"
        body = f"""
        <h2>Low Balance Alert ⚠️</h2>
        <p>Hi {user_name},</p>
        <p>There's an issue with an upcoming payment:</p>
        <ul>
            <li><strong>Payment Due:</strong> {payment_amount} USDC</li>
            <li><strong>Current Balance:</strong> {current_balance} USDC</li>
            <li><strong>Shortfall:</strong> {shortfall} USDC</li>
        </ul>
        <p>Please add funds to your wallet to ensure the payment can be executed.</p>
        <p>Best,<br>Crypto Butler</p>
        """
        
        return self.send_email(email, subject, body, user_name)
    
    def notify_payment_scheduled(self, email: str, user_name: str, recipient_name: str, 
                               amount: float, frequency: str, start_date: datetime) -> bool:
        """Send notification when payment is scheduled"""
        
        subject = f"Payment Scheduled: {amount} USDC to {recipient_name}"
        body = f"""
        <h2>Payment Scheduled 📅</h2>
        <p>Hi {user_name},</p>
        <p>You've scheduled a recurring payment:</p>
        <ul>
            <li><strong>Recipient:</strong> {recipient_name}</li>
            <li><strong>Amount:</strong> {amount} USDC</li>
            <li><strong>Frequency:</strong> {frequency}</li>
            <li><strong>Start Date:</strong> {start_date.strftime('%Y-%m-%d')}</li>
        </ul>
        <p>✅ Payment will be executed automatically.</p>
        <p>Best,<br>Crypto Butler</p>
        """
        
        return self.send_email(email, subject, body, user_name)

# Singleton instance
email_service = EmailService()
