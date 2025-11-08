# Enable Real-Time News Fetching Plan

## Current Status
- System uses Celery polling every 2 hours for news collection
- Real-time components exist but not active due to import issues
- Frontend lacks WebSocket integration for live updates

## Tasks to Complete

### 1. Verify Redis Configuration
- [x] Check if Redis is installed and running
- [x] Install Redis if not present
- [x] Test Redis connectivity with `redis-cli ping`

### 2. Fix Import Path Issues
- [x] Update import paths in realtime_collector.py to resolve ModuleNotFoundError
- [x] Ensure models/__init__.py exists and is properly configured
- [x] Test imports work correctly

### 3. Start Real-Time Services
- [x] Launch realtime_main.py (collector service)
- [x] Launch websocket_server.py
- [ ] Verify services are running and communicating

### 4. Integrate Frontend
- [x] Add WebSocket connection to NewsFeed.tsx component
- [x] Implement live article updates in dashboard
- [x] Test WebSocket connection and data flow

### 5. Disable Polling (Optional)
- [ ] Comment out Celery schedules in config/settings.py
- [ ] Ensure real-time system handles all collection

### 6. Test Real-Time Functionality
- [ ] Verify articles appear instantly on dashboard
- [ ] Test end-to-end real-time flow
- [ ] Monitor performance and error handling
