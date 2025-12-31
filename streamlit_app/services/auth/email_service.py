"""
Email Service - Handles email verification and SMTP operations
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import streamlit as st


class EmailService:
    """
    Service for handling email operations including verification emails.
    """

    def __init__(self):
        """Initialize email service with default values. Secrets are accessed lazily."""
        self._smtp_server = None
        self._smtp_port = None
        self._username = None
        self._password = None
        self._from_email = None
        self._from_name = None

    @property
    def smtp_server(self) -> str:
        """Get SMTP server from secrets or cache."""
        if self._smtp_server is None:
            self._smtp_server = st.secrets.get("EMAIL_SMTP_SERVER", "")
        return self._smtp_server

    @property
    def smtp_port(self) -> int:
        """Get SMTP port from secrets or cache."""
        if self._smtp_port is None:
            self._smtp_port = int(st.secrets.get("EMAIL_SMTP_PORT", "587"))
        return self._smtp_port

    @property
    def username(self) -> str:
        """Get email username from secrets or cache."""
        if self._username is None:
            self._username = st.secrets.get("EMAIL_USERNAME", "")
        return self._username

    @property
    def password(self) -> str:
        """Get email password from secrets or cache."""
        if self._password is None:
            self._password = st.secrets.get("EMAIL_PASSWORD", "")
        return self._password

    @property
    def from_email(self) -> str:
        """Get from email from secrets or cache."""
        if self._from_email is None:
            username = st.secrets.get("EMAIL_USERNAME", "")
            self._from_email = st.secrets.get("EMAIL_FROM", username)
        return self._from_email

    @property
    def from_name(self) -> str:
        """Get from name from secrets or cache."""
        if self._from_name is None:
            self._from_name = st.secrets.get("EMAIL_FROM_NAME", "Language Learning App")
        return self._from_name

    def is_configured(self) -> bool:
        """
        Check if email service is properly configured.

        Returns:
            bool: True if all required email settings are configured
        """
        return all([
            self.smtp_server,
            self.smtp_port,
            self.username,
            self.password
        ])

    def send_verification_email(self, email: str, verification_link: str) -> bool:
        """
        Send verification email using SMTP.

        Args:
            email: Recipient email address
            verification_link: Email verification link

        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        if not self.is_configured():
            st.error("Email service not configured")
            return False

        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = "Verify Your Email - Language Learning App"
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = email

            # HTML content
            html = f"""
            <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #333;">Welcome to Language Anki Deck Generator! 🎓</h2>
                <p>Thank you for creating an account. To complete your registration, please verify your email address by clicking the button below:</p>

                <div style="text-align: center; margin: 30px 0;">
                    <a href="{verification_link}" style="background-color: #4CAF50; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; display: inline-block;">Verify Email Address</a>
                </div>

                <p><strong>Verification Link:</strong><br>
                <a href="{verification_link}">{verification_link}</a></p>

                <p>If you didn't create an account, you can safely ignore this email.</p>

                <hr style="margin: 30px 0; border: none; border-top: 1px solid #eee;">
                <p style="color: #666; font-size: 12px;">This email was sent by Language Anki Deck Generator. If you have any questions, please contact support.</p>
            </body>
            </html>
            """

            # Plain text content
            text = f"""
            Welcome to Language Anki Deck Generator!

            Thank you for creating an account. To complete your registration, please verify your email address by clicking this link:

            {verification_link}

            If you didn't create an account, you can safely ignore this email.

            This email was sent by Language Anki Deck Generator.
            """

            # Attach parts
            part1 = MIMEText(text, 'plain')
            part2 = MIMEText(html, 'html')
            msg.attach(part1)
            msg.attach(part2)

            # Send email
            print(f"Email config - Server: {self.smtp_server}, Port: {self.smtp_port}, User: {self.username}, From: {self.from_email}")
            print(f"Connecting to SMTP server {self.smtp_server}:{self.smtp_port}")
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            print(f"Logging in as {self.username}")
            server.login(self.username, self.password)
            print(f"Sending email to {email}")
            server.sendmail(self.from_email, email, msg.as_string())
            server.quit()

            print(f"Verification email sent successfully to {email}")
            return True

        except Exception as e:
            print(f"Failed to send verification email to {email}: {str(e)}")
            import traceback
            traceback.print_exc()
            return False