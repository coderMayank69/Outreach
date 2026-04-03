import smtplib
import pandas as pd # pyright: ignore[reportMissingModuleSource]
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time
from datetime import datetime
import os
import sys

class PersonalEmailAutomation:
    def __init__(self):
        """Initialize with personal email approach"""
        self.gmail_user = ""
        self.gmail_password = ""
        self.email_list_file = "email_list.csv"
        self.delay_between_emails = 45  # Longer delay for better reputation
        self.your_name = ""  # Will be set during setup
        self.portfolio_link = ""
        self.video_link = ""

    def setup_gmail_credentials(self):
        """Setup Gmail credentials and personal info"""
        print("🔐 Gmail & Personal Setup")
        print("=" * 40)
        print("You need to generate an App Password in Gmail:")
        print("1. Go to Gmail Settings > Security")
        print("2. Enable 2-Factor Authentication")
        print("3. Generate App Password")
        print("4. Use that 16-character password here\n")

        self.gmail_user = input("Enter your Gmail address: ").strip()
        self.gmail_password = input("Enter your Gmail App Password: ").strip()

        print("\n📝 Personal Information (for email personalization):")
        self.your_name = input("Enter your name: ").strip()
        self.portfolio_link = input("Enter your portfolio link: ").strip()
        self.video_link = input("Enter your intro video link (optional): ").strip()

        # Save credentials and info
        save_creds = input("\nSave this info for future use? (y/n): ").lower()
        if save_creds == 'y':
            with open('gmail_config.txt', 'w') as f:
                f.write(f"EMAIL={self.gmail_user}\n")
                f.write(f"PASSWORD={self.gmail_password}\n")
                f.write(f"NAME={self.your_name}\n")
                f.write(f"PORTFOLIO={self.portfolio_link}\n")
                f.write(f"VIDEO={self.video_link}\n")
            print("✅ Information saved to gmail_config.txt")

    def load_credentials(self):
        """Load saved credentials and personal info"""
        if os.path.exists('gmail_config.txt'):
            try:
                with open('gmail_config.txt', 'r') as f:
                    lines = f.readlines()
                    for line in lines:
                        if line.startswith('EMAIL='):
                            self.gmail_user = line.split('=')[1].strip()
                        elif line.startswith('PASSWORD='):
                            self.gmail_password = line.split('=')[1].strip()
                        elif line.startswith('NAME='):
                            self.your_name = line.split('=')[1].strip()
                        elif line.startswith('PORTFOLIO='):
                            self.portfolio_link = line.split('=')[1].strip()
                        elif line.startswith('VIDEO='):
                            self.video_link = line.split('=')[1].strip()
                print("✅ Loaded saved information")
                return True
            except Exception as e:
                print(f"❌ Error loading information: {e}")
        return False

    def get_personal_email_templates(self):
        """Get different personal email templates"""
        templates = []

        # Template 1: The Genuine Interest Approach
        template1 = {
            'subject': f"Loved your recent video!",
            'body': f"""Hi,

I came across your youtube channel and really enjoyed your recent videos! Your content style is exactly what I think would benefit from some thumbnail improvements.

I'm a thumbnail designer from India, and I've been helping creators increase their click-through rates. I can make a quick sample for one of your video.

Would you be interested in seeing it? It's completely free - I just enjoy helping creators grow.

You can check out some of my other work here: {self.portfolio_link}

Let me know what you think!

Best,
{self.your_name}
WhatsApp: +91 8115529832

P.S. If thumbnails aren't a priority for you right now, no worries at all - just let me know and I won't bother you again."""
        }

        # Template 2: The Helper Approach
        template2 = {
            'subject': f"Quick suggestion for your channel",
            'body': f"""Hey,

I've been watching some creators in your niche, and your content really stands out. Great work!

I noticed one thing that could potentially help you get even more views - your thumbnails have room for improvement.

I'm a thumbnail designer and I can create a thumbnail for one of your videos. 

Here's a quick video about my approach: {self.video_link if self.video_link else self.portfolio_link}

Let me know if you're interested

Either way, keep up the excellent content!

Cheers,
{self.your_name}
+91 8115529832

My work: {self.portfolio_link}"""
        }

        # Template 3: The Collaboration Approach  
        template3 = {
            'subject': f"Collaboration opportunity",
            'body': f"""Hi,

I'm {self.your_name}, a thumbnail designer based in India. I've been following creators in your space and your content caught my attention.

I think there's an opportunity to make your videos even more clickable with some thumbnail improvements. I've helped several creators increase their CTR by 20-30%.

Would you be open to a quick collaboration? I can create a few sample thumbnails for your recent videos to show you what I mean.

Here's a quick video about my approach: {self.video_link if self.video_link else self.portfolio_link}

My work : {self.portfolio_link}
Let me know if this sounds interesting!

Best regards,
{self.your_name}
📱 +91 8115529832
"""
        }

        return [template1, template2, template3]

    def send_single_email(self, to_email, subject, body, use_html=False):
        """Send a single email with anti-spam measures"""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.your_name} <{self.gmail_user}>"  # Personal sender name
            msg['To'] = to_email
            msg['Reply-To'] = self.gmail_user

            if use_html:
                html_part = MIMEText(body, 'html')
                msg.attach(html_part)
            else:
                # Plain text for better deliverability
                text_part = MIMEText(body, 'plain')
                msg.attach(text_part)

            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.login(self.gmail_user, self.gmail_password)
            server.send_message(msg)
            server.quit()

            return True, "Sent successfully"

        except Exception as e:
            return False, str(e)

    def load_email_list(self):
        """Load email list from CSV"""
        if not os.path.exists(self.email_list_file):
            print(f"❌ Email list file '{self.email_list_file}' not found!")
            return None

        try:
            df = pd.read_csv(self.email_list_file)
            print(f"✅ Loaded {len(df)} email addresses")
            return df
        except Exception as e:
            print(f"❌ Error loading email list: {e}")
            return None

    def send_bulk_emails(self):
        """Send personal emails to avoid promotional tab"""
        if not self.load_credentials():
            self.setup_gmail_credentials()

        df = self.load_email_list()
        if df is None:
            return

        unsent_emails = df[df['status'] == 'Not Sent']
        if len(unsent_emails) == 0:
            print("✅ No unsent emails found!")
            return

        print(f"📧 Found {len(unsent_emails)} unsent emails")
        print("Using personal email approach to avoid promotional tab...")

        # Get email templates
        templates = self.get_personal_email_templates()

        sent_count = 0
        failed_count = 0

        for index, row in unsent_emails.iterrows():
            email_address = row['email']

            # Rotate between templates to avoid pattern detection
            template = templates[sent_count % len(templates)]

            print(f"\nSending to: {email_address}")
            print(f"Using template: {template['subject']}")

            # Send email (plain text for better deliverability)
            success, message = self.send_single_email(
                email_address, 
                template['subject'], 
                template['body'],
                use_html=False  # Plain text reduces promotional classification
            )

            if success:
                print(f"✅ Sent successfully")
                df.at[index, 'status'] = 'Sent'
                df.at[index, 'last_sent'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                sent_count += 1
            else:
                print(f"❌ Failed: {message}")
                df.at[index, 'status'] = 'Failed'
                failed_count += 1

            # Save progress
            df.to_csv(self.email_list_file, index=False)

            # Longer delay for better sender reputation
            if index < len(unsent_emails) - 1:
                print(f"⏳ Waiting {self.delay_between_emails} seconds...")
                time.sleep(self.delay_between_emails)

        print("\n" + "=" * 50)
        print("📊 FINAL SUMMARY")
        print("=" * 50)
        print(f"✅ Emails sent successfully: {sent_count}")
        print(f"❌ Emails failed: {failed_count}")
        print(f"📁 Email list updated: {self.email_list_file}")
        print("\n🎯 ANTI-SPAM MEASURES USED:")
        print("- Personal sender name")
        print("- Plain text format")
        print("- Conversational tone")
        print("- Template rotation")
        print("- Extended delays between sends")
        print("=" * 50)

def main():
    automation = PersonalEmailAutomation()

    print("🎯 PERSONAL EMAIL AUTOMATION (Anti-Promotional)")
    print("=" * 50)
    print("This system uses personal, conversational emails")
    print("to avoid promotional tab and spam filters.")
    print("=" * 50)

    automation.send_bulk_emails()

if __name__ == "__main__":
    main()
