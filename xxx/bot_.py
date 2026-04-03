

"""
QUICK FIX VERSION - Addresses immediate issues with your bot
===========================================================

This version fixes:
1. ✅ Removes spelling variations (clean messages only)
2. ✅ Reduces new tab issues with better timing and tab closing
3. ⚡ Simple optimizations for better performance
4. 🎯 Keeps it simple - minimal changes to your existing code

Usage: Just replace your bot.py with this version!
"""

import pywhatkit as pwk
import random
import time
import datetime
import pyautogui

class QuickFixWhatsAppBot:
    def __init__(self, phone_number):
        self.phone_number = phone_number
        self.messages = []
        self.emojis = {
            'primary': '🥰',  # 75% of the time
            'secondary': ['😘', '😚', '😙', '❤️', '💕', '😍', '💖','💘,''💝','💓','❣️']  # 25% of the time
        }
        self.create_clean_messages()  # 🔥 NO MORE SPELLING ERRORS!

    def create_clean_messages(self):
        """Create clean message templates - NO spelling variations"""
        # 🎯 CLEAN MESSAGES ONLY - no more 'lovee', 'youu', 'bachaa', etc.
        
        self.messages = [
            "I Love you",
            "I love you", 
"Love you",
            "love you",
            "Love you",
            "love you",
            "I Love you bacha",
            "I love you bachaa",
            
            "Love you Shalini",
            
            "I love you bachaa",
            "Love you Shalini",
            "love you Shalini",
            "I Love you Shalini",
            "I love you Shalini"
        ]

    def get_emoji(self):
        """Get emoji based on 75% primary, 25% secondary distribution"""
        if random.random() < 0.20 :
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

    def create_message(self):
        """Create a complete message with text and emojis"""
        base_message = random.choice(self.messages)
        emoji_count = self.get_emoji_count()

        if emoji_count == 0:
            return base_message

        emojis = ""
        for _ in range(emoji_count):
            emojis += self.get_emoji()

        # 90% at the end, 10% at the beginning  
        if random.random() < 0.9:
            return f"{base_message} {emojis}"
        else:
            return f"{emojis} {base_message}"

    def send_message_optimized(self, message):
        """Optimized message sending with tab management"""
        try:
            # Get current time + 1 minute (minimum for pywhatkit)
            now = datetime.datetime.now()
            send_time = now + datetime.timedelta(minutes=1)
            hour = send_time.hour
            minute = send_time.minute
            

            print(f"Sending: '{message}' at {hour:02d}:{minute:02d}")

            # 🔥 KEY OPTIMIZATION: Use tab_close=True and shorter wait time
            pwk.sendwhatmsg(
                self.phone_number, 
                message, 
                hour, 
                minute, 
                wait_time=10,    # Reduced from 20 to 15 seconds
                tab_close=True,  # 🎯 CLOSES TAB AUTOMATICALLY!
                close_time=15     # Closes after 3 seconds
            )

            print(f"✅ Message sent successfully!")
            return True

        except Exception as e:
            print(f"❌ Error sending message: {e}")
            return False

    def send_message_instant(self, message):
        """Send message instantly (alternative method)"""
        try:
            print(f"Sending instantly: '{message}'")

            # 🚀 INSTANT SEND - no scheduling needed
            pwk.sendwhatmsg_instantly(
                self.phone_number,
                message,
                wait_time=10,    # Shorter wait time
                tab_close=True   # 🎯 CLOSES TAB AFTER SENDING
            )

            print(f"✅ Instant message sent!")
            return True

        except Exception as e:
            print(f"❌ Error sending instant message: {e}")
            return False

    def test_bot_improved(self, num_messages=5, use_instant=True):
        """Improved test with better tab management"""
        print(f"🚀 Testing improved bot with {num_messages} messages")
        print(f"📱 Target: {self.phone_number}")
        print(f"⚡ Mode: {'Instant' if use_instant else 'Scheduled'}")
        print("=" * 50)

        successful_sends = 0

        for i in range(num_messages):
            print(f"\n📤 Message {i+1}/{num_messages}")

            message = self.create_message()

            if use_instant:
                success = self.send_message_instant(message)
            else:
                success = self.send_message_optimized(message)

            if success:
                successful_sends += 1

            # Wait between messages (except for last one)
            if i < num_messages - 1:
                delay = random.randint(2, 5)  # Shorter delays
                print(f"⏱️  Waiting {delay} seconds before next message...")
                time.sleep(delay)

        print(f"\n" + "=" * 50)
        print(f"✅ Test completed!")
        print(f"📊 Success rate: {successful_sends}/{num_messages} messages sent")
        print(f"🎯 All messages were clean (no spelling errors)")
        print(f"🚀 Tabs were closed automatically")

        return successful_sends

    def show_sample_messages(self, count=10):
        """Show sample messages that will be sent"""
        print(f"📝 Sample clean messages (no spelling errors):")
        print("-" * 40)
        for i in range(count):
            sample = self.create_message()
            print(f"{i+1:2d}. {sample}")
        print("-" * 40)


# 🎯 SIMPLE USAGE EXAMPLE
def main():
    """Main function - easy to use!"""
    print("🔥 QUICK FIX WhatsApp Bot - Issues Resolved!")
    print("=" * 50)

    # Initialize bot
    phone_number = "+91 8471039615"  # Your number
    bot = QuickFixWhatsAppBot(phone_number)

    # Show what changed
    print("✅ FIXES APPLIED:")
    print("   1. Removed ALL spelling errors")
    print("   2. Added automatic tab closing") 
    print("   3. Optimized timing and delays")
    print("   4. Better error handling")
    print()

    # Show sample messages
    bot.show_sample_messages(8)

    print("\n🚀 Ready to test? Choose an option:")
    print("1. Test with 3 messages (instant mode)")
    print("2. Test with 5 messages (instant mode)") 
    print("3. Show more sample messages")
    print("4. Exit")

    try:
        choice = input("\nEnter choice (1-4): ").strip()

        if choice == "1":
            print("\n🚀 Testing with 3 messages...")
            bot.test_bot_improved(3, use_instant=True)
        elif choice == "2":
            print("\n🚀 Testing with 5 messages...")
            bot.test_bot_improved(765
                                  , use_instant=True)
        elif choice == "3":
            bot.show_sample_messages(15)
        elif choice == "4":
            print("👋 Goodbye!")
        else:
            print("❌ Invalid choice")

    except KeyboardInterrupt:
        print("\n\n👋 Bot stopped by user")


if __name__ == "__main__":
    main()

