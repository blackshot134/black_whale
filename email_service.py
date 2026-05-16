import smtplib
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()

EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_USERNAME = os.getenv("EMAIL_USERNAME")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_FROM = os.getenv("EMAIL_FROM")

def generate_verification_code() -> str:
    return str(random.randint(100000, 999999))

def send_verification_email(to_email: str, code: str) -> bool:
    if not EMAIL_USERNAME or not EMAIL_PASSWORD:
        print(f"[TEST] Verification code for {to_email}: {code}")
        return True
    
    subject = "Black Whale - Email Verification"
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="UTF-8"></head>
    <body style="font-family: Arial, sans-serif; background: #0a0a0a; color: #fff; padding: 40px;">
        <div style="max-width: 500px; margin: 0 auto; background: linear-gradient(135deg, #1a1a2e, #0a0a0a); border-radius: 20px; padding: 30px; text-align: center; border: 1px solid #00d4ff;">
            <h1 style="color: #00d4ff;">🐋 BLACK WHALE</h1>
            <h2>Verify Your Email</h2>
            <p>Use the code below to complete your registration:</p>
            <div style="font-size: 36px; font-weight: bold; letter-spacing: 5px; color: #00d4ff; margin: 20px 0;">{code}</div>
            <p>This code expires in <strong>10 minutes</strong>.</p>
            <hr style="border-color: #333;">
            <p style="font-size: 12px; color: #666;">Black Whale Security System</p>
        </div>
    </body>
    </html>
    """
    
    msg = MIMEMultipart()
    msg["From"] = EMAIL_FROM
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(html, "html"))
    
    try:
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()
        server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False

def send_welcome_email(to_email: str, username: str) -> bool:
    if not EMAIL_USERNAME or not EMAIL_PASSWORD:
        return True
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="UTF-8"></head>
    <body style="font-family: Arial, sans-serif; background: #0a0a0a; color: #fff; padding: 40px;">
        <div style="max-width: 500px; margin: 0 auto; background: linear-gradient(135deg, #1a1a2e, #0a0a0a); border-radius: 20px; padding: 30px; text-align: center; border: 1px solid #00d4ff;">
            <h1 style="color: #00d4ff;">🐋 Welcome to Black Whale</h1>
            <p>Hi <strong>{username}</strong>,</p>
            <p>Your account has been verified successfully!</p>
            <p>You now have access to:</p>
            <ul style="text-align: left;">
                <li>SMS Bomber (85+ APIs)</li>
                <li>Intruder Search Database</li>
                <li>Sheypoor & Divar Scraper</li>
                <li>Live Location Tracking</li>
                <li>Real-time Dashboard</li>
            </ul>
            <p>Current Plan: <strong style="color: #cd7f32;">BRONZE</strong> (Free)</p>
            <hr style="border-color: #333;">
            <p style="font-size: 12px; color: #666;">Black Whale Security System</p>
        </div>
    </body>
    </html>
    """
    
    msg = MIMEMultipart()
    msg["From"] = EMAIL_FROM
    msg["To"] = to_email
    msg["Subject"] = "Welcome to Black Whale!"
    msg.attach(MIMEText(html, "html"))
    
    try:
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()
        server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except:
        return False