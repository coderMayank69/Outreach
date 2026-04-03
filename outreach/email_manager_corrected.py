import pandas as pd
import os
import re

class EmailListManager:
    def __init__(self):
        self.csv_file = "email_list.csv"

    def create_new_list(self):
        """Create a new email list CSV"""
        df = pd.DataFrame({
            'email': [],
            'status': [],
            'last_sent': [],
            'follow_up_count': []
        })
        df.to_csv(self.csv_file, index=False)
        print(f"✅ Created new email list: {self.csv_file}")

    def add_emails_from_text(self, text_input):
        """Add emails from text input"""
        # Extract emails using regex
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        found_emails = re.findall(email_pattern, text_input.lower())

        # Remove duplicates
        found_emails = list(set(found_emails))

        if not found_emails:
            print("❌ No valid email addresses found!")
            return

        # Load existing CSV or create new one
        if os.path.exists(self.csv_file):
            df = pd.read_csv(self.csv_file)
            existing_emails = set(df['email'].str.lower())
        else:
            df = pd.DataFrame(columns=['email', 'status', 'last_sent', 'follow_up_count'])
            existing_emails = set()

        # Add new emails
        new_emails = []
        duplicate_count = 0

        for email in found_emails:
            if email not in existing_emails:
                new_emails.append({
                    'email': email,
                    'status': 'Not Sent',
                    'last_sent': '',
                    'follow_up_count': 0
                })
            else:
                duplicate_count += 1

        # Add to DataFrame
        if new_emails:
            new_df = pd.DataFrame(new_emails)
            df = pd.concat([df, new_df], ignore_index=True)
            df.to_csv(self.csv_file, index=False)
            print(f"✅ Added {len(new_emails)} new email addresses")

            if duplicate_count > 0:
                print(f"⚠️ Skipped {duplicate_count} duplicate addresses")
            print(f"📁 Total emails in list: {len(df)}")
        else:
            print("ℹ️ All emails already exist in the list")

    def add_emails_from_file(self, file_path):
        """Add emails from a text file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.add_emails_from_text(content)
        except FileNotFoundError:
            print(f"❌ File not found: {file_path}")
        except Exception as e:
            print(f"❌ Error reading file: {e}")

    def show_list(self):
        """Show current email list"""
        if not os.path.exists(self.csv_file):
            print("❌ Email list not found. Create one first.")
            return

        df = pd.read_csv(self.csv_file)
        print(f"📧 EMAIL LIST ({len(df)} addresses)")
        print("=" * 60)

        # Show statistics
        if not df.empty:
            status_counts = df['status'].value_counts()
            for status, count in status_counts.items():
                print(f"{status}: {count}")

        print("\n" + "=" * 60)
        print("Recent entries:")
        print(df.tail(10).to_string(index=False))

    def manual_add(self):
        """Manually add emails one by one"""
        print("Manual email entry (press Enter with empty email to stop):")
        emails_added = 0

        while True:
            email = input("Enter email address: ").strip().lower()
            if not email:
                break

            # Validate email
            email_pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'
            if not re.match(email_pattern, email):
                print("❌ Invalid email format!")
                continue

            self.add_emails_from_text(email)
            emails_added += 1

        if emails_added > 0:
            print(f"✅ Finished adding {emails_added} emails")

def main():
    manager = EmailListManager()

    while True:
        print("\n🗂️ EMAIL LIST MANAGER")
        print("=" * 30)
        print("1. Add emails from text/notes")
        print("2. Add emails from text file")
        print("3. Add emails manually")
        print("4. Show current email list")
        print("5. Create new email list")
        print("6. Exit")

        choice = input("\nEnter choice (1-6): ").strip()

        if choice == '1':
            print("\nPaste your text with email addresses (press Enter twice to finish):")
            lines = []
            empty_lines = 0

            while True:
                try:
                    line = input()
                    if line.strip() == '':
                        empty_lines += 1
                        if empty_lines >= 2:
                            break
                    else:
                        empty_lines = 0
                        lines.append(line)
                except EOFError:
                    break

            if lines:
                text_input = '\n'.join(lines)
                manager.add_emails_from_text(text_input)

        elif choice == '2':
            file_path = input("Enter text file path: ").strip()
            manager.add_emails_from_file(file_path)

        elif choice == '3':
            manager.manual_add()

        elif choice == '4':
            manager.show_list()

        elif choice == '5':
            confirm = input("This will create a new email list. Continue? (y/n): ")
            if confirm.lower() == 'y':
                manager.create_new_list()

        elif choice == '6':
            print("Goodbye!")
            break

        else:
            print("Invalid choice!")

if __name__ == "__main__":
    main()
