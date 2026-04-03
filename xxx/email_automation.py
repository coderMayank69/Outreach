import smtplib
import pandas as pd # pyright: ignore[reportMissingModuleSource]
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time
from datetime import datetime
import os
import sys

class EmailAutomation:
    def __init__(self):
        """Initialize the email automation system"""
        self.gmail_user = ""
        self.gmail_password = ""  # App password
        self.email_list_file = "email_list.csv"
        self.delay_between_emails = 30  # seconds

    def setup_gmail_credentials(self):
        """Setup Gmail credentials"""
        print("🔐 Gmail Setup")
        print("=" * 40)
        print("You need to generate an App Password in Gmail:")
        print("1. Go to Gmail Settings > Security")
        print("2. Enable 2-Factor Authentication")
        print("3. Generate App Password")
        print("4. Use that 16-character password here\n")

        self.gmail_user = input("Enter your Gmail address: ").strip()
        self.gmail_password = input("Enter your Gmail App Password: ").strip()

        # Save credentials to file for future use (optional)
        save_creds = input("Save credentials for future use? (y/n): ").lower()
        if save_creds == 'y':
            with open('gmail_config.txt', 'w') as f:
                f.write(f"EMAIL={self.gmail_user}\n")
                f.write(f"PASSWORD={self.gmail_password}\n")
            print("✅ Credentials saved to gmail_config.txt")

    def load_credentials(self):
        """Load saved credentials"""
        if os.path.exists('gmail_config.txt'):
            try:
                with open('gmail_config.txt', 'r') as f:
                    lines = f.readlines()
                    for line in lines:
                        if line.startswith('EMAIL='):
                            self.gmail_user = line.split('=')[1].strip()
                        elif line.startswith('PASSWORD='):
                            self.gmail_password = line.split('=')[1].strip()
                print("✅ Loaded saved credentials")
                return True
            except Exception as e:
                print(f"❌ Error loading credentials: {e}")
        return False

    def load_email_list(self):
        """Load email list from CSV"""
        if not os.path.exists(self.email_list_file):
            print(f"❌ Email list file '{self.email_list_file}' not found!")
            print("Create it using: python create_email_list.py")
            return None

        try:
            df = pd.read_csv(self.email_list_file)
            print(f"✅ Loaded {len(df)} email addresses")
            return df
        except Exception as e:
            print(f"❌ Error loading email list: {e}")
            return None

    def create_email_content(self):
        """Create the email content"""
        subject = "I had made something for you!"

        # Email body with your requirements
        body = """
        <html>
        <head></head>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="padding: 20px;">
                <h2 style="color: #333;">I had made something for you!</h2>

                <p>Hi,</p>

                <p>I'm a professional thumbnail designer and I've created something special that I think could really help boost your content's performance!</p>

                <div style="background-color: #f8f9fa; padding: 15px; border-left: 4px solid #007bff; margin: 20px 0;">
                    <h3 style="margin-top: 0; color: #007bff;">🎬 Watch My 2-Minute Pitch</h3>
                    <p><a href="https://youtu.be/1MIbIcsms3M?feature=shared" style="color: #007bff; text-decoration: none; font-weight: bold;">► Click here to see what I can do for your channel</a></p>
                </div>

                <div style="background-color: #f8f9fa; padding: 15px; border-left: 4px solid #28a745; margin: 20px 0;">
                    <h3 style="margin-top: 0; color: #28a745;">🎨 View My Portfolio</h3>
                    <p><a href="https://www.behance.net/gallery/215773425/Portfolio" style="color: #28a745; text-decoration: none; font-weight: bold;">► Check out my recent thumbnail designs</a></p>
                </div>

                <p><strong>What I offer:</strong></p>
                <ul style="line-height: 1.6;">
                    <li>🎯 Click-worthy thumbnail designs that boost CTR</li>
                    <li>⚡ 24-48 hour delivery</li>
                    <li>🔄 Unlimited revisions</li>
                    <li>💰 Affordable pricing for creators</li>
                </ul>

                <p>I'd love to create something amazing for your channel. Interested in seeing what I can do?</p>

                <hr style="border: 1px solid #eee; margin: 30px 0;">

                <div style="text-align: center; background-color: #f8f9fa; padding: 20px; border-radius: 5px;">
                    <p style="margin: 0; font-weight: bold;">Ready to get started?</p>
                    <p style="margin: 10px 0 0 0; color: #666;">
                        📱 <strong>WhatsApp/Call:</strong> <a href="tel:+918115529832" style="color: #007bff;">+91 8115529832</a><br>
                    </p>
                </div>

                <p style="font-size: 12px; color: #666; margin-top: 30px;">
                    <em>If you're not interested, simply reply with "UNSUBSCRIBE" and I won't contact you again.</em>
                </p>
            </div>
        </body>
        </html>
        """.format(gmail_user=self.gmail_user)

        return subject, body

    def send_single_email(self, to_email, subject, body):
        """Send a single email"""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.gmail_user
            msg['To'] = to_email

            # Add HTML body
            html_part = MIMEText(body, 'html')
            msg.attach(html_part)

            # Send email
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.login(self.gmail_user, self.gmail_password)
            server.send_message(msg)
            server.quit()

            return True, "Sent successfully"

        except Exception as e:
            return False, str(e)

    def update_email_status(self, df, index, status):
        """Update email status in DataFrame"""
        df.at[index, 'status'] = status
        df.at[index, 'last_sent'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return df

    def send_bulk_emails(self):
        """Send emails to all unsent addresses"""
        # Load credentials
        if not self.load_credentials():
            self.setup_gmail_credentials()

        # Load email list
        df = self.load_email_list()
        if df is None:
            return

        # Get unsent emails
        unsent_emails = df[df['status'] == 'Not Sent']

        if len(unsent_emails) == 0:
            print("✅ No unsent emails found!")
            return

        print(f"📧 Found {len(unsent_emails)} unsent emails")
        print("Starting email sending process...\n")

        # Create email content
        subject, body = self.create_email_content()

        # Send emails
        sent_count = 0
        failed_count = 0

        for index, row in unsent_emails.iterrows():
            email_address = row['email']

            print(f"Sending to: {email_address}")

            # Send email
            success, message = self.send_single_email(email_address, subject, body)

            if success:
                print(f"✅ Sent successfully")
                df = self.update_email_status(df, index, 'Sent')
                sent_count += 1
            else:
                print(f"❌ Failed: {message}")
                df = self.update_email_status(df, index, 'Failed')
                failed_count += 1

            # Save progress after each email
            df.to_csv(self.email_list_file, index=False)

            # Delay between emails
            if index < len(unsent_emails) - 1:  # Don't delay after last email
                print(f"⏳ Waiting {self.delay_between_emails} seconds...\n")
                time.sleep(self.delay_between_emails)

        # Final summary
        print("=" * 50)
        print("📊 FINAL SUMMARY")
        print("=" * 50)
        print(f"✅ Emails sent successfully: {sent_count}")
        print(f"❌ Emails failed: {failed_count}")
        print(f"📁 Updated email list saved to: {self.email_list_file}")
        print("=" * 50)

    def show_statistics(self):
        """Show email statistics"""
        df = self.load_email_list()
        if df is None:
            return

        print("📊 EMAIL STATISTICS")
        print("=" * 30)
        status_counts = df['status'].value_counts()
        for status, count in status_counts.items():
            print(f"{status}: {count}")
        print(f"Total: {len(df)}")
        print("=" * 30)

# Main execution
if __name__ == "__main__":
    automation = EmailAutomation()

    print("🚀 EMAIL AUTOMATION SYSTEM")
    print("=" * 40)
    print("1. Send bulk emails")
    print("2. Show statistics")
    print("3. Exit")

    choice = input("\nEnter your choice (1-3): ").strip()

    if choice == '1':
        automation.send_bulk_emails()
    elif choice == '2':
        automation.show_statistics()
    else:
        print("Goodbye!")
