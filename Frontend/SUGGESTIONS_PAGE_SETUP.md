# Suggestions Page - Setup Guide

## Overview

The Suggestions page displays AI-processed, categorized content from social media posts with:
- **Category browsing** - View all categories (medicine, hospital, drug, etc.)
- **Detailed insights** - AI suggestions, info, sentiment, severity
- **Batch processing** - Process new search results with one click
- **Real-time updates** - Live batch progress tracking
- **Reload functionality** - Refresh data anytime

---

## Features

### 1. Category Display
- Grid view of all categories
- Filter by type (medicine, drug, hospital, condition, symptom, procedure, general)
- Shows entry count and tags
- Click to view details

### 2. Process Button
- Enter search execution ID
- Triggers batch processing
- Shows real-time progress
- Updates categories when complete

### 3. Category Details Modal
- View all entries for a category
- AI suggestions and info
- Sentiment and severity indicators
- Adverse event flags
- Processing timestamps

### 4. Reload Button
- Refresh categories list
- Get latest data
- Loading indicator

---

## Setup

### 1. Environment Variables

Create/update `Frontend/.env.local`:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 2. Install Dependencies

```bash
cd Frontend
npm install
```

### 3. Start Frontend

```bash
npm run dev
```

### 4. Access Page

Navigate to: http://localhost:3000/suggestions

---

## Usage Flow

### Step 1: Perform Search
1. Go to `/search` page
2. Enter query (e.g., "Lisinopril side effects")
3. Select sources (e.g., Reddit)
4. Click "Search"
5. **Copy the search_execution_id from the response**

### Step 2: Process Results
1. Go to `/suggestions` page
2. Paste search_execution_id in the input
3. Click "Process" button
4. Watch batch progress in real-time
5. Wait for completion (~2-3 minutes for 100 posts)

### Step 3: View Results
1. Categories appear automatically after processing
2. Filter by type (medicine, drug, etc.)
3. Click a category to view details
4. Read AI suggestions and insights

### Step 4: Refresh Data
- Click "Reload" button anytime to fetch latest data
- New entries are added to existing categories

---

## UI Components

### Category Card
```
┌─────────────────────────────────┐
│ Ibuprofen          [medicine]   │
│ 📄 150 entries                  │
│ [NSAID] [pain relief]           │
└─────────────────────────────────┘
```

### Category Details Modal
```
┌─────────────────────────────────────────┐
│ Ibuprofen                          [X]  │
│ 150 total entries                       │
├─────────────────────────────────────────┤
│ [negative] [medium] [Adverse Event]     │
│                                         │
│ Patient reports severe stomach pain...  │
│                                         │
│ 💡 AI Suggestion:                       │
│ Consider switching to acetaminophen...  │
│                                         │
│ ℹ️ Additional Info:                     │
│ Ibuprofen is an NSAID that can cause... │
└─────────────────────────────────────────┘
```

### Batch Progress
```
Processing Batch 1/5:
[████████████░░░░░░░░] 15/20 posts | processing
[████████████████████] 20/20 posts | completed
```

---

## API Integration

### Endpoints Used:

1. **GET /api/v1/categories**
   - Fetches all categories
   - Supports filtering by type
   - Returns category list

2. **GET /api/v1/categories/{name}**
   - Fetches category details
   - Returns entries with AI analysis
   - Limited to 50 most recent entries

3. **POST /api/v1/process/search**
   - Triggers batch processing
   - Background processing mode
   - Returns batch IDs

4. **GET /api/v1/process/batch/{id}/status**
   - Polls batch status
   - Returns progress (processed/total)
   - Shows completion status

---

## Example Workflow

### Complete Example:

```bash
# 1. Start Backend
cd Backend
uvicorn app.main:app --reload

# 2. Start Frontend
cd Frontend
npm run dev

# 3. Perform Search
# Go to: http://localhost:3000/search
# Search: "Lisinopril side effects"
# Sources: Reddit
# Result: search_execution_id = "abc-123-def-456"

# 4. Process Results
# Go to: http://localhost:3000/suggestions
# Enter: "abc-123-def-456"
# Click: "Process"
# Wait: ~2-3 minutes

# 5. View Results
# Categories appear automatically
# Click "Lisinopril" to see details
# Read AI suggestions and insights
```

---

## Styling

Uses Tailwind CSS with:
- **Sky Blue** (#0284c7) - Primary color
- **Purple** (#d946ef) - Accent color
- **Framer Motion** - Smooth animations
- **Responsive Design** - Mobile-friendly

### Color Coding:

**Sentiment:**
- Very Negative: Red
- Negative: Orange
- Neutral: Gray
- Positive: Green
- Very Positive: Emerald

**Severity:**
- Low: Blue
- Medium: Yellow
- High: Orange
- Critical: Red

**Category Types:**
- Medicine: Blue
- Drug: Indigo
- Hospital: Green
- Condition: Red
- Symptom: Orange
- Procedure: Purple
- General: Gray

---

## Troubleshooting

### Issue: "Failed to fetch categories"
**Solution:** Make sure backend is running on port 8000

### Issue: "No categories found"
**Solution:** Process some search results first

### Issue: "Processing failed"
**Solution:** 
- Check search_execution_id is valid
- Ensure MongoDB collections are created
- Verify Azure OpenAI credentials

### Issue: Batch stuck at "processing"
**Solution:**
- Check backend logs for errors
- Verify Azure OpenAI is responding
- Check batch status in MongoDB

---

## Performance

- **Initial Load:** ~500ms (fetching categories)
- **Category Details:** ~200ms (fetching entries)
- **Batch Processing:** ~2-3 minutes (100 posts)
- **Polling Interval:** 3 seconds (batch status)

---

## Next Steps

1. ✅ Suggestions page created
2. ✅ Category browsing implemented
3. ✅ Batch processing integrated
4. ⏳ **Next:** Add search filters
5. ⏳ **Next:** Export functionality
6. ⏳ **Next:** Analytics dashboard
7. ⏳ **Next:** Real-time notifications

---

## Navigation

The page is accessible from:
- Landing page: "Suggestions" link in nav
- Search page: "Suggestions" link in nav
- Direct URL: `/suggestions`

**Ready to use!** 🎉
