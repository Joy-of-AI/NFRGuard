
#!/usr/bin/env python3
"""
Alert Manager for RAG System
"""

import json
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import logging

class AlertManager:
    def __init__(self):
        self.slack_config = self._load_config("slack_config.json")
        self.email_config = self._load_config("email_config.json")
        self.logger = logging.getLogger(__name__)
    
    def _load_config(self, config_file):
        try:
            with open(config_file, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def send_slack_alert(self, alert_type, message, details=None):
        """Send alert to Slack"""
        if not self.slack_config.get("webhook_url"):
            self.logger.warning("Slack webhook not configured")
            return False
        
        alert_config = self.slack_config["alerts"].get(alert_type, {})
        
        payload = {
            "channel": self.slack_config.get("channel", "#alerts"),
            "username": self.slack_config.get("username", "Alert Bot"),
            "icon_emoji": self.slack_config.get("icon_emoji", ":warning:"),
            "attachments": [
                {
                    "color": alert_config.get("color", "warning"),
                    "title": alert_config.get("title", "Alert"),
                    "text": message,
                    "fields": [
                        {
                            "title": "Timestamp",
                            "value": datetime.now().isoformat(),
                            "short": True
                        },
                        {
                            "title": "System",
                            "value": "NFRGuard RAG",
                            "short": True
                        }
                    ]
                }
            ]
        }
        
        if details:
            payload["attachments"][0]["fields"].extend([
                {"title": k, "value": str(v), "short": True}
                for k, v in details.items()
            ])
        
        try:
            response = requests.post(
                self.slack_config["webhook_url"],
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            self.logger.info(f"Slack alert sent: {alert_type}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to send Slack alert: {e}")
            return False
    
    def send_email_alert(self, alert_type, message, details=None):
        """Send alert via email"""
        if not self.email_config.get("smtp_server"):
            self.logger.warning("Email configuration not set up")
            return False
        
        alert_config = self.email_config["alerts"].get(alert_type, {})
        
        msg = MIMEMultipart()
        msg["From"] = self.email_config["from_email"]
        msg["To"] = ", ".join(self.email_config["to_emails"])
        msg["Subject"] = alert_config.get("subject", "RAG System Alert")
        
        body = f"""
        {message}
        
        Timestamp: {datetime.now().isoformat()}
        System: NFRGuard RAG
        
        """
        
        if details:
            body += "Details:\n"
            for k, v in details.items():
                body += f"  {k}: {v}\n"
        
        msg.attach(MIMEText(body, "plain"))
        
        try:
            server = smtplib.SMTP(
                self.email_config["smtp_server"],
                self.email_config["smtp_port"]
            )
            server.starttls()
            server.login(
                self.email_config["username"],
                self.email_config["password"]
            )
            server.send_message(msg)
            server.quit()
            self.logger.info(f"Email alert sent: {alert_type}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to send email alert: {e}")
            return False
    
    def send_alert(self, alert_type, message, details=None):
        """Send alert via all configured channels"""
        self.logger.info(f"Sending {alert_type} alert: {message}")
        
        slack_success = self.send_slack_alert(alert_type, message, details)
        email_success = self.send_email_alert(alert_type, message, details)
        
        return slack_success or email_success

# Usage example
if __name__ == "__main__":
    alert_manager = AlertManager()
    
    # Test alerts
    alert_manager.send_alert("info", "RAG system alerting configured successfully")
    alert_manager.send_alert("warning", "Test warning alert")
    alert_manager.send_alert("critical", "Test critical alert")
