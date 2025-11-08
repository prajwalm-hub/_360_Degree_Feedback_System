# Login Page Error Fix Guide

## Problem
Error: `Unexpected token '<', '<!DOCTYPE...' is not valid JSON`

This error occurs when the frontend tries to parse an HTML error page as JSON, typically because the backend API is not reachable.

---

## ✅ Solution Applied

### 1. **Enhanced Error Handling in AuthContext**
- Added check for HTML responses (backend not reachable)
- Improved error messages to guide users
- Better handling of network errors

### 2. **Updated Frontend Environment Variables**
File: `frontend/.env`
```env
VITE_API_BASE_URL=http://localhost:8000
VITE_API_URL=/api
```

### 3. **Created Backend Health Check Script**
Run `CHECK-BACKEND.bat` to verify backend status

---

## 🚀 How to Fix

### Step 1: Start the Backend Server

**Option A: Using the start script**
```powershell
# From project root
.\start-backend.bat
```

**Option B: Manual start**
```powershell
# Navigate to backend directory
cd backend

# Activate virtual environment (if using one)
.\.venv\Scripts\Activate.ps1

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 2: Verify Backend is Running

**Option A: Use the check script**
```powershell
.\CHECK-BACKEND.bat
```

**Option B: Manual check**
```powershell
# Test health endpoint
curl http://localhost:8000/api/health

# Expected response:
# {"status":"ok","name":"360-Degree Feedback Backend","env":"development"}
```

**Option C: Open in browser**
- Navigate to: http://localhost:8000/docs
- You should see the FastAPI Swagger documentation

### Step 3: Start the Frontend

```powershell
# From project root
.\start-frontend.bat

# Or manually:
cd frontend
npm run dev
```

### Step 4: Test Login

1. Open browser: http://localhost:5173
2. Use demo credentials:
   - **Username:** `pib_delhi`
   - **Password:** `officer123`

---

## 🔍 Troubleshooting

### Error: "Backend server is not reachable"

**Cause:** Backend is not running on port 8000

**Fix:**
1. Check if backend is running: `CHECK-BACKEND.bat`
2. Check if port 8000 is in use: `netstat -ano | findstr :8000`
3. Kill process if needed: `taskkill /PID <PID> /F`
4. Restart backend

### Error: "Cannot connect to backend server"

**Cause:** Network/firewall blocking connection

**Fix:**
1. Check Windows Firewall settings
2. Ensure localhost is accessible
3. Try: `ping localhost`
4. Check proxy settings

### Error: "CORS policy blocked"

**Cause:** CORS configuration issue

**Fix:**
1. Verify `backend/app/config.py` has:
   ```python
   CORS_ORIGINS: List[str] = ["*", "http://localhost:5173", "http://127.0.0.1:5173"]
   ```
2. Restart backend after changes

### Error: "Database connection failed"

**Cause:** PostgreSQL not running

**Fix:**
1. Start PostgreSQL service
2. Or use Docker: `docker compose up db -d`
3. Verify connection in `backend/.env`:
   ```env
   DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/newsdb
   ```

---

## 📋 Quick Checklist

- [ ] Backend running on http://localhost:8000
- [ ] Health endpoint accessible: http://localhost:8000/api/health
- [ ] API docs accessible: http://localhost:8000/docs
- [ ] Frontend running on http://localhost:5173
- [ ] No CORS errors in browser console
- [ ] Database connection working

---

## 🔧 Configuration Files

### Backend API Configuration
**File:** `backend/app/config.py`
```python
API_PREFIX: str = "/api"  # All routes prefixed with /api
PORT: int = 8000
CORS_ORIGINS: List[str] = ["*", "http://localhost:5173"]
```

### Frontend Proxy Configuration
**File:** `frontend/vite.config.ts`
```typescript
proxy: {
  '/api': {
    target: 'http://localhost:8000',
    changeOrigin: true,
    secure: false,
    ws: true
  }
}
```

### Environment Variables
**File:** `frontend/.env`
```env
VITE_API_BASE_URL=http://localhost:8000
VITE_API_URL=/api
```

---

## 🎯 API Endpoints

### Authentication
- **POST** `/api/auth/login` - User login
- **GET** `/api/auth/me` - Get current user
- **POST** `/api/auth/change-password` - Change password

### Health Check
- **GET** `/api/health` - Server health status

### News
- **GET** `/api/news` - List articles
- **GET** `/api/news/latest` - Latest articles
- **POST** `/api/collect` - Trigger collection

---

## 📞 Support

If issues persist:

1. Check backend logs for errors
2. Check browser console for network errors
3. Verify all dependencies installed:
   ```powershell
   # Backend
   cd backend
   pip install -r requirements.txt
   
   # Frontend
   cd frontend
   npm install
   ```

4. Try clearing browser cache and localStorage
5. Restart both servers

---

## ✨ What Was Fixed

1. **AuthContext.tsx** - Added proper error handling for:
   - HTML responses (backend not reachable)
   - Network errors
   - JSON parsing errors
   - Clear error messages

2. **Environment Configuration** - Added:
   - `VITE_API_BASE_URL` for backend URL
   - Proper API prefix configuration

3. **Health Check Script** - Created:
   - `CHECK-BACKEND.bat` for quick backend verification

4. **Documentation** - Created:
   - This comprehensive troubleshooting guide

---

**Last Updated:** 2024
**Status:** ✅ Fixed and Tested
