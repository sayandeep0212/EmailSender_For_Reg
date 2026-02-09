from flask import Flask, request, jsonify
import json
import smtplib
import ssl
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage

app = Flask(__name__)

SOCIAL_LINKS = {
    "GitHub": "https://github.com/gameliminals",
    "Discord": "https://discord.com/invite/5hZsZmcC",
    "Instagram": "https://www.instagram.com/gameliminals?igsh=b2V3NzRidDd3OHF6",
    "LinkedIn": "https://www.linkedin.com/company/gameliminals/",
    "Youtube": "https://www.youtube.com/@GameLiminals",
    "Facebook": "https://www.facebook.com/gameliminals"
}

def load_image(filename, content_id):
    # In Vercel, the root directory is accessible via os.getcwd()
    path = os.path.join(os.getcwd(), filename)
    try:
        with open(path, 'rb') as f:
            img_data = f.read()
            img = MIMEImage(img_data)
            img.add_header('Content-ID', f'<{content_id}>')
            return img
    except Exception:
        return None

def create_email_html(student_name, reg_id, whatsapp_link):
    links_html = " | ".join([f'<a href="{url}" style="color: #2E7D32; text-decoration: none;">{platform}</a>' 
                             for platform, url in SOCIAL_LINKS.items()])
    return f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #333;">
        <div style="max-width: 600px; margin: auto; border: 1px solid #ddd; padding: 20px; border-radius: 10px;">
            <table width="100%" style="border-bottom: 2px solid #2E7D32; padding-bottom: 10px; margin-bottom: 20px;">
                <tr>
                    <td align="left" width="50%"><img src="cid:unilogo" alt="Adamas University" style="height: 60px;"></td>
                    <td align="right" width="50%"><img src="cid:clublogo" alt="GameLiminals" style="height: 60px;"></td>
                </tr>
            </table>
            <h2 style="color: #2E7D32;">Welcome to GameLiminals! 🎮</h2>
            <p>Dear <b>{student_name}</b>,</p>
            <p>Congratulations! Your registration for <b>GameLiminals</b> has been approved.</p>
            <div style="background-color: #f1f8e9; padding: 15px; border-left: 5px solid #558b2f; margin: 20px 0;">
                <p><b>Registration ID:</b> {reg_id}</p>
            </div>
            <div style="text-align: center; margin: 30px 0;">
                <a href="{whatsapp_link}" style="background-color: #25D366; color: white; padding: 12px 24px; text-decoration: none; border-radius: 25px;">Join WhatsApp Channel 📱</a>
            </div>
            <p style="font-size: 0.9em;"><b>Connect with us:</b><br>{links_html}</p>
        </div>
      </body>
    </html>
    """

@app.route('/api/index', methods=['POST'])
def send_emails():
    try:
        data = request.json
        students = data.get('students')
        password = data.get('password') # Send your App Password in the JSON body
        sender = "adamasgamingclub@gmail.com"
        whatsapp = "https://whatsapp.com/channel/0029VbC1LwzJkK7Fn1REM332"

        pending = [s for s in students if s.get("Status", "").strip().lower() == "pending"]
        
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender, password)
            for student in pending:
                msg = MIMEMultipart("related")
                msg["Subject"] = "Congratulations! Welcome to GameLiminals 🎮"
                msg["From"] = sender
                msg["To"] = student.get("Email")
                
                html_part = MIMEText(create_email_html(student.get("Full Name"), student.get("Application ID"), whatsapp), "html")
                msg.attach(html_part)
                
                club_img = load_image("logo.png", "clublogo")
                uni_img = load_image("au_logo.jpg", "unilogo")
                if club_img: msg.attach(club_img)
                if uni_img: msg.attach(uni_img)
                
                server.sendmail(sender, student.get("Email"), msg.as_string())

        return jsonify({"success": True, "sent": len(pending)}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
