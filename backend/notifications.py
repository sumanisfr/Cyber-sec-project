"""Notification helpers for alerts (email + Slack)."""

import os
import smtplib
import traceback
from email.message import EmailMessage

import requests


def send_email(subject: str, body: str, to_addrs=None):
    """Send a basic email alert using SMTP config from env."""
    to_addrs = to_addrs or os.getenv('ALERT_EMAIL_TO', '').split(',')
    if not to_addrs or not os.getenv('ALERT_EMAIL_HOST'):
        return False

    try:
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = os.getenv('ALERT_EMAIL_FROM', 'no-reply@example.com')
        msg['To'] = ','.join([a for a in to_addrs if a])
        msg.set_content(body)

        with smtplib.SMTP(os.getenv('ALERT_EMAIL_HOST'), int(os.getenv('ALERT_EMAIL_PORT', '25'))) as smtp:
            if os.getenv('ALERT_EMAIL_STARTTLS', 'false').lower() in ('1', 'true', 'yes'):
                smtp.starttls()
            username = os.getenv('ALERT_EMAIL_USER')
            password = os.getenv('ALERT_EMAIL_PASS')
            if username and password:
                smtp.login(username, password)
            smtp.send_message(msg)
        return True
    except Exception:
        traceback.print_exc()
        return False


def send_slack(message: str):
    """Send a Slack message via Incoming Webhook."""
    webhook = os.getenv('SLACK_WEBHOOK_URL')
    if not webhook:
        return False
    try:
        requests.post(webhook, json={'text': message}, timeout=5)
        return True
    except Exception:
        traceback.print_exc()
        return False


def alert(subject: str, body: str):
    """Send alert using configured channels."""
    send_email(subject, body)
    send_slack(f"*{subject}*\n{body}")
