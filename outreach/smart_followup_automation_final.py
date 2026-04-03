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
import json

class SmartMultiSenderFollowUpAutomation:
    def __init__(self):
        # Multiple sender accounts configuration
        self.sender_accounts = [
            {
                "email": "creativemayank96325@gmail.com",
                "password": "lelp kuqc phvu xbgr",
                "name": "Mayank",
                "index_range": (0, 519),  # emails 0-518 (first 519 emails)
                "daily_limit": 500,  # Gmail daily sending limit
                "priority": 1  # Higher priority means it's tried first
            },
            {
                "email": "mayanksingh96325@gmail.com", 
                "password": "mnja ascg uksa jrgv",
                "name": "Mayank",
                "index_range": (519, float('inf')),  # emails 519+ (rest)
                "daily_limit": 500,  # Gmail daily sending limit
                "priority": 2
            }
        ]

        self.video_link = ""
        self.portfolio_link = ""
        self.email_list_file = "email_list.csv"
        self.daily_usage_file = "daily_email_usage.json"
        self.delay_between_emails = 20  # seconds
        self.followup_delay_hours = 60  # 60 hours between follow-ups
        self.max_followups = 50  # Reduced for testing

    def get_sender_by_index(self, email_index):
        """Get the appropriate sender account based on email index"""
        for sender in self.sender_accounts:
            start, end = sender["index_range"]
            if start <= email_index < end:
                return sender

        # Default to last sender if index is beyond all ranges
        return self.sender_accounts[-1]

    def get_best_available_sender(self, preferred_sender=None):
        """
        Get the best available sender account that still has quota.
        If preferred_sender has quota, use it. Otherwise, find next available.
        """
        # Sort senders by priority
        sorted_senders = sorted(self.sender_accounts, key=lambda x: x["priority"])

        # If preferred sender is specified and has quota, use it
        if preferred_sender and self.can_send_email(preferred_sender):
            return preferred_sender

        # Otherwise, find first available sender with quota
        for sender in sorted_senders:
            if self.can_send_email(sender):
                return sender

        # No sender has quota available
        return None

    def load_additional_config(self):
        """Load additional configuration like portfolio links"""
        if os.path.exists('gmail_config.txt'):
            try:
                with open('gmail_config.txt', 'r') as f:
                    lines = f.readlines()
                for line in lines:
                    line = line.strip()
                    if line.startswith('PORTFOLIO='):
                        self.portfolio_link = line.split('=', 1)[1].strip()
                    elif line.startswith('VIDEO='):
                        self.video_link = line.split('=', 1)[1].strip()
                print("✅ Loaded additional configuration")
            except Exception as e:
                print(f"⚠️ Could not load additional config: {e}")

    def load_daily_usage(self):
        """Load daily email usage tracking"""
        if os.path.exists(self.daily_usage_file):
            try:
                with open(self.daily_usage_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ Could not load daily usage file: {e}")

        # Return empty usage if file doesn't exist
        return {}

    def save_daily_usage(self, usage_data):
        """Save daily email usage tracking"""
        try:
            with open(self.daily_usage_file, 'w') as f:
                json.dump(usage_data, f, indent=2)
        except Exception as e:
            print(f"⚠️ Could not save daily usage: {e}")

    def get_today_usage(self, sender_email):
        """Get today's email usage for a specific sender"""
        usage_data = self.load_daily_usage()
        today = datetime.now().strftime("%Y-%m-%d")

        if sender_email not in usage_data:
            usage_data[sender_email] = {}

        if today not in usage_data[sender_email]:
            usage_data[sender_email][today] = 0

        return usage_data[sender_email][today], usage_data

    def increment_daily_usage(self, sender_email):
        """Increment daily usage counter for a sender"""
        current_usage, usage_data = self.get_today_usage(sender_email)
        today = datetime.now().strftime("%Y-%m-%d")

        usage_data[sender_email][today] = current_usage + 1
        self.save_daily_usage(usage_data)

        return usage_data[sender_email][today]

    def can_send_email(self, sender_account):
        """Check if sender can send more emails today"""
        current_usage, _ = self.get_today_usage(sender_account["email"])
        return current_usage < sender_account["daily_limit"]

    def get_remaining_quota(self, sender_account):
        """Get remaining email quota for sender today"""
        current_usage, _ = self.get_today_usage(sender_account["email"])
        return sender_account["daily_limit"] - current_usage

    def check_for_replies_all_accounts(self, email_address, since_date):
        """
        Check for replies in ALL sender account inboxes
        Returns: (has_reply, has_bounce, details)
        """
        details = {"accounts_checked": [], "method_used": None, "search_results": [], "errors": []}

        overall_has_reply = False
        overall_has_bounce = False

        # Check each sender account's inbox
        for i, sender in enumerate(self.sender_accounts):
            sender_email = sender["email"]
            sender_password = sender["password"]

            print(f"    Checking inbox of {sender_email}...")
            details["accounts_checked"].append(sender_email)

            try:
                # Connect to this sender's Gmail IMAP
                mail = imaplib.IMAP4_SSL('imap.gmail.com')
                mail.login(sender_email, sender_password)
                mail.select('inbox')

                # Check for direct replies in this account
                has_reply = self._check_direct_replies(mail, email_address, since_date, details, sender_email)
                if has_reply:
                    overall_has_reply = True
                    details["method_used"] = f"direct_reply_in_{sender_email}"

                # Check for conversation replies in this account  
                if not has_reply:
                    has_reply = self._check_conversation_replies(mail, email_address, since_date, details, sender_email)
                    if has_reply:
                        overall_has_reply = True
                        details["method_used"] = f"conversation_reply_in_{sender_email}"

                # Check for bounces in this account
                has_bounce = self._check_bounces(mail, email_address, since_date, details, sender_email)
                if has_bounce:
                    overall_has_bounce = True

                mail.close()
                mail.logout()

                if overall_has_reply:
                    print(f"    ✅ Reply found in {sender_email}")
                    break  # Found reply, no need to check other accounts

            except Exception as e:
                error_msg = f"Could not check {sender_email} for {email_address}: {e}"
                print(f"    ⚠️ {error_msg}")
                details["errors"].append(error_msg)
                continue

        print(f"  Multi-account reply check for {email_address}: Reply={overall_has_reply}, Bounce={overall_has_bounce}")

        return overall_has_reply, overall_has_bounce

    def _check_direct_replies(self, mail, email_address, since_date, details, sender_email):
        """Check for direct replies from the email address"""
        try:
            search_date = since_date.strftime("%d-%b-%Y")
            search_criteria = f'(FROM "{email_address}" SINCE "{search_date}")'
            result, data = mail.search(None, search_criteria)

            if result == 'OK' and data[0]:
                message_ids = data[0].split()
                if len(message_ids) > 0:
                    details["search_results"].append(f"Found {len(message_ids)} direct messages from {email_address} in {sender_email}")
                    print(f"      ✓ Found {len(message_ids)} direct replies from {email_address} in {sender_email}")
                    return True

            return False

        except Exception as e:
            details["errors"].append(f"Direct reply check failed in {sender_email}: {e}")
            return False

    def _check_conversation_replies(self, mail, email_address, since_date, details, sender_email):
        """Check for replies in email conversations/threads"""
        try:
            search_date = since_date.strftime("%d-%b-%Y")

            search_patterns = [
                f'(FROM "{email_address}" SINCE "{search_date}")',
                f'(TO "{sender_email}" FROM "{email_address}" SINCE "{search_date}")',
                f'(HEADER "In-Reply-To" "" FROM "{email_address}" SINCE "{search_date}")'
            ]

            for pattern in search_patterns:
                try:
                    result, data = mail.search(None, pattern)
                    if result == 'OK' and data[0]:
                        message_ids = data[0].split()
                        if len(message_ids) > 0:
                            details["search_results"].append(f"Pattern found {len(message_ids)} messages in {sender_email}")
                            print(f"      ✓ Found {len(message_ids)} conversation replies in {sender_email}")
                            return True
                except Exception as e:
                    details["errors"].append(f"Pattern '{pattern}' failed in {sender_email}: {e}")
                    continue

            return False

        except Exception as e:
            details["errors"].append(f"Conversation check failed in {sender_email}: {e}")
            return False

    def _check_bounces(self, mail, email_address, since_date, details, sender_email):
        """Check for bounce-back messages"""
        try:
            search_date = since_date.strftime("%d-%b-%Y")
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

                        for msg_id in message_ids:
                            try:
                                result, msg_data = mail.fetch(msg_id, '(RFC822)')
                                if result == 'OK':
                                    email_body = msg_data[0][1]
                                    email_message = email.message_from_bytes(email_body)

                                    subject = email_message.get('Subject', '').lower()
                                    body = self._extract_email_body(email_message).lower()

                                    if email_address.lower() in subject or email_address.lower() in body:
                                        details["search_results"].append(f"Bounce detected for {email_address} in {sender_email}")
                                        print(f"      ⚠️ Bounce detected for {email_address} in {sender_email}")
                                        return True

                            except Exception:
                                continue

                except Exception as e:
                    details["errors"].append(f"Bounce check for '{sender}' failed in {sender_email}: {e}")
                    continue

            return False

        except Exception as e:
            details["errors"].append(f"Bounce check failed in {sender_email}: {e}")
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

    def get_followup_content(self, followup_number, sender_email, is_final=False):
        """Generate follow-up email content based on sequence number"""
        if is_final:
            subject = "Final message - Thumbnail Design Services"
            body = f"""Hi there,

This is my final message regarding thumbnail design services for your channel.

I understand you might be busy or not interested at this time, and that's completely fine!

If you ever need professional thumbnails in the future, feel free to reach out:

📱 WhatsApp: +91 8115529832
✉️ Email: {sender_email}

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

    def send_single_email(self, to_email, subject, body, sender_account):
        """Send a single email using specified sender account with quota checking"""
        # Check daily quota before sending
        if not self.can_send_email(sender_account):
            remaining = self.get_remaining_quota(sender_account)
            return False, f"Daily limit reached for {sender_account['email']} (remaining: {remaining})"

        try:
            sender_email = sender_account["email"]
            sender_password = sender_account["password"]
            sender_name = sender_account["name"]

            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{sender_name} <{sender_email}>"
            msg['To'] = to_email
            msg['Reply-To'] = sender_email

            # Use plain text to avoid promotional tab
            text_part = MIMEText(body, 'plain')
            msg.attach(text_part)

            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.login(sender_email, sender_password)
            server.send_message(msg)
            server.quit()

            # Increment daily usage counter
            new_count = self.increment_daily_usage(sender_email)
            remaining = sender_account["daily_limit"] - new_count

            return True, f"Sent successfully from {sender_email} (used: {new_count}/{sender_account['daily_limit']}, remaining: {remaining})"

        except Exception as e:
            return False, f"Failed from {sender_account['email']}: {str(e)}"

    def process_followups(self):
        """
        Main follow-up processing function with smart sender switching.
        When preferred sender reaches quota, automatically switch to available sender.
        """
        print("🔄 Starting smart multi-sender follow-up processing...")
        print("📧 Smart switching: When one account reaches 500 emails, automatically switch to another available account")

        # Load additional configuration
        self.load_additional_config()

        if not os.path.exists(self.email_list_file):
            print("❌ Email list not found!")
            return

        df = pd.read_csv(self.email_list_file)
        current_time = datetime.now()

        # Show current quota status
        print("\n📊 DAILY QUOTA STATUS:")
        print("=" * 50)
        total_available_quota = 0
        for sender in self.sender_accounts:
            current_usage, _ = self.get_today_usage(sender["email"])
            remaining = sender["daily_limit"] - current_usage
            total_available_quota += remaining
            status = "🟢 Available" if remaining > 0 else "🔴 Exhausted"
            print(f"{sender['email']}: {current_usage}/{sender['daily_limit']} used (remaining: {remaining}) {status}")
        print(f"\n📊 Total available quota across all accounts: {total_available_quota}")
        print("=" * 50)

        if total_available_quota == 0:
            print("❌ All sender accounts have reached their daily limits!")
            print("🕒 Please wait until tomorrow or reset quotas using admin option.")
            return

        # Find candidates for follow-up
        followup_candidates = []

        print("\n🔍 Analyzing email list for follow-up candidates...")

        for index, row in df.iterrows():
            status = str(row['status']).strip()
            last_sent = row['last_sent']
            followup_count = int(row['follow_up_count']) if pd.notna(row['follow_up_count']) else 0
            email_address = str(row['email']).strip()

            # Determine preferred sender based on index
            preferred_sender = self.get_sender_by_index(index)

            print(f"  Checking {email_address} [Index {index}]: status={status}, followups={followup_count}, preferred_sender={preferred_sender['email']}")

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
                        'last_sent_date': last_sent_date,
                        'preferred_sender': preferred_sender
                    })
                    print(f"    → ✓ Added to follow-up candidates (preferred: {preferred_sender['email']})")
                else:
                    print(f"    → Skipped: Not enough time elapsed")

            except ValueError as e:
                print(f"    → Skipped: Date parsing error ({e})")
                continue

        if not followup_candidates:
            print("✅ No follow-ups needed at this time")
            return

        print(f"\n📧 Found {len(followup_candidates)} emails ready for follow-up")

        # Process each candidate with smart sender switching
        sent_count = 0
        replied_count = 0
        bounced_count = 0
        quota_exhausted_count = 0
        sender_switches = 0

        for i, candidate in enumerate(followup_candidates):
            index = candidate['index']
            email_address = candidate['email']
            current_followup_count = candidate['followup_count']
            last_sent_date = candidate['last_sent_date']
            preferred_sender = candidate['preferred_sender']

            print(f"\n[{i+1}/{len(followup_candidates)}] Processing: {email_address}")
            print(f"  Index: {index}, Preferred sender: {preferred_sender['email']}")

            # Smart sender selection - use preferred if available, otherwise switch
            available_sender = self.get_best_available_sender(preferred_sender)

            if not available_sender:
                print(f"  ❌ No sender accounts have quota available - stopping process")
                quota_exhausted_count += 1
                break

            # Check if we had to switch from preferred sender
            if available_sender['email'] != preferred_sender['email']:
                print(f"  🔄 SMART SWITCH: {preferred_sender['email']} quota exhausted, switching to {available_sender['email']}")
                sender_switches += 1

            print(f"  📧 Using sender: {available_sender['email']}")

            # Check for replies in ALL accounts
            print("  🔍 Checking for replies in all sender accounts...")
            has_reply, has_bounce = self.check_for_replies_all_accounts(email_address, last_sent_date)

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

            # Send follow-up using the available sender
            new_followup_count = current_followup_count + 1
            is_final = new_followup_count >= self.max_followups

            subject, body = self.get_followup_content(new_followup_count, available_sender['email'], is_final)

            print(f"  📤 Sending follow-up #{new_followup_count} from {available_sender['email']}...")
            success, message = self.send_single_email(email_address, subject, body, available_sender)

            if success:
                print(f"  ✅ Follow-up #{new_followup_count} sent successfully")
                print(f"  📊 {message}")  # Shows quota usage
                df.at[index, 'follow_up_count'] = new_followup_count
                df.at[index, 'last_sent'] = current_time.strftime("%Y-%m-%d %H:%M:%S")
                df.at[index, 'status'] = 'Follow-up Complete' if is_final else 'Follow-up Sent'

                if is_final:
                    print("  🏁 Final follow-up sent - sequence complete")

                sent_count += 1
            else:
                print(f"  ❌ Failed to send: {message}")
                df.at[index, 'status'] = 'Follow-up Failed'
                if "Daily limit reached" in message:
                    quota_exhausted_count += 1

            # Save progress after each email
            df.to_csv(self.email_list_file, index=False)

            # Add delay between emails (except for last one)
            if i < len(followup_candidates) - 1:
                print(f"  ⏳ Waiting {self.delay_between_emails} seconds...")
                time.sleep(self.delay_between_emails)

        # Final summary
        print("\n" + "=" * 80)
        print("📊 SMART MULTI-SENDER FOLLOW-UP PROCESSING COMPLETE")
        print("=" * 80)
        print(f"✅ Follow-ups sent: {sent_count}")
        print(f"💬 Replies detected: {replied_count}")
        print(f"🚫 Bounces detected: {bounced_count}")
        print(f"⚠️ Quota exhausted stops: {quota_exhausted_count}")
        print(f"🔄 Smart sender switches: {sender_switches}")
        print(f"📁 Database updated: {self.email_list_file}")

        print("\n📊 FINAL QUOTA STATUS:")
        for sender in self.sender_accounts:
            current_usage, _ = self.get_today_usage(sender["email"])
            remaining = sender["daily_limit"] - current_usage
            percentage = (current_usage / sender["daily_limit"]) * 100
            print(f"  {sender['email']}: {current_usage}/{sender['daily_limit']} ({percentage:.1f}%) - Remaining: {remaining}")

        print("\n🎯 SMART SWITCHING BENEFITS:")
        print("  - Automatically continues sending when preferred account reaches limit")
        print("  - Maximizes daily email throughput across all accounts")
        print("  - No manual intervention required when quotas are reached")
        print("  - Maintains email sending continuity")
        print("=" * 80)

    def show_followup_stats(self):
        """Show follow-up statistics with sender breakdown and quota info"""
        if not os.path.exists(self.email_list_file):
            print("❌ Email list not found!")
            return

        df = pd.read_csv(self.email_list_file)
        current_time = datetime.now()

        print("📊 SMART MULTI-SENDER FOLLOW-UP STATISTICS")
        print("=" * 70)

        # Daily quota status
        print("\n📈 DAILY QUOTA STATUS:")
        total_used = 0
        total_limit = 0
        total_remaining = 0

        for sender in self.sender_accounts:
            current_usage, _ = self.get_today_usage(sender["email"])
            remaining = sender["daily_limit"] - current_usage
            percentage = (current_usage / sender["daily_limit"]) * 100
            status = "🟢 Available" if remaining > 0 else "🔴 Exhausted"

            total_used += current_usage
            total_limit += sender["daily_limit"]
            total_remaining += remaining

            print(f"  {sender['email']}: {current_usage}/{sender['daily_limit']} ({percentage:.1f}%) - Remaining: {remaining} {status}")

        total_percentage = (total_used / total_limit) * 100
        print(f"\n  📊 TOTAL: {total_used}/{total_limit} ({total_percentage:.1f}%) - Remaining: {total_remaining}")

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

        # Sender distribution
        print("\n📧 Sender Account Distribution:")
        for sender in self.sender_accounts:
            start, end = sender["index_range"]
            if end == float('inf'):
                end = len(df)
            count_in_range = min(end, len(df)) - start
            count_in_range = max(0, count_in_range)
            print(f"  {sender['email']}: {count_in_range} emails (indexes {start}-{min(end-1, len(df)-1)})")

        # Emails ready for follow-up (considering quotas and smart switching)
        ready_count = 0
        ready_with_quota = 0

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

                            # Check if any sender has quota (smart switching)
                            preferred_sender = self.get_sender_by_index(index)
                            available_sender = self.get_best_available_sender(preferred_sender)
                            if available_sender:
                                ready_with_quota += 1
                    except:
                        continue

        print(f"\n⏰ Ready for follow-up now: {ready_count}")
        print(f"🔄 Ready with smart switching (quota available): {ready_with_quota}")
        print(f"⚙️ Follow-up delay: {self.followup_delay_hours} hours")
        print(f"🔄 Max follow-ups per email: {self.max_followups}")

        if ready_with_quota < ready_count:
            shortage = ready_count - ready_with_quota
            print(f"⚠️ {shortage} emails ready but no quota available across all accounts")

        print("=" * 70)

    def test_reply_detection(self):
        """Test reply detection for a specific email"""
        email_to_test = input("Enter email address to test reply detection: ").strip()
        if not email_to_test:
            print("❌ No email address provided")
            return

        test_date = datetime.now() - timedelta(days=7)  # Check last 7 days
        print(f"\nTesting reply detection for {email_to_test} since {test_date.strftime('%Y-%m-%d')}...")
        print("This will check ALL sender account inboxes...")

        has_reply, has_bounce = self.check_for_replies_all_accounts(email_to_test, test_date)

        print(f"\n📊 Results: Has Reply = {has_reply}, Has Bounce = {has_bounce}")

        if has_reply:
            print("✅ Reply was found - this email would be marked as 'Replied'")
        else:
            print("❌ No reply found - this email would receive follow-ups")

    def reset_daily_quota(self, sender_email=None):
        """Reset daily quota for specific sender or all senders"""
        if sender_email:
            # Reset specific sender
            usage_data = self.load_daily_usage()
            today = datetime.now().strftime("%Y-%m-%d")
            if sender_email in usage_data and today in usage_data[sender_email]:
                usage_data[sender_email][today] = 0
                self.save_daily_usage(usage_data)
                print(f"✅ Reset daily quota for {sender_email}")
            else:
                print(f"ℹ️ No usage found for {sender_email} today")
        else:
            # Reset all senders
            usage_data = {}
            self.save_daily_usage(usage_data)
            print("✅ Reset daily quota for all senders")

def main():
    automation = SmartMultiSenderFollowUpAutomation()

    print("🚀 SMART MULTI-SENDER FOLLOW-UP AUTOMATION")
    print("=" * 70)
    print("This system features intelligent sender switching:")
    print("📧 creativemayank96325@gmail.com: Emails 0-518 (first 519 emails) - 500/day limit")
    print("📧 mayanksingh96325@gmail.com: Emails 519+ (remaining emails) - 500/day limit")
    print("🔍 Reply detection checks ALL sender inboxes")
    print("🔄 SMART SWITCHING: Auto-switch to available account when quota reached")
    print("📊 Maximizes daily throughput across all accounts")
    print("=" * 70)
    print("1. Process follow-ups (with smart sender switching)")
    print("2. Show follow-up statistics")
    print("3. Test reply detection for specific email")
    print("4. Show sender account configuration & quota status")
    print("5. Reset daily quota (admin)")
    print("6. Exit")

    choice = input("\nEnter choice (1-6): ").strip()

    if choice == '1':
        print("\n🚀 Starting smart multi-sender follow-up process...")
        automation.process_followups()

    elif choice == '2':
        automation.show_followup_stats()

    elif choice == '3':
        automation.test_reply_detection()

    elif choice == '4':
        print("\n📧 SENDER ACCOUNT CONFIGURATION & QUOTA STATUS:")
        print("=" * 60)
        for i, sender in enumerate(automation.sender_accounts):
            start, end = sender["index_range"]
            end_str = "∞" if end == float('inf') else str(end-1)
            current_usage, _ = automation.get_today_usage(sender["email"])
            remaining = sender["daily_limit"] - current_usage
            percentage = (current_usage / sender["daily_limit"]) * 100
            status = "🟢 Available" if remaining > 0 else "🔴 Exhausted"

            print(f"{i+1}. {sender['email']}")
            print(f"   Name: {sender['name']}")
            print(f"   Email Range: Indexes {start}-{end_str}")
            print(f"   Daily Limit: {sender['daily_limit']} emails")
            print(f"   Today's Usage: {current_usage}/{sender['daily_limit']} ({percentage:.1f}%) {status}")
            print(f"   Remaining: {remaining}")
            print(f"   Priority: {sender['priority']}")
            print(f"   Password: {'*' * len(sender['password'])}")
            print()

    elif choice == '5':
        print("\n🔧 QUOTA RESET OPTIONS:")
        print("1. Reset specific sender")
        print("2. Reset all senders")
        print("3. Cancel")

        reset_choice = input("Enter choice (1-3): ").strip()
        if reset_choice == '1':
            print("\nAvailable senders:")
            for i, sender in enumerate(automation.sender_accounts):
                current_usage, _ = automation.get_today_usage(sender["email"])
                print(f"{i+1}. {sender['email']} (currently used: {current_usage})")

            try:
                sender_idx = int(input("Enter sender number: ")) - 1
                if 0 <= sender_idx < len(automation.sender_accounts):
                    sender_email = automation.sender_accounts[sender_idx]["email"]
                    automation.reset_daily_quota(sender_email)
                else:
                    print("❌ Invalid sender number")
            except ValueError:
                print("❌ Invalid input")

        elif reset_choice == '2':
            confirm = input("Reset quota for ALL senders? This will allow more emails to be sent today. (y/n): ")
            if confirm.lower() == 'y':
                automation.reset_daily_quota()
            else:
                print("❌ Cancelled")

    else:
        print("Goodbye!")

if __name__ == "__main__":
    main()
