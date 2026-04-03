
import pywhatkit as pwk
import random
import time
import datetime
from threading import Timer

class WhatsAppRomanticBot:
    def __init__(self, phone_number):
        self.phone_number = phone_number
        self.messages = []
        self.emojis = {
            'primary': '🥰',  # 75% of the time
            'secondary': ['😘', '😚', '😙', '❤️', '💕', '😍', '💖']  # 25% of the time
        }
        self.create_message_variations()

    def create_message_variations(self):
        """Create various message templates with spelling variations"""
        base_messages = [
            "I Love you",
            "I love you", 
            "Love you",
            
            "love you",
            "Love you",
            "love you",
            "I Love you bacha",
            "I love you bacha",
            "Love you Shalini",
            "love you Shalini",
            "I Love you Shalini",
            "I love you Shalini"
        ]

        # Add spelling variations (double letters, missing letters)
        spelling_variations = []
        for msg in base_messages:
            # Double letter variations
            spelling_variations.append(msg.replace('love', 'lovee'))
            spelling_variations.append(msg.replace('Love', 'Lovee'))
            spelling_variations.append(msg.replace('you', 'youu'))
            spelling_variations.append(msg.replace('bacha', 'bachaa'))
            spelling_variations.append(msg.replace('Shalini', 'Shalinii'))

            # Missing letter variations
            spelling_variations.append(msg.replace('love', 'lov'))
            spelling_variations.append(msg.replace('Love', 'Lov'))
            spelling_variations.append(msg.replace('Shalini', 'Shalin'))

        self.messages = base_messages + spelling_variations

    def get_emoji(self):
        """Get emoji based on 75% primary, 25% secondary distribution"""
        if random.random() < 0.75:
            return self.emojis['primary']
        else:
            return random.choice(self.emojis['secondary'])

    def get_emoji_count(self):
        """Randomly choose 0-3 emojis"""
        weights = [0.2, 0.6, 0.1, 0.1]  # 20% no emoji, 30% single, 30% double, 20% triple
        return random.choices([0, 1, 2, 3], weights=weights)[0]

    def create_message(self):
        
        """Create a complete message with text and emojis"""
        base_message = random.choice(self.messages)
        emoji_count = self.get_emoji_count()

        if emoji_count == 0:
            return base_message

        emojis = ""
        for _ in range(emoji_count):
            emojis += self.get_emoji()

        # Sometimes add emojis at the end, sometimes at the beginning
        if random.random() < 0.99 :  # 80% at the end
            return f"{base_message} {emojis}"
        else:  # 20% at the beginning
            return f"{emojis} {base_message}"

    def get_delay(self):
        """Get random delay between 5-20 seconds"""
        return random.randint(1, 5)

    def send_message_now(self, message):
        """Send message immediately using WhatsApp Web"""
        try:
            # Get current time + 1 minute (pywhatkit requirement)
            now = datetime.datetime.now()
            send_time = now + datetime.timedelta(minutes=1)
            hour = send_time.hour
            minute = send_time.minute

            print(f"Scheduling: {message} at {hour:02d}:{minute:02d}")
            pwk.sendwhatmsg(self.phone_number, message, hour, minute, 15, True, 2)
            print(f"✓ Sent: {message}")

        except Exception as e:
            print(f"Error sending message: {e}")

    def test_bot(self, num_messages=50):
        """Test the bot with a few messages"""
        print(f"Testing bot with {num_messages} messages to {self.phone_number}")
        print("Make sure WhatsApp Web is logged in on your browser!")
        print("Starting in 0 seconds...")
        time.sleep(0)

        for i in range(num_messages):
            message = self.create_message()
            delay = self.get_delay()

            print(f"\nMessage {i+1}/{num_messages}")
            self.send_message_now(message)

            if i < num_messages - 1:  # Don't wait after last message
                print(f"Waiting {delay} seconds...")
                time.sleep(delay)

        print("\n✓ Test completed!")

    def start_full_campaign(self):
        """Start the full 2 hours 47 minutes campaign"""
        print(f"Starting full romantic message campaign to {self.phone_number}")
        print("Duration: 2 hours 47 minutes")
        print("Make sure WhatsApp Web is logged in!")
        print("Starting in 30 seconds...")
        time.sleep(30)

        start_time = time.time()
        message_count = 0
        total_duration = 167 * 60  # 2 hours 47 minutes in seconds

        while time.time() - start_time < total_duration:
            message = self.create_message()
            self.send_message_now(message)
            message_count += 1

            elapsed = int(time.time() - start_time)
            elapsed_minutes = elapsed // 60

            # Check for break (6:37) between 1-2 hours
            if 60 <= elapsed_minutes <= 120 and random.random() < 0.05:
                print("\n--- Taking 6:37 minute break ---")
                time.sleep(597)  # 6 minutes 37 seconds

            # Regular delay between messages
            delay = self.get_delay()
            print(f"Message {message_count} sent. Waiting {delay}s... ({elapsed_minutes}m elapsed)")
            time.sleep(delay)

        print(f"\n✓ Campaign completed! Sent {message_count} messages over {elapsed_minutes} minutes")

# Usage Examples:
if __name__ == "__main__":
    # Initialize bot
    bot = WhatsAppRomanticBot("+91 8115529832")

    print("WhatsApp Romantic Message Bot")
    print("=" * 40)
    print("1. Test with 5 messages")
    print("2. Start full campaign (2h 47m)")
    print("3. Show message samples")

    choice = input("\nEnter choice (1/2/3): ")

    if choice == "1":
        bot.test_bot(5)
    elif choice == "2":
        confirm = input("Are you sure you want to start the full campaign? (yes/no): ")
        if confirm.lower() == "yes":
            bot.start_full_campaign()
        else:
            print("Campaign cancelled.")
    elif choice == "3":
        print("\nSample messages:")
        for i in range(20):
            print(f"- {bot.create_message()}")
    else:
        print("Invalid choice")
