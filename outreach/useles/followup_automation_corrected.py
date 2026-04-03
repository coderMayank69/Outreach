import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time
from datetime import datetime, timedelta
import os
import imaplib
import email
import re

class FollowUpAutomation:
    def __init__(self):
        self.gmail_user = ""
        self.gmail_password = ""
        self.video_link = ""
        self.portfolio_link = ""
        self.email_list_file = "email_list.csv"
        self.delay_between_emails = 30  # seconds
        self.followup_delay_hours = 60  # 60 hours between follow-ups
        self.max_followups = 50  # Reduced for testing

    def load_credentials(self):
        """Load Gmail credentials from config file"""
        if os.path.exists('gmail_config.txt'):
            try:
                with open('gmail_config.txt', 'r') as f:
                    lines = f.readlines()
                for line in lines:
                    line = line.strip()
                    if line.startswith('EMAIL='):
                        self.gmail_user = line.split('=', 1)[1].strip()
                        print(f"Loaded EMAIL: {self.gmail_user}")
                    elif line.startswith('PASSWORD='):
                        self.gmail_password = line.split('=', 1)[1].strip()
                        print(f"Loaded PASSWORD: {'*' * len(self.gmail_password)}")
                    elif line.startswith('PORTFOLIO='):
                        self.portfolio_link = line.split('=', 1)[1].strip()
                    elif line.startswith('VIDEO='):
                        self.video_link = line.split('=', 1)[1].strip()

                if self.gmail_user and self.gmail_password:
                    return True
                else:
                    print("❌ Missing credentials in config file")
                    return False

            except Exception as e:
                print(f"❌ Error loading credentials: {e}")
                return False
        else:
            print("❌ gmail_config.txt file not found!")
            return False

    def check_for_replies(self, email_address, since_date):
        """
        Enhanced reply checking with multiple search methods
        Returns: (has_reply, has_bounce, details)
        """
        details = {"method_used": None, "search_results": [], "errors": []}

        try:
            # Connect to Gmail IMAP
            mail = imaplib.IMAP4_SSL('imap.gmail.com')
            mail.login(self.gmail_user, self.gmail_password)

            # Select both INBOX and Sent folder to catch all conversations
            mail.select('inbox')

            # Method 1: Search by sender email (most direct)
            has_reply = self._check_direct_replies(mail, email_address, since_date, details)

            # Method 2: Search by conversation/thread (more comprehensive)
            if not has_reply:
                has_reply = self._check_conversation_replies(mail, email_address, since_date, details)

            # Method 3: Check bounces
            has_bounce = self._check_bounces(mail, email_address, since_date, details)

            mail.close()
            mail.logout()

            print(f"  Reply check for {email_address}: Reply={has_reply}, Bounce={has_bounce}")
            if details["method_used"]:
                print(f"  Method used: {details['method_used']}")

            return has_reply, has_bounce

        except Exception as e:
            error_msg = f"Could not check replies for {email_address}: {e}"
            print(f"⚠️ {error_msg}")
            details["errors"].append(error_msg)
            return False, False

    def _check_direct_replies(self, mail, email_address, since_date, details):
        """Check for direct replies from the email address"""
        try:
            # Format date for IMAP (Gmail expects DD-Mon-YYYY format)
            search_date = since_date.strftime("%d-%b-%Y")

            # Search for emails FROM this address since the date
            search_criteria = f'(FROM "{email_address}" SINCE "{search_date}")'
            result, data = mail.search(None, search_criteria)

            if result == 'OK' and data[0]:
                message_ids = data[0].split()
                if len(message_ids) > 0:
                    details["method_used"] = "direct_reply_search"
                    details["search_results"].append(f"Found {len(message_ids)} messages from {email_address}")
                    print(f"  ✓ Found {len(message_ids)} direct replies from {email_address}")
                    return True

            return False

        except Exception as e:
            details["errors"].append(f"Direct reply check failed: {e}")
            return False

    def _check_conversation_replies(self, mail, email_address, since_date, details):
        """Check for replies in email conversations/threads"""
        try:
            # Search for any email containing our address (in To or CC) since the date
            search_date = since_date.strftime("%d-%b-%Y")

            # Multiple search approaches
            search_patterns = [
                f'(FROM "{email_address}" SINCE "{search_date}")',
                f'(TO "{self.gmail_user}" FROM "{email_address}" SINCE "{search_date}")',
                f'(HEADER "In-Reply-To" "" FROM "{email_address}" SINCE "{search_date}")'
            ]

            for pattern in search_patterns:
                try:
                    result, data = mail.search(None, pattern)
                    if result == 'OK' and data[0]:
                        message_ids = data[0].split()
                        if len(message_ids) > 0:
                            details["method_used"] = "conversation_search"
                            details["search_results"].append(f"Pattern '{pattern}' found {len(message_ids)} messages")
                            print(f"  ✓ Found {len(message_ids)} conversation replies using pattern")
                            return True
                except Exception as e:
                    details["errors"].append(f"Pattern '{pattern}' failed: {e}")
                    continue

            return False

        except Exception as e:
            details["errors"].append(f"Conversation check failed: {e}")
            return False

    def _check_bounces(self, mail, email_address, since_date, details):
        """Check for bounce-back messages"""
        try:
            search_date = since_date.strftime("%d-%b-%Y")

            # Common bounce sender patterns
            bounce_senders = [
                "Mail Delivery Subsystem",
                "postmaster",
                "mailer-daemon",
                "Mail Delivery System"
            ]

            for sender in bounce_senders:
                try:
                    search_criteria = f'(FROM "{sender}" SINCE "{search_date}")'
                    result, data = mail.search(None, search_criteria)

                    if result == 'OK' and data[0]:
                        message_ids = data[0].split()

                        # Check each bounce message for our target email
                        for msg_id in message_ids:
                            try:
                                result, msg_data = mail.fetch(msg_id, '(RFC822)')
                                if result == 'OK':
                                    email_body = msg_data[0][1]
                                    email_message = email.message_from_bytes(email_body)

                                    # Get subject and body
                                    subject = email_message.get('Subject', '').lower()
                                    body = self._extract_email_body(email_message).lower()

                                    # Check if our target email is mentioned
                                    if email_address.lower() in subject or email_address.lower() in body:
                                        details["method_used"] = "bounce_detection"
                                        details["search_results"].append(f"Bounce detected for {email_address}")
                                        print(f"  ⚠️ Bounce detected for {email_address}")
                                        return True

                            except Exception as e:
                                continue

                except Exception as e:
                    details["errors"].append(f"Bounce check for '{sender}' failed: {e}")
                    continue

            return False

        except Exception as e:
            details["errors"].append(f"Bounce check failed: {e}")
            return False

    def _extract_email_body(self, email_message):
        """Extract text body from email message"""
        body = ""
        try:
            if email_message.is_multipart():
                for part in email_message.walk():
                    if part.get_content_type() == "text/plain":
                        payload = part.get_payload(decode=True)
                        if payload:
                            body += payload.decode('utf-8', errors='ignore')
            else:
                payload = email_message.get_payload(decode=True)
                if payload:
                    body = payload.decode('utf-8', errors='ignore')
        except Exception:
            pass
        return body

    def get_followup_content(self, followup_number, is_final=False):
        """Generate follow-up email content based on sequence number"""
        if is_final:
            subject = "Final message - Thumbnail Design Services"
            body = f"""Hi there,

This is my final message regarding thumbnail design services for your channel.

I understand you might be busy or not interested at this time, and that's completely fine!

If you ever need professional thumbnails in the future, feel free to reach out:

📱 WhatsApp: +91 8115529832
✉️ Email: {self.gmail_user}

Portfolio: {self.portfolio_link}

Thank you for your time, and best of luck with your content!

Best regards,
Mayank
Thumbnail Designer

*You won't receive any more messages from me about this service.*"""

        elif followup_number == 1:
            subject = "Quick follow-up - Thumbnail Design"
            body = f"""Hi,

I hope you're doing well! I wanted to follow up on my previous message about thumbnail design services.

I know you're probably busy creating amazing content, but I genuinely believe I can help boost your video performance with eye-catching thumbnails.

Quick reminder of what I offer:
• Professional thumbnail designs that increase CTR
• Quick 24-48 hour turnaround  
• Unlimited revisions until you're happy

Would you be interested in seeing a free sample thumbnail for one of your recent videos?

Here's my work: {self.portfolio_link}
📱 WhatsApp: +91 8115529832

Best,
Mayank"""

        else:
            subject = "Free thumbnail sample offer"
            body = f"""Hello,

I've been following your content and really impressed with your work!

I'd love to create a FREE sample thumbnail for one of your recent videos - no strings attached. This way you can see the quality of my work firsthand.

Many creators have seen 20-40% increases in CTR after switching to professional thumbnails.

Interested in a free sample? Just reply with the video title you'd like me to work on.

Portfolio: {self.portfolio_link}
📱 WhatsApp: +91 8115529832

Thanks,
Mayank"""

        return subject, body

    def send_single_email(self, to_email, subject, body):
        """Send a single email"""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"Mayank <{self.gmail_user}>"
            msg['To'] = to_email
            msg['Reply-To'] = self.gmail_user

            # Use plain text to avoid promotional tab
            text_part = MIMEText(body, 'plain')
            msg.attach(text_part)

            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.login(self.gmail_user, self.gmail_password)
            server.send_message(msg)
            server.quit()

            return True, "Sent successfully"

        except Exception as e:
            return False, str(e)

    def process_followups(self):
        """Main follow-up processing function with enhanced reply detection"""
        print("🔄 Starting follow-up processing...")

        if not self.load_credentials():
            print("❌ Could not load credentials. Please check gmail_config.txt")
            return

        if not os.path.exists(self.email_list_file):
            print("❌ Email list not found!")
            return

        df = pd.read_csv(self.email_list_file)
        current_time = datetime.now()

        # Find candidates for follow-up
        followup_candidates = []

        print("🔍 Analyzing email list for follow-up candidates...")

        for index, row in df.iterrows():
            status = str(row['status']).strip()
            last_sent = row['last_sent']
            followup_count = int(row['follow_up_count']) if pd.notna(row['follow_up_count']) else 0
            email_address = str(row['email']).strip()

            print(f"  Checking {email_address}: status={status}, followups={followup_count}")

            # Skip if not eligible for follow-up
            if status in ['Replied', 'Bounced', 'Invalid Email', 'Follow-up Complete']:
                print(f"    → Skipped: {status}")
                continue

            if status not in ['Sent', 'Follow-up Sent']:
                print(f"    → Skipped: Status not eligible ({status})")
                continue

            if followup_count >= self.max_followups:
                print(f"    → Skipped: Max follow-ups reached ({followup_count})")
                continue

            if pd.isna(last_sent) or str(last_sent).strip() == '':
                print(f"    → Skipped: No last_sent date")
                continue

            try:
                last_sent_date = datetime.strptime(str(last_sent), "%Y-%m-%d %H:%M:%S")
                hours_since_last = (current_time - last_sent_date).total_seconds() / 3600

                print(f"    → Hours since last sent: {hours_since_last:.1f}")

                if hours_since_last >= self.followup_delay_hours:
                    followup_candidates.append({
                        'index': index,
                        'email': email_address,
                        'followup_count': followup_count,
                        'last_sent_date': last_sent_date
                    })
                    print(f"    → ✓ Added to follow-up candidates")
                else:
                    print(f"    → Skipped: Not enough time elapsed")

            except ValueError as e:
                print(f"    → Skipped: Date parsing error ({e})")
                continue

        if not followup_candidates:
            print("✅ No follow-ups needed at this time")
            return

        print(f"\n📧 Found {len(followup_candidates)} emails ready for follow-up")

        # Process each candidate
        sent_count = 0
        replied_count = 0
        bounced_count = 0

        for i, candidate in enumerate(followup_candidates):
            index = candidate['index']
            email_address = candidate['email']
            current_followup_count = candidate['followup_count']
            last_sent_date = candidate['last_sent_date']

            print(f"\n[{i+1}/{len(followup_candidates)}] Processing: {email_address}")

            # Check for replies first
            print("  🔍 Checking for replies...")
            has_reply, has_bounce = self.check_for_replies(email_address, last_sent_date)

            if has_reply:
                print(f"  ✅ Reply detected - marking as 'Replied'")
                df.at[index, 'status'] = 'Replied'
                df.to_csv(self.email_list_file, index=False)
                replied_count += 1
                continue

            if has_bounce:
                print(f"  🚫 Bounce detected - marking as 'Invalid Email'")
                df.at[index, 'status'] = 'Invalid Email'
                df.to_csv(self.email_list_file, index=False)
                bounced_count += 1
                continue

            # Send follow-up
            new_followup_count = current_followup_count + 1
            is_final = new_followup_count >= self.max_followups

            subject, body = self.get_followup_content(new_followup_count, is_final)

            print(f"  📤 Sending follow-up #{new_followup_count}...")
            success, message = self.send_single_email(email_address, subject, body)

            if success:
                print(f"  ✅ Follow-up #{new_followup_count} sent successfully")
                df.at[index, 'follow_up_count'] = new_followup_count
                df.at[index, 'last_sent'] = current_time.strftime("%Y-%m-%d %H:%M:%S")
                df.at[index, 'status'] = 'Follow-up Complete' if is_final else 'Follow-up Sent'

                if is_final:
                    print("  🏁 Final follow-up sent - sequence complete")

                sent_count += 1
            else:
                print(f"  ❌ Failed to send: {message}")
                df.at[index, 'status'] = 'Follow-up Failed'

            # Save progress after each email
            df.to_csv(self.email_list_file, index=False)

            # Add delay between emails (except for last one)
            if i < len(followup_candidates) - 1:
                print(f"  ⏳ Waiting {self.delay_between_emails} seconds...")
                time.sleep(self.delay_between_emails)

        # Final summary
        print("\n" + "=" * 60)
        print("📊 FOLLOW-UP PROCESSING COMPLETE")
        print("=" * 60)
        print(f"✅ Follow-ups sent: {sent_count}")
        print(f"💬 Replies detected: {replied_count}")
        print(f"🚫 Bounces detected: {bounced_count}")
        print(f"📁 Database updated: {self.email_list_file}")
        print("=" * 60)

    def show_followup_stats(self):
        """Show follow-up statistics"""
        if not os.path.exists(self.email_list_file):
            print("❌ Email list not found!")
            return

        df = pd.read_csv(self.email_list_file)
        current_time = datetime.now()

        print("📊 FOLLOW-UP STATISTICS")
        print("=" * 50)

        # Status distribution
        print("\n📋 Status Distribution:")
        if not df.empty:
            status_counts = df['status'].value_counts()
            for status, count in status_counts.items():
                print(f"  {status}: {count}")

        # Follow-up count distribution
        print("\n🔄 Follow-up Count Distribution:")
        if 'follow_up_count' in df.columns:
            followup_dist = df['follow_up_count'].value_counts().sort_index()
            for count, freq in followup_dist.items():
                print(f"  {int(count)} follow-ups: {freq} emails")

        # Emails ready for follow-up
        ready_count = 0
        for index, row in df.iterrows():
            status = str(row['status']).strip()
            followup_count = int(row['follow_up_count']) if pd.notna(row['follow_up_count']) else 0

            if status in ['Sent', 'Follow-up Sent'] and followup_count < self.max_followups:
                if pd.notna(row['last_sent']) and str(row['last_sent']).strip() != '':
                    try:
                        last_sent_date = datetime.strptime(str(row['last_sent']), "%Y-%m-%d %H:%M:%S")
                        hours_since_last = (current_time - last_sent_date).total_seconds() / 3600
                        if hours_since_last >= self.followup_delay_hours:
                            ready_count += 1
                    except:
                        continue

        print(f"\n⏰ Ready for follow-up now: {ready_count}")
        print(f"⚙️ Follow-up delay: {self.followup_delay_hours} hours")
        print(f"🔄 Max follow-ups per email: {self.max_followups}")
        print("=" * 50)


def main():
    automation = FollowUpAutomation()

    print("🔄 ENHANCED FOLLOW-UP AUTOMATION SYSTEM")
    print("=" * 50)
    print("This system includes improved reply detection to prevent")
    print("sending follow-ups to emails that have already replied.")
    print("=" * 50)
    print("1. Process follow-ups (send follow-up emails)")
    print("2. Show follow-up statistics")
    print("3. Test reply detection for specific email")
    print("4. Exit")

    choice = input("\nEnter choice (1-4): ").strip()

    if choice == '1':
        print("\n🚀 Starting follow-up process...")
        automation.process_followups()

    elif choice == '2':
        automation.show_followup_stats()

    elif choice == '3':
        if automation.load_credentials():
            email_to_test = input("Enter email address to test reply detection: ").strip()
            test_date = datetime.now() - timedelta(days=7)  # Check last 7 days
            print(f"\nTesting reply detection for {email_to_test} since {test_date.strftime('%Y-%m-%d')}...")
            has_reply, has_bounce = automation.check_for_replies(email_to_test, test_date)
            print(f"\nResults: Has Reply = {has_reply}, Has Bounce = {has_bounce}")
        else:
            print("❌ Could not load credentials for testing")

    else:
        print("Goodbye!")


if __name__ == "__main__":
    main()
