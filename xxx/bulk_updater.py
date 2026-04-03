import pandas as pd
import os
from datetime import datetime

class BulkEmailUpdater:
    def __init__(self):
        self.csv_file = "email_list.csv"

    def bulk_import_from_text_file(self, file_path):
        """Import emails from any text file (notes, etc.)"""
        print(f"📁 Importing from: {file_path}")

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Extract all emails using regex
            import re
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            found_emails = re.findall(email_pattern, content.lower())
            found_emails = list(set(found_emails))  # Remove duplicates

            print(f"📧 Found {len(found_emails)} unique emails in file")

            # Load existing data
            if os.path.exists(self.csv_file):
                df = pd.read_csv(self.csv_file)
                existing = set(df['email'].str.lower())
            else:
                df = pd.DataFrame(columns=['email', 'status', 'last_sent', 'follow_up_count'])
                existing = set()

            # Add only new emails
            new_emails = []
            for email in found_emails:
                if email not in existing:
                    new_emails.append({
                        'email': email,
                        'status': 'Not Sent',
                        'last_sent': '',
                        'follow_up_count': 0
                    })

            if new_emails:
                new_df = pd.DataFrame(new_emails)
                df = pd.concat([df, new_df], ignore_index=True)
                df.to_csv(self.csv_file, index=False)

                print(f"✅ Added {len(new_emails)} NEW emails")
                print(f"⚠️  Skipped {len(found_emails) - len(new_emails)} existing emails")
                print(f"📊 Total emails in database: {len(df)}")
            else:
                print("ℹ️  No new emails to add (all already exist)")

        except Exception as e:
            print(f"❌ Error: {e}")

    def reset_failed_emails(self):
        """Reset failed emails to 'Not Sent' for retry"""
        if not os.path.exists(self.csv_file):
            print("❌ No email list found")
            return

        df = pd.read_csv(self.csv_file)
        failed_count = len(df[df['status'] == 'Failed'])

        if failed_count == 0:
            print("✅ No failed emails to reset")
            return

        # Reset failed to "Not Sent"
        df.loc[df['status'] == 'Failed', 'status'] = 'Not Sent'
        df.loc[df['status'] == 'Not Sent', 'last_sent'] = ''
        df.to_csv(self.csv_file, index=False)

        print(f"✅ Reset {failed_count} failed emails to 'Not Sent'")
        print("These will be retried in the next sending batch")

    def export_email_list(self, status_filter=None):
        """Export emails by status"""
        if not os.path.exists(self.csv_file):
            print("❌ No email list found")
            return

        df = pd.read_csv(self.csv_file)

        if status_filter:
            filtered_df = df[df['status'] == status_filter]
            filename = f"emails_{status_filter.lower().replace(' ', '_')}.txt"
        else:
            filtered_df = df
            filename = "all_emails.txt"

        # Export just email addresses
        with open(filename, 'w') as f:
            for email in filtered_df['email']:
                f.write(f"{email}\n")

        print(f"✅ Exported {len(filtered_df)} emails to: {filename}")

def main():
    updater = BulkEmailUpdater()

    print("🔄 BULK EMAIL UPDATER")
    print("=" * 30)
    print("1. Import from text file (notes, etc.)")
    print("2. Reset failed emails for retry")
    print("3. Export emails by status")
    print("4. Exit")

    choice = input("\nEnter choice (1-4): ").strip()

    if choice == '1':
        file_path = input("Enter path to your text file: ").strip()
        updater.bulk_import_from_text_file(file_path)

    elif choice == '2':
        updater.reset_failed_emails()

    elif choice == '3':
        print("\nExport options:")
        print("1. All emails")
        print("2. Not Sent only")
        print("3. Sent only") 
        print("4. Failed only")

        export_choice = input("Choose (1-4): ").strip()
        filters = {
            '1': None,
            '2': 'Not Sent',
            '3': 'Sent', 
            '4': 'Failed'
        }
        updater.export_email_list(filters.get(export_choice))

    elif choice == '4':
        print("Goodbye!")

if __name__ == "__main__":
    main()
