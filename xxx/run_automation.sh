#!/bin/bash

echo "🚀 EMAIL AUTOMATION SYSTEM"
echo "========================"
echo ""
echo "Choose an option:"
echo "1. Manage Email List"
echo "2. Send Emails"
echo "3. Exit"
echo ""
read -p "Enter choice (1-3): " choice

case $choice in
    1)
        python3 email_manager.py
        ;;
    2)
        python3 email_automation.py
        ;;
    *)
        echo "Goodbye!"
        ;;
esac
