# Sentry Error Monitoring Setup

## 📊 Current Configuration

**DSN Type**: User Reporting DSN (`sntryu_*`)
```
SENTRY_DSN=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
```

## ⚠️ Important: DSN Types

### User Reporting DSN (`sntryu_*`)
- **Purpose**: Frontend user feedback and session replay
- **Used for**: React/Next.js applications
- **Not for**: Backend error tracking

### Standard DSN (`https://`)
- **Purpose**: Backend/server error tracking
- **Used for**: Python FastAPI, Node.js servers
- **Format**: `https://<key>@<host>/<project>`

## 🔧 Current Status

**Backend**: Sentry SDK requires standard DSN format
- User Reporting DSN detected but cannot be used directly
- Backend error tracking **disabled** until standard DSN is provided
- All errors are still logged to console/logs

**Frontend**: User Reporting DSN can be used
- Suitable for Next.js/React applications
- Enables user feedback collection
- Session replay (if enabled)

## ✅ How to Enable Full Sentry

### Step 1: Get Standard DSN for Backend

1. Go to Sentry Dashboard
2. Navigate to: **Settings → Projects → [Your Project]**
3. Go to: **Client Keys (DSN)**
4. Copy the **standard DSN** (starts with `https://`)
5. Update `.env`:
   ```
   SENTRY_DSN=https://xxxxx@xxxxx.ingest.sentry.io/xxxxx
   ```

### Step 2: Keep User Reporting DSN for Frontend

The User Reporting DSN can be used in the frontend:

```typescript
// src/app/providers.tsx or similar
import * as Sentry from "@sentry/nextjs"

Sentry.init({
  dsn: "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",
  // User reporting settings
  beforeSend(event, hint) {
    // Filter events if needed
    return event
  },
})
```

### Step 3: Update Environment Variables

**Backend** (`server/.env`):
```env
# Standard DSN for backend error tracking
SENTRY_DSN=https://xxxxx@xxxxx.ingest.sentry.io/xxxxx
SENTRY_RELEASE=1.0.0  # Optional
ENVIRONMENT=development
```

**Frontend** (`.env.local`):
```env
# User Reporting DSN for frontend
NEXT_PUBLIC_SENTRY_DSN=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
```

## 📋 Features Enabled with Sentry

### Backend (Standard DSN)
- ✅ Automatic error capture
- ✅ Performance monitoring
- ✅ Request tracking
- ✅ SQL query tracking
- ✅ Release tracking
- ✅ Environment tagging

### Frontend (User Reporting DSN)
- ✅ User feedback collection
- ✅ Session replay
- ✅ Frontend error tracking
- ✅ Performance monitoring

## 🔍 Testing Sentry

### Test Backend Error
```python
# This will be captured when standard DSN is configured
raise Exception("Test error for Sentry")
```

### Test Frontend Error
```typescript
// In browser console or component
throw new Error("Test frontend error")
```

## 📊 Current Implementation

### Backend (`server/api/main.py`)
- Detects User Reporting DSN format
- Shows warning message
- Does not initialize (requires standard DSN)
- All errors still logged normally

### Error Handling
- Custom exception handlers already integrated
- Ready for Sentry once DSN is configured
- Errors logged with full context

## 🚀 Next Steps

1. ✅ User Reporting DSN stored in `.env`
2. ⏳ Get standard DSN from Sentry dashboard
3. ⏳ Update `server/.env` with standard DSN
4. ⏳ Restart server to enable Sentry
5. ⏳ (Optional) Add frontend Sentry integration

## 📚 Documentation

- [Sentry Python SDK](https://docs.sentry.io/platforms/python/)
- [Sentry Next.js SDK](https://docs.sentry.io/platforms/javascript/guides/nextjs/)
- [User Reporting Guide](https://docs.sentry.io/platforms/javascript/user-feedback/)

