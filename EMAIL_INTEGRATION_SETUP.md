# Email Integration Setup - PRIMARY DRIVER

Email integration is the **PRIMARY DRIVER** of PlexSync AI. The system automatically polls your email inbox for invoices and processes them automatically.

## 🎯 How It Works

1. **Background Worker** continuously polls your email inbox
2. **Finds emails** with invoice attachments (PDF, images)
3. **Extracts attachments** automatically
4. **Processes invoices** through AI parser
5. **Creates invoice records** in the system
6. **Makes them available** for review and sync

## 📧 Email Configuration

### IMAP Setup (Recommended)

Add these to your `.env` file:

```env
# Email Integration (PRIMARY DRIVER)
EMAIL_PROVIDER=imap
EMAIL_IMAP_SERVER=imap.gmail.com
EMAIL_IMAP_PORT=993
EMAIL_USERNAME=your-email@gmail.com
EMAIL_PASSWORD=your-password
# OR use Gmail App Password:
EMAIL_APP_PASSWORD=your-app-password
EMAIL_POLL_INTERVAL=60
EMAIL_INBOX_FOLDER=INBOX
EMAIL_PROCESSED_FOLDER=Processed
EMAIL_FAILED_FOLDER=Failed

# Optional: Whitelist specific senders (empty = accept from anyone)
EMAIL_ALLOWED_SENDERS=vendor1@example.com,vendor2@example.com
```

### Gmail Setup

1. **Enable 2-Factor Authentication** on your Google account
2. **Generate App Password**:
   - Go to: https://myaccount.google.com/apppasswords
   - Create app password for "Mail"
   - Use this password in `EMAIL_APP_PASSWORD`

3. **IMAP Settings**:
   - Server: `imap.gmail.com`
   - Port: `993`
   - Username: Your Gmail address
   - Password: App password (not your regular password)

### Other Email Providers

**Outlook/Office 365:**
```env
EMAIL_IMAP_SERVER=outlook.office365.com
EMAIL_IMAP_PORT=993
```

**Yahoo:**
```env
EMAIL_IMAP_SERVER=imap.mail.yahoo.com
EMAIL_IMAP_PORT=993
```

**Custom IMAP:**
```env
EMAIL_IMAP_SERVER=mail.yourdomain.com
EMAIL_IMAP_PORT=993
```

## 🔄 Workflow

### Automatic Processing Flow:

1. **Email arrives** in inbox with invoice attachment
2. **Worker detects** new email (every 60 seconds by default)
3. **Extracts attachment** (PDF, PNG, JPG, etc.)
4. **Saves file** to storage
5. **Creates invoice record** with status "received"
6. **AI parses invoice** automatically
7. **Updates invoice** with parsed data (status → "parsed")
8. **Email moved** to "Processed" folder
9. **Invoice appears** in dashboard for review/sync

### Manual Upload (Secondary):

- Users can still manually upload invoices via web interface
- Same processing flow applies
- Useful for testing or one-off invoices

## ⚙️ Configuration Options

### Poll Interval
```env
EMAIL_POLL_INTERVAL=60  # Check every 60 seconds
```

### Allowed File Types
```env
EMAIL_ATTACHMENT_EXTENSIONS=pdf,png,jpg,jpeg,tiff
```

### Sender Whitelist (Optional)
```env
# Only process emails from these senders (comma-separated)
EMAIL_ALLOWED_SENDERS=vendor1@example.com,vendor2@example.com
# Leave empty to accept from anyone
```

## 🚀 Starting the System

The email worker starts automatically when you start the backend server:

```bash
cd backend
python main.py
```

You'll see:
```
✅ Email worker started - invoices will be automatically processed from email
📧 Email worker started - checking for invoices via email
   Poll interval: 60 seconds
```

## 📊 Monitoring

Check logs to see email processing:
- `✅ Processed X new invoice(s) from email` - Success
- `No new emails found` - Normal (no new emails)
- `Error in email polling loop` - Check configuration

## 🔒 Security

- Use **App Passwords** for Gmail (not your main password)
- Consider using **OAuth2** for production (future enhancement)
- Whitelist senders if you want to restrict who can send invoices
- Processed emails are moved to separate folder for audit trail

## 🐛 Troubleshooting

### "IMAP connection failed"
- Check server address and port
- Verify username and password
- For Gmail: Use App Password, not regular password
- Check firewall/network settings

### "No invoices processed"
- Check if emails have attachments
- Verify attachment file types are allowed
- Check sender whitelist (if configured)
- Look for errors in logs

### "Email worker not started"
- Check `FEATURE_EMAIL_INTEGRATION=true` in .env
- Verify `EMAIL_IMAP_SERVER` is configured
- Check logs for startup messages

## 📝 Next Steps

1. Configure email settings in `.env`
2. Restart backend server
3. Send a test email with invoice attachment
4. Watch logs for processing confirmation
5. Check dashboard for new invoice

---

**Email integration is now the PRIMARY DRIVER of invoice processing!** 🎉

