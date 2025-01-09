from passlib.context import CryptContext
from datetime import datetime, timedelta
from database.users import User_database
from jose import jwt,JWTError
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from fastapi import HTTPException
import random 
import string
import secrets



pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "my_secret_key"

class user_functions():
    def __init__(self):
        pass
    async def get_password_hash(password):
        return pwd_context.hash(password)
    
    async def authenticate_user(username: str, password: str):
        user = await User_database.get_user_from_email(username)
        if user=="RecordNotFound":
            return "invalid_username"
        else:
            return user
        
    async def create_access_token(data: dict, expires_delta: timedelta = None):
        to_encode = data
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=10)
        to_encode.update({ "expires": expire.isoformat() })
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY,algorithm="HS256")
        return encoded_jwt
    async def send_email(receiver_email,verification_code):
        subject = "Account Verification"
        html_content = """
        <!doctype html>
        <html lang="en">
        <head>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
            <title>Account Verification</title>
            <style media="all" type="text/css">
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333333;
                    background-color: #f4f5f6;
                    margin: 0;
                    padding: 0;
                }}
                .container {{
                    max-width: 600px;
                    margin: 20px auto;
                    padding: 20px;
                    background-color: #ffffff;
                    border-radius: 8px;
                    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                }}
                h1 {{
                    color: #2275eb;
                    text-align: center;
                    margin-bottom: 30px;
                }}
                p {{
                    margin-bottom: 20px;
                }}
                strong {{
                    color: #2275eb;
                }}
                .verification-code {{
                    font-size: 24px;
                    font-weight: bold;
                    color: #2275eb;
                }}
                .circle-container {{
                    display: flex;
                    align-items: center;
                    font-family: Helvetica, sans-serif;
                    font-size: 24px;
                    font-weight: bold;
                    margin: 0;
                    margin-bottom: 16px;
                    margin-top:3px;
                }}
                
                .circle-container img {{
                    width: 100px;
                    height: 100px;
                    border-radius: 50%; /* Makes the image round */
                    margin-right: 10px; /* Add some space between the image and text */
                    
                }}
                
            </style>
            <script src='https://kit.fontawesome.com/a076d05399.js' crossorigin='anonymous'></script>
        </head>
        <body>
            <div class="container">
                <h5 style=" font-family: Helvetica, sans-serif; font-size: 16px; vertical-align: top; text-align: center;  color: white; padding: 1rem 2rem; background-color: #2275eb; border-radius: 10px; border-top: 1px solid #0867ec; border-bottom: 1px solid #0867ec;">
                Verification code: {}
                </h5>
                <h4>Please use this verification code to complete your account setup.</h4>
                <h4>If you didn't request this code, you can safely ignore this email.</h4>
                <br>
            </div>
        </body>
        </html>
        """.format(verification_code)
        # Create message
        message = MIMEMultipart()
        message['From'] = "ThinkCompanionAlly@gmail.com"
        message['To'] = receiver_email
        message['Subject'] = subject

        # Attach HTML content
        message.attach(MIMEText(html_content, 'html'))

        # Connect to SMTP server
        try:
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login("ThinkCompanionAlly@gmail.com", "ihto ailv uahu ytzk")
                server.send_message(message)
                return "sent"
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
    async def generate_verification_token(length=6):
        letters_and_digits = string.ascii_letters + string.digits
        return ''.join(random.choice(letters_and_digits) for i in range(length))
    
    async def generate_reset_token():
        reset_token_length = 32
        return secrets.token_urlsafe(reset_token_length)
    async def send_reset_password_email(receiver_email, reset_token):
        subject = "Password Reset"
        html_content = """
        <!doctype html>
        <html lang="en">
        <head>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
            <title>Password Reset</title>
            <style media="all" type="text/css">
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333333;
                    background-color: #f4f5f6;
                    margin: 0;
                    padding: 0;
                }}
                .container {{
                    max-width: 600px;
                    margin: 20px auto;
                    padding: 20px;
                    background-color: #ffffff;
                    border-radius: 8px;
                    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                }}
                h1 {{
                    color: #2275eb;
                    text-align: center;
                    margin-bottom: 30px;
                }}
                p {{
                    margin-bottom: 20px;
                }}
                strong {{
                    color: #2275eb;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Password Reset</h1>
                <p>You are receiving this email because a password reset request was made for your account.</p>
                <p>If you did not request a password reset, please ignore this email.</p>
                # <p>To reset your password, click the link below:</p>
                # <p><a href="https://chumsai.in/reset-password?token={reset_token}">Reset Password</a></p>
                # <p>If the above link doesn't work, copy and paste the following URL into your web browser's address bar:</p>
                # <p>token={reset_token}</p>
                # <p>This link will expire in 24 hours.</p>
            </div>
        </body>
        </html>
        """.format(reset_token=reset_token)

        # Create message
        message = MIMEMultipart()
        message['From'] = "ThinkCompanionAlly@gmail.com"
        message['To'] = receiver_email
        message['Subject'] = subject

        # Attach HTML content
        message.attach(MIMEText(html_content, 'html'))

        # Connect to SMTP server
        try:
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login("ThinkCompanionAlly@gmail.com", "ihto ailv uahu ytzk")
                server.send_message(message)
                return "sent"
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

