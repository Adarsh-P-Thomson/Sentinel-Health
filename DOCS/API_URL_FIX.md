# API URL Configuration Fix

## Issue
Frontend was getting 404 errors when calling backend endpoints because of inconsistent API URL configuration.

## Root Cause
1. **Frontend `.env.local`** was missing the `/api/v1` prefix:
   - ❌ `NEXT_PUBLIC_API_URL=http://localhost:8000`
   - ✅ `NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1`

2. **Search page** was hardcoding `/api/v1` in the fetch URLs, causing double prefix:
   - ❌ `fetch(\`${process.env.NEXT_PUBLIC_API_URL}/api/v1/search\`)`
   - ✅ `fetch(\`${process.env.NEXT_PUBLIC_API_URL}/search\`)`

## What Was Fixed

### 1. Frontend Environment Variable
**File:** `Frontend/.env.local`

```diff
- NEXT_PUBLIC_API_URL=http://localhost:8000
+ NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

### 2. Search Page API Calls
**File:** `Frontend/app/search/page.tsx`

```diff
- fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/sources`)
+ fetch(`${process.env.NEXT_PUBLIC_API_URL}/sources`)

- fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/search`, {...})
+ fetch(`${process.env.NEXT_PUBLIC_API_URL}/search`, {...})
```

### 3. Suggestions Page (Already Correct)
**File:** `Frontend/app/suggestions/page.tsx`

The suggestions page was already using the correct pattern:
```typescript
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
fetch(`${API_BASE}/categories`)
fetch(`${API_BASE}/process/latest`)
```

## Result

All frontend pages now correctly call backend endpoints:

### Search Page
- ✅ `GET http://localhost:8000/api/v1/sources`
- ✅ `POST http://localhost:8000/api/v1/search`

### Suggestions Page
- ✅ `GET http://localhost:8000/api/v1/categories`
- ✅ `POST http://localhost:8000/api/v1/process/latest`
- ✅ `GET http://localhost:8000/api/v1/process/batch/{id}/status`
- ✅ `GET http://localhost:8000/api/v1/categories/{name}`

## Best Practice

**Always use the environment variable without hardcoding the prefix:**

```typescript
// ✅ GOOD - Let the env var handle the prefix
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
fetch(`${API_BASE}/endpoint`)

// ❌ BAD - Hardcoding /api/v1 causes double prefix
fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/endpoint`)
```

## Testing

After fixing, restart the frontend dev server to pick up the new environment variable:

```bash
cd Frontend
npm run dev
```

Then test:
1. Search page should load sources
2. Search should execute successfully
3. Suggestions page should load categories
4. Process button should work
