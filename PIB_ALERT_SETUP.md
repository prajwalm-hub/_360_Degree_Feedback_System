# PIB Alert System - Quick Setup

## 📧 Gmail Configuration (Required)

### Step 1: Enable 2-Step Verification
1. Go to https://myaccount.google.com/security
2. Enable "2-Step Verification"

### Step 2: Generate App Password
1. Search "App passwords" in Google Account
2. Select "Mail" → "Other (NewsScope)"
3. Copy the 16-character password

### Step 3: Configure Environment
Edit `backend/.env`:
```env
SMTP_ENABLED=true
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=xxxx xxxx xxxx xxxx
PIB_ALERT_EMAIL=prajwalmgowda3@gmail.com
ALERT_ENABLED=true
ALERT_NEGATIVE_THRESHOLD=0.6
```

## 🚀 Quick Start

```bash
# 1. Restart backend
cd backend
uvicorn app.run_server:app --host 0.0.0.0 --port 8001 --reload

# 2. Access frontend
# Navigate to: http://localhost:5173
# Click "PIB Alerts" in sidebar
```

## 📊 Features

✅ Auto-detects negative news (sentiment ≥ 0.6)  
✅ Sends email alerts instantly  
✅ Web interface for alert management  
✅ Badge shows unread count  
✅ Filter by status and language  

## 🔧 Configuration Options

```env
# Adjust sensitivity (0.0 - 1.0)
ALERT_NEGATIVE_THRESHOLD=0.6  # Default

# Disable email (DB only)
SMTP_ENABLED=false

# Disable alerts completely
ALERT_ENABLED=false
```

## 📖 Documentation

Full details: `docs/RESEARCH_PAPER_IEEE.md` (Section V.F)

---

**Status**: Production Ready ✅  
**Setup Time**: 5 minutes
