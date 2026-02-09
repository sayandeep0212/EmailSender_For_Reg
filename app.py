from flask import Flask, request, jsonify, render_template_string
import json
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import os

app = Flask(__name__)

SOCIAL_LINKS = {
    "GitHub": "https://github.com/gameliminals",
    "Discord": "https://discord.com/invite/5hZsZmcC",
    "Instagram": "https://www.instagram.com/gameliminals",
    "LinkedIn": "https://www.linkedin.com/company/gameliminals/",
}

def create_email_html(student_name, reg_id, whatsapp_link):
    links_html = " | ".join([f'<a href="{url}">{platform}</a>' for platform, url in SOCIAL_LINKS.items()])
    return f"""
    <html>
      <body style="font-family: Arial; padding: 20px;">
        <h2 style="color: #2E7D32;">Welcome to GameLiminals! 🎮</h2>
        <p>Dear <b>{student_name}</b>,</p>
        <p>Your registration ID is: <b>{reg_id}</b></p>
        <p><a href="{whatsapp_link}" style="background: #25D366; color: white; padding: 10px; text-decoration: none; border-radius: 5px;">Join WhatsApp Channel</a></p>
        <hr>
        <p>{links_html}</p>
      </body>
    </html>
    """

@app.route('/', methods=['GET'])
def index():
    return render_template_string('''
        <h1>GameLiminals Email Manager</h1>
        <form action="/send-emails" method="post" enctype="multipart/form-data">
            <input type="password" name="password" placeholder="App Password" required><br><br>
            <input type="file" name="file" accept=".json" required><br><br>
            <button type="submit">Send Emails</button>
        </form>
    ''')

@app.route('/send-emails', methods=['POST'])
def send_emails():
    sender_email = "adamasgamingclub@gmail.com"
    sender_password = request.form.get('password')
    whatsapp_link = "https://whatsapp.com/channel/0029VbC1LwzJkK7Fn1REM332"
    
    file = request.files['file']
    students = json.load(file)
    pending_students = [s for s in students if s.get("Status", "").strip().lower() == "pending"]

    success_count = 0
    context = ssl.create_default_context()

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender_email, sender_password)
            for student in pending_students:
                email = student.get("Email")
                if email:
                    msg = MIMEMultipart()
                    msg["Subject"] = "Congratulations! Welcome to GameLiminals 🎮"
                    msg["From"] = sender_email
                    msg["To"] = email
                    
                    html = create_email_html(student.get("Full Name", "Student"), student.get("Application ID", "N/A"), whatsapp_link)
                    msg.attach(MIMEText(html, "html"))
                    server.sendmail(sender_email, email, msg.as_string())
                    success_count += 1
        return f"Successfully sent {success_count} emails!"
    except Exception as e:
        return f"Error: {str(e)}", 500

# Vercel needs this
def handler(event, context):
    return app(event, context)
