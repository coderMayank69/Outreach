# 🚀 EMAIL AUTOMATION SETUP GUIDE

## Step 1: Install Dependencies
```bash
pip install pandas
```
OR
```bash
pip install -r requirements.txt
```

## Step 2: Setup Gmail App Password
1. Go to your Gmail account settings
2. Click "Security" in the left sidebar
3. Enable "2-Step Verification" (if not already enabled)
4. Scroll down to "App passwords"
5. Select "Mail" and "Windows Computer" (or Other)
6. Copy the 16-character password (save this!)

## Step 3: Add Your Email Addresses
```bash
python email_manager.py
```
- Choose option 1 to paste emails from notes
- OR choose option 2 to load from text file
- OR choose option 3 to add manually

## Step 4: Update Email Content
Open `email_automation.py` and update:
- YOUR_VIDEO_LINK_HERE → Your 2-minute pitch video URL
- YOUR_PORTFOLIO_LINK_HERE → Your portfolio website URL

## Step 5: Send Emails
```bash
python email_automation.py
```
- Choose option 1 to send bulk emails
- First time: Enter your Gmail and App Password
- System will remember credentials for future use

## 📁 Files Created:
- `email_list.csv` → Your email database
- `gmail_config.txt` → Saved Gmail credentials (optional)
- `email_automation.py` → Main sending script
- `email_manager.py` → Email list management
- `requirements.txt` → Python dependencies

## 🔒 Security Features:
- ✅ Duplicate prevention (won't send twice to same email)
- ✅ Status tracking (Not Sent → Sent → Failed)
- ✅ Progress saving (can resume if interrupted)
- ✅ 30-second delays between emails (anti-spam)
- ✅ Error handling and logging

## 📊 Usage:
1. Run `python email_manager.py` to add emails
2. Run `python email_automation.py` to send emails
3. Check statistics anytime with option 2

## 🔄 Adding More Emails Later:
Just run `email_manager.py` again and add new emails.
The system automatically prevents duplicates!
