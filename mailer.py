import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app
from config import Config

class Mailer:
    def __init__(self):
        self.mail_server = Config.MAIL_SERVER
        self.mail_port = Config.MAIL_PORT
        self.mail_use_tls = Config.MAIL_USE_TLS
        self.mail_username = Config.MAIL_USERNAME
        self.mail_password = Config.MAIL_PASSWORD
        self.mail_sender = Config.MAIL_SENDER
        self.client_origin = Config.CLIENT_ORIGIN
        
    def send_email(self, to_email: str, subject: str, html_content: str, text_content: str = None):
        """Send email using SMTP or print to console in development"""
        
        # In development mode, print to console instead of sending
        if os.environ.get('FLASK_ENV') == 'development' or not self.mail_server:
            print(f"\n{'='*50}")
            print(f"EMAIL TO: {to_email}")
            print(f"SUBJECT: {subject}")
            print(f"HTML CONTENT:")
            print(html_content)
            if text_content:
                print(f"TEXT CONTENT:")
                print(text_content)
            print(f"{'='*50}\n")
            return True
            
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.mail_sender
            msg['To'] = to_email
            
            # Add text and HTML parts
            if text_content:
                text_part = MIMEText(text_content, 'plain', 'utf-8')
                msg.attach(text_part)
            
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.mail_server, self.mail_port) as server:
                if self.mail_use_tls:
                    server.starttls()
                if self.mail_username and self.mail_password:
                    server.login(self.mail_username, self.mail_password)
                server.send_message(msg)
            
            return True
            
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False
    
    def send_email_verification(self, to_email: str, name: str, token: str):
        """Send email verification email"""
        verification_url = f"{self.client_origin}/verify-email?token={token}"
        
        subject = "Hatch 이메일 인증"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>이메일 인증</title>
        </head>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="text-align: center; margin-bottom: 30px;">
                <h1 style="color: #4F46E5; margin-bottom: 10px;">Hatch</h1>
                <h2 style="color: #333;">이메일 인증</h2>
            </div>
            
            <div style="background-color: #f8f9fa; padding: 30px; border-radius: 10px; margin-bottom: 20px;">
                <p style="font-size: 16px; color: #333; margin-bottom: 20px;">
                    안녕하세요 <strong>{name}</strong>님,
                </p>
                <p style="font-size: 16px; color: #333; margin-bottom: 20px;">
                    Hatch 계정 생성을 완료하려면 아래 버튼을 클릭하여 이메일을 인증해주세요.
                </p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{verification_url}" 
                       style="background-color: #4F46E5; color: white; padding: 15px 30px; text-decoration: none; border-radius: 25px; font-weight: bold; display: inline-block;">
                        이메일 인증하기
                    </a>
                </div>
                
                <p style="font-size: 14px; color: #666; margin-top: 20px;">
                    버튼이 작동하지 않는다면 아래 링크를 복사하여 브라우저에 붙여넣으세요:
                </p>
                <p style="font-size: 12px; color: #999; word-break: break-all;">
                    {verification_url}
                </p>
            </div>
            
            <div style="text-align: center; color: #666; font-size: 12px;">
                <p>이 링크는 30분 후에 만료됩니다.</p>
                <p>© 2024 Hatch. All rights reserved.</p>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Hatch 이메일 인증
        
        안녕하세요 {name}님,
        
        Hatch 계정 생성을 완료하려면 아래 링크를 클릭하여 이메일을 인증해주세요:
        
        {verification_url}
        
        이 링크는 30분 후에 만료됩니다.
        
        © 2024 Hatch. All rights reserved.
        """
        
        return self.send_email(to_email, subject, html_content, text_content)
    
    def send_password_reset(self, to_email: str, name: str, token: str):
        """Send password reset email"""
        reset_url = f"{self.client_origin}/reset-password?token={token}"
        
        subject = "Hatch 비밀번호 재설정"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>비밀번호 재설정</title>
        </head>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="text-align: center; margin-bottom: 30px;">
                <h1 style="color: #4F46E5; margin-bottom: 10px;">Hatch</h1>
                <h2 style="color: #333;">비밀번호 재설정</h2>
            </div>
            
            <div style="background-color: #f8f9fa; padding: 30px; border-radius: 10px; margin-bottom: 20px;">
                <p style="font-size: 16px; color: #333; margin-bottom: 20px;">
                    안녕하세요 <strong>{name}</strong>님,
                </p>
                <p style="font-size: 16px; color: #333; margin-bottom: 20px;">
                    비밀번호 재설정 요청을 받았습니다. 아래 버튼을 클릭하여 새 비밀번호를 설정해주세요.
                </p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{reset_url}" 
                       style="background-color: #4F46E5; color: white; padding: 15px 30px; text-decoration: none; border-radius: 25px; font-weight: bold; display: inline-block;">
                        비밀번호 재설정하기
                    </a>
                </div>
                
                <p style="font-size: 14px; color: #666; margin-top: 20px;">
                    버튼이 작동하지 않는다면 아래 링크를 복사하여 브라우저에 붙여넣으세요:
                </p>
                <p style="font-size: 12px; color: #999; word-break: break-all;">
                    {reset_url}
                </p>
                
                <div style="background-color: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin-top: 20px;">
                    <p style="font-size: 14px; color: #856404; margin: 0;">
                        <strong>보안 안내:</strong> 이 요청을 하지 않으셨다면 이 이메일을 무시하세요. 
                        비밀번호는 변경되지 않습니다.
                    </p>
                </div>
            </div>
            
            <div style="text-align: center; color: #666; font-size: 12px;">
                <p>이 링크는 15분 후에 만료됩니다.</p>
                <p>© 2024 Hatch. All rights reserved.</p>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Hatch 비밀번호 재설정
        
        안녕하세요 {name}님,
        
        비밀번호 재설정 요청을 받았습니다. 아래 링크를 클릭하여 새 비밀번호를 설정해주세요:
        
        {reset_url}
        
        보안 안내: 이 요청을 하지 않으셨다면 이 이메일을 무시하세요. 비밀번호는 변경되지 않습니다.
        
        이 링크는 15분 후에 만료됩니다.
        
        © 2024 Hatch. All rights reserved.
        """
        
        return self.send_email(to_email, subject, html_content, text_content)

# Global mailer instance
mailer = Mailer()






