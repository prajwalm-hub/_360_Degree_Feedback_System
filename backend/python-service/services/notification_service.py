import logging
# For email notifications
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# For SMS notifications (placeholder, requires integration with a real SMS gateway like Twilio)
# from twilio.rest import Client

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class NotificationService:
    def __init__(self, config):
        self.config = config
        self.email_config = config.get("email_notifications", {})
        self.sms_config = config.get("sms_notifications", {})
        logging.info("NotificationService initialized.")

    def send_email_notification(self, recipient_email, subject, body):
        """
        Sends an email notification.
        """
        if not self.email_config.get("enabled", False):
            logging.info("Email notifications are disabled in config.")
            return False

        sender_email = self.email_config.get("sender_email")
        sender_password = self.email_config.get("sender_password")
        smtp_server = self.email_config.get("smtp_server")
        smtp_port = self.email_config.get("smtp_port")

        if not all([sender_email, sender_password, smtp_server, smtp_port]):
            logging.error("Email notification configuration is incomplete. Cannot send email.")
            return False

        try:
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = recipient_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))

            with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
                server.login(sender_email, sender_password)
                server.send_message(msg)
            logging.info(f"Email notification sent to {recipient_email} with subject: '{subject}'")
            return True
        except Exception as e:
            logging.error(f"Error sending email notification to {recipient_email}: {e}")
            return False

    def send_sms_notification(self, recipient_phone_number, message):
        """
        Sends an SMS notification (placeholder for Twilio or similar integration).
        """
        if not self.sms_config.get("enabled", False):
            logging.info("SMS notifications are disabled in config.")
            return False

        # Example for Twilio (requires twilio library and account SID/auth token)
        # account_sid = self.sms_config.get("twilio_account_sid")
        # auth_token = self.sms_config.get("twilio_auth_token")
        # twilio_phone_number = self.sms_config.get("twilio_phone_number")

        # if not all([account_sid, auth_token, twilio_phone_number]):
        #     logging.error("SMS notification configuration is incomplete. Cannot send SMS.")
        #     return False

        # try:
        #     client = Client(account_sid, auth_token)
        #     message = client.messages.create(
        #         to=recipient_phone_number,
        #         from_=twilio_phone_number,
        #         body=message
        #     )
        #     logging.info(f"SMS notification sent to {recipient_phone_number}. SID: {message.sid}")
        #     return True
        # except Exception as e:
        #     logging.error(f"Error sending SMS notification to {recipient_phone_number}: {e}")
        #     return False
        
        logging.warning(f"SMS notification functionality is a placeholder. Message: '{message}' to {recipient_phone_number}")
        return False # Indicate not actually sent

    def notify_officials(self, alert):
        """
        Sends notifications to configured government officials based on the alert.
        """
        recipient_emails = self.config.get("government_officials_emails", [])
        recipient_phones = self.config.get("government_officials_phones", [])

        subject = f"Urgent Alert: {alert['alert_type']} - Severity {alert['severity']}"
        body = f"An alert has been triggered:\n\n" \
               f"Type: {alert['alert_type']}\n" \
               f"Severity: {alert['severity']}\n" \
               f"Content: {alert['content']}\n" \
               f"Triggered Threshold: {alert['threshold_triggered']}\n" \
               f"Created Date: {alert['created_date'].isoformat()}\n" \
               f"Original Data ID: {alert.get('original_data_id', 'N/A')}\n" \
               f"Original Data Type: {alert.get('original_data_type', 'N/A')}\n\n" \
               f"Please review the system dashboard for more details."

        email_sent = False
        for email in recipient_emails:
            if self.send_email_notification(email, subject, body):
                email_sent = True
        
        sms_sent = False
        for phone in recipient_phones:
            if self.send_sms_notification(phone, f"Alert: {alert['alert_type']} - {alert['content'][:100]}..."):
                sms_sent = True
        
        if not email_sent and not sms_sent:
            logging.warning(f"No notifications sent for alert: {alert['alert_type']}. Check configuration.")
            return False
        return True

if __name__ == '__main__':
    # Example Usage
    sample_config = {
        "email_notifications": {
            "enabled": True,
            "sender_email": "your_email@example.com",
            "sender_password": "your_email_password", # Use environment variables or secure storage in production
            "smtp_server": "smtp.example.com",
            "smtp_port": 587
        },
        "sms_notifications": {
            "enabled": False, # Set to True and configure Twilio for actual SMS
            # "twilio_account_sid": "ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            # "twilio_auth_token": "your_auth_token",
            # "twilio_phone_number": "+15017122661"
        },
        "government_officials_emails": ["official1@example.com", "official2@example.com"],
        "government_officials_phones": ["+919876543210"]
    }

    notifier = NotificationService(sample_config)

    sample_alert = {
        'alert_type': 'Negative Sentiment',
        'severity': 'High',
        'content': 'Strong negative sentiment detected in an article about a new policy.',
        'threshold_triggered': -0.7,
        'created_date': datetime.now(),
        'status': 'new',
        'original_data_id': 'art123',
        'original_data_type': 'article'
    }

    print("--- Sending notifications for sample alert ---")
    notifier.notify_officials(sample_alert)

    # Test email directly
    # if sample_config["email_notifications"]["enabled"]:
    #     notifier.send_email_notification(
    #         "test_recipient@example.com",
    #         "Test Email from News Monitoring System",
    #         "This is a test email from the notification service."
    #     )
