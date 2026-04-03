import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time
from datetime import datetime
import os


class FollowUpAutomation:
    def __init__(self):
        self.gmail_user = ""
        self.gmail_password = ""
        self.video_link = ""
        self.portfolio_link = ""
        self.email_list_file = "email_list.csv"
        self.delay_between_emails = 30  # seconds
        self.followup_delay_hours = 60  # 60 hours between follow-ups
        self.max_followups = 50

    def load_credentials(self):
        if os.path.exists('gmail_config.txt'):
            try:
                with open('gmail_config.txt', 'r') as f:
                    lines = f.readlines()
                    for line in lines:
                        print(f"Reading line: {line.strip()}")
                        if line.startswith('EMAIL='):
                            self.gmail_user = line.split('=')[1].strip()
                            print(f"Loaded EMAIL: {self.gmail_user}")
                        elif line.startswith('PASSWORD='):
                            self.gmail_password = line.split('=')[1].strip()
                            print(f"Loaded PASSWORD: {'*' * len(self.gmail_password)}")
                return True
            except Exception as e:
                print(f"Error loading credentials: {e}")
        else:
            print("gmail_config.txt file not found!")
        return False

    def check_for_replies(self, email_address, since_date):
        """Check if there are any replies from this email address OR bounce-back messages"""
        try:
            import imaplib
            import email

            mail = imaplib.IMAP4_SSL('imap.gmail.com')
            mail.login(self.gmail_user, self.gmail_password)
            mail.select('inbox')

            search_criteria = f'(FROM "{email_address}" SINCE "{since_date.strftime("%d-%b-%Y")}")'
            result, data = mail.search(None, search_criteria)
            has_reply = len(data[0].split()) > 0

            bounce_search_criteria = f'(FROM "Mail Delivery Subsystem" SINCE "{since_date.strftime("%d-%b-%Y")}")'
            bounce_result, bounce_data = mail.search(None, bounce_search_criteria)
            has_bounce = False

            if len(bounce_data[0].split()) > 0:
                bounce_message_ids = bounce_data[0].split()

                for msg_id in bounce_message_ids:
                    try:
                        result, msg_data = mail.fetch(msg_id, '(RFC822)')
                        email_body = msg_data[0][1]
                        email_message = email.message_from_bytes(email_body)

                        subject = email_message.get('Subject', '')

                        body = ""
                        if email_message.is_multipart():
                            for part in email_message.walk():
                                if part.get_content_type() == "text/plain":
                                    body += part.get_payload(decode=True).decode('utf-8', errors='ignore')
                        else:
                            body = email_message.get_payload(decode=True).decode('utf-8', errors='ignore')

                        if email_address.lower() in subject.lower() or email_address.lower() in body.lower():
                            has_bounce = True
                            break

                    except Exception:
                        continue

            mail.close()
            mail.logout()

            return has_reply, has_bounce

        except Exception as e:
            print(f"⚠️  Could not check replies/bounces for {email_address}: {e}")
            return False, False

    def get_followup_content(self, followup_number, is_final=False):
        """Generate follow-up email content based on sequence number"""
        portfolio_html = """
        <p>🔗 <strong>My Portfolio:</strong> 
        <a href="https://www.behance.net/gallery/215773425/Portfolio" target="_blank">
        View My Work on Behance
        </a></p>
        """

        if is_final:
            subject = "Last message - Thumbnail Design Services"
            body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                <p>Hi there,</p>
                <p>This is my final message regarding thumbnail design services for your channel.</p>
                <p>I understand you might be busy or not interested at this time, and that's completely fine!</p>
                <p>If you ever need professional thumbnails in the future, feel free to reach out:</p>
                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; text-align: center;">
                    <p><strong>📱 WhatsApp:</strong> +91 8115529832</p>
                    <p><strong>✉️ Email:</strong> {self.gmail_user}</p>
                </div>
                {portfolio_html}
                <p>Thank you for your time, and best of luck with your content!</p>
                <p>Best regards,<br>
                Mayank<br>
                Thumbnail Designer</p>
                <p style="font-size: 12px; color: #666; margin-top: 30px;">
                    <em>You won't receive any more messages from me about this service.</em>
                </p>
            </body>
            </html>
            """
            return subject, body
        elif followup_number <= 3:
            subject = "Quick follow-up - Thumbnail Design"
            body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                <p>Hi,</p>
                <p>I hope you're doing well! I wanted to follow up on my previous message about thumbnail design services.</p>
                <p>I know you're probably busy creating amazing content, but I genuinely believe I can help boost your video performance with eye-catching thumbnails.</p>
                <p><strong>Quick reminder of what I offer:</strong></p>
                <ul>
                    <li>Professional thumbnail designs that increase CTR</li>
                    <li>Quick 24-48 hour turnaround</li>
                    <li>Unlimited revisions until you're happy</li>
                </ul>
                <p>Would you be interested in seeing a free sample thumbnail for one of your recent videos?</p>
                Here's a quick video about my approach: {self.video_link if self.video_link else self.portfolio_link}

                <p>📱 <strong>WhatsApp:</strong> +91 8115529832</p>
                {portfolio_html}
                <p>Best,<br>
                Mayank</p>
            </body>
            </html>
            """
            return subject, body
        else:
            subject = "Free thumbnail sample offer"
            body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                <p>Hello,</p>
                <p>I've been following your content and really impressed with your work!</p>
                <p>I'd love to create a <strong>FREE sample thumbnail</strong> for one of your recent videos - no strings attached. This way you can see the quality of my work firsthand.</p>
                <p>Many creators have seen 20-40% increases in CTR after switching to professional thumbnails.</p>
                <p>Interested in a free sample? Just reply with the video title you'd like me to work on.</p>
                <p>📱 <strong>WhatsApp:</strong> +91 8115529832</p>
                Here's a quick video about my approach: {self.video_link if self.video_link else self.portfolio_link}

                {portfolio_html}
                <p>Thanks,<br>
                Mayank</p>
            </body>
            </html>
            """
            return subject, body

    def send_single_email(self, to_email, subject, body):
        """Send a single email"""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.gmail_user
            msg['To'] = to_email

            html_part = MIMEText(body, 'html')
            msg.attach(html_part)

            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.login(self.gmail_user, self.gmail_password)
            server.send_message(msg)
            server.quit()
            return True, "Sent successfully"
        except Exception as e:
            return False, str(e)

    def process_followups(self):
        """Main follow-up processing function with bounce detection"""
        if not self.load_credentials():
            return

        if not os.path.exists(self.email_list_file):
            print("❌ Email list not found!")
            return

        df = pd.read_csv(self.email_list_file)
        current_time = datetime.now()
        followup_candidates = []

        for index, row in df.iterrows():
            status = row['status']
            last_sent = row['last_sent']
            followup_count = row['follow_up_count']
            email_address = row['email']

            if (status not in ['Sent', 'Follow-up Sent'] or
                status in ['Replied', 'Bounced', 'Invalid Email'] or
                followup_count >= self.max_followups):
                continue

            if pd.isna(last_sent) or last_sent == '':
                continue

            try:
                last_sent_date = datetime.strptime(str(last_sent), "%Y-%m-%d %H:%M:%S")
                hours_since_last = (current_time - last_sent_date).total_seconds() / 3600

                if hours_since_last >= self.followup_delay_hours:
                    followup_candidates.append({
                        'index': index,
                        'email': email_address,
                        'followup_count': followup_count,
                        'last_sent_date': last_sent_date
                    })

            except ValueError:
                continue

        if not followup_candidates:
            print("✅ No follow-ups needed at this time")
            return

        print(f"📧 Found {len(followup_candidates)} emails ready for follow-up")
        sent_count = 0
        replied_count = 0
        bounced_count = 0

        for candidate in followup_candidates:
            index = candidate['index']
            email_address = candidate['email']
            current_followup_count = candidate['followup_count']
            last_sent_date = candidate['last_sent_date']

            print(f"\nProcessing: {email_address}")

            has_reply, has_bounce = self.check_for_replies(email_address, last_sent_date)

            if has_reply:
                print(f"✅ Reply received - marking as 'Replied'")
                df.at[index, 'status'] = 'Replied'
                df.to_csv(self.email_list_file, index=False)
                replied_count += 1
                continue

            if has_bounce:
                print(f"🚫 Bounce-back detected - marking as 'Invalid Email'")
                df.at[index, 'status'] = 'Invalid Email'
                df.to_csv(self.email_list_file, index=False)
                bounced_count += 1
                continue

            is_final = (current_followup_count + 1) >= self.max_followups
            subject, body = self.get_followup_content(current_followup_count + 1, is_final)
            success, message = self.send_single_email(email_address, subject, body)

            if success:
                new_followup_count = current_followup_count + 1
                print(f"✅ Follow-up #{new_followup_count} sent")
                df.at[index, 'follow_up_count'] = new_followup_count
                df.at[index, 'last_sent'] = current_time.strftime("%Y-%m-%d %H:%M:%S")
                df.at[index, 'status'] = 'Follow-up Sent'
                if is_final:
                    df.at[index, 'status'] = 'Follow-up Complete'
                    print("🏁 Final follow-up sent - sequence complete")
                sent_count += 1
            else:
                print(f"❌ Failed: {message}")
                df.at[index, 'status'] = 'Follow-up Failed'

            df.to_csv(self.email_list_file, index=False)
            if candidate != followup_candidates[-1]:
                print(f"⏳ Waiting {self.delay_between_emails} seconds...")
                time.sleep(self.delay_between_emails)

        print("\n" + "=" * 50)
        print("📊 FOLLOW-UP SUMMARY")
        print("=" * 50)
        print(f"✅ Follow-ups sent: {sent_count}")
        print(f"💬 Replies detected: {replied_count}")
        print(f"🚫 Invalid emails detected: {bounced_count}")
        print(f"📁 Database updated: {self.email_list_file}")
        print("=" * 50)

    def show_followup_stats(self):
        """Show follow-up statistics"""
        if not os.path.exists(self.email_list_file):
            print("❌ Email list not found!")
            return

        df = pd.read_csv(self.email_list_file)

        print("📊 FOLLOW-UP STATISTICS")
        print("=" * 40)

        status_counts = df['status'].value_counts()
        for status, count in status_counts.items():
            print(f"{status}: {count}")

        print()

        followup_dist = df['follow_up_count'].value_counts().sort_index()
        print("Follow-up Distribution:")
        for count, freq in followup_dist.items():
            print(f"  {count} follow-ups: {freq} emails")

        current_time = datetime.now()
        ready_for_followup = 0

        for index, row in df.iterrows():
            if row['status'] in ['Sent', 'Follow-up Sent'] and row['follow_up_count'] < self.max_followups:
                try:
                    if pd.notna(row['last_sent']) and row['last_sent'] != '':
                        last_sent_date = datetime.strptime(str(row['last_sent']), "%Y-%m-%d %H:%M:%S")
                        hours_since_last = (current_time - last_sent_date).total_seconds() / 3600
                        if hours_since_last >= self.followup_delay_hours:
                            ready_for_followup += 1
                except:
                    continue

        print(f"\n⏰ Ready for follow-up now: {ready_for_followup}")
        print("=" * 40)


def main():
    automation = FollowUpAutomation()

    print("🔄 FOLLOW-UP AUTOMATION SYSTEM")
    print("=" * 40)
    print("1. Process follow-ups (send follow-up emails)")
    print("2. Show follow-up statistics")
    print("3. Exit")

    choice = input("\nEnter choice (1-3): ").strip()
    if choice == '1':
        print("\n🚀 Starting follow-up process...")
        automation.process_followups()
    elif choice == '2':
        automation.show_followup_stats()
    else:
        print("Goodbye!")


if __name__ == "__main__":
    main()
