import os # Add this import at the top

# ... (keep all your social links and image helper functions exactly the same)

@app.route('/api/index', methods=['POST'])
def send_emails():
    try:
        data = request.json
        students = data.get('students')
        
        # Pull the password from Vercel Environment Variables
        password = os.environ.get('GMAIL_APP_PASSWORD') 
        
        sender = "adamasgamingclub@gmail.com"
        whatsapp = "https://whatsapp.com/channel/0029VbC1LwzJkK7Fn1REM332"

        if not password:
            return jsonify({"error": "Server password configuration missing"}), 500

        pending = [s for s in students if s.get("Status", "").strip().lower() == "pending"]
        
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender, password)
            for student in pending:
                msg = MIMEMultipart("related")
                msg["Subject"] = "Congratulations! Welcome to GameLiminals 🎮"
                msg["From"] = sender
                msg["To"] = student.get("Email")
                
                # Use your existing create_email_html function
                html_part = MIMEText(create_email_html(
                    student.get("Full Name"), 
                    student.get("Application ID"), 
                    whatsapp
                ), "html")
                msg.attach(html_part)
                
                club_img = load_image("logo.png", "clublogo")
                uni_img = load_image("au_logo.jpg", "unilogo")
                if club_img: msg.attach(club_img)
                if uni_img: msg.attach(uni_img)
                
                server.sendmail(sender, student.get("Email"), msg.as_string())

        return jsonify({"success": True, "sent": len(pending)}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500