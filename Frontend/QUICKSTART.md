# ⚡ Quick Start Guide

Get Sentinel Health frontend running in under 2 minutes.

## Prerequisites

- **Node.js 18+** ([Download](https://nodejs.org/))
- **npm** (comes with Node.js)

Check your versions:
```bash
node --version  # Should be v18 or higher
npm --version   # Should be v9 or higher
```

## Setup Steps

### 1. Navigate to Frontend Directory
```bash
cd Frontend
```

### 2. Install Dependencies
```bash
npm install
```

This will install:
- Next.js 14
- React 18
- Tailwind CSS
- Framer Motion
- TypeScript
- Lucide React (icons)

**Installation time**: ~1-2 minutes depending on your internet speed

### 3. Start Development Server
```bash
npm run dev
```

You should see:
```
  ▲ Next.js 14.2.3
  - Local:        http://localhost:3000
  - Ready in 2.5s
```

### 4. Open in Browser
Navigate to: **http://localhost:3000**

You should see the Sentinel Health landing page! 🎉

## Troubleshooting

### Port 3000 Already in Use?
```bash
# Kill the process using port 3000
npx kill-port 3000

# Or run on a different port
npm run dev -- -p 3001
```

### Module Not Found Errors?
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

### TypeScript Errors?
```bash
# Regenerate TypeScript definitions
npm run build
```

## Environment Configuration

The `.env.local` file is pre-configured:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Change this** if your FastAPI backend runs on a different port.

## Available Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Start development server (hot reload enabled) |
| `npm run build` | Build for production |
| `npm start` | Start production server |
| `npm run lint` | Run ESLint |

## Next Steps

1. ✅ Frontend is running
2. 🔧 Set up the FastAPI backend (see `/Backend/README.md`)
3. 🎨 Customize the design (see `/DOCS/DESIGN_SYSTEM.md`)
4. 🚀 Start building features

## Need Help?

- **Design System**: `/DOCS/DESIGN_SYSTEM.md`
- **Full README**: `/Frontend/README.md`
- **Project Overview**: `/Idea.md`

---

**Estimated Setup Time**: 2-3 minutes  
**Last Updated**: May 6, 2026
