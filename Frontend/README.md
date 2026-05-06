# Sentinel Health - Frontend

Professional Next.js 14 frontend for the Sentinel Health patient safety monitoring platform.

## 🚀 Quick Setup

```bash
# Navigate to frontend directory
cd Frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) - Done! 🎉

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Animation**: Framer Motion
- **Icons**: Lucide React
- **Fonts**: Inter (body), Poppins (headings)

## Design System

This project follows a strict design system documented in `/DOCS/DESIGN_SYSTEM.md`:

- **Color Scheme**: Blue (primary) + Purple (accent) + Neutral grays
- **Typography**: Inter for body, Poppins for headings
- **Components**: Consistent button, card, and badge patterns
- **Animation**: Subtle, professional Framer Motion transitions

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn

### Installation

```bash
cd Frontend
npm install
```

### Environment Variables

The `.env.local` file is already configured:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Update this URL if your FastAPI backend runs on a different port.

### Development

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Build for Production

```bash
npm run build
npm start
```

## Project Structure

```
Frontend/
├── app/
│   ├── globals.css          # Tailwind imports + custom styles
│   ├── layout.tsx            # Root layout with font configuration
│   └── page.tsx              # Landing page
├── .env.local                # Environment variables
├── tailwind.config.ts        # Tailwind configuration
└── tsconfig.json             # TypeScript configuration
```

## API Integration

The frontend connects to the FastAPI backend via the `NEXT_PUBLIC_API_URL` environment variable.

Example usage:
```typescript
const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/endpoint`);
```

## Design Principles

1. **Professional & Clinical**: Clean, minimal design that conveys trust
2. **Consistent**: Follow the design system for all new components
3. **Accessible**: High contrast ratios, semantic HTML, focus states
4. **Responsive**: Mobile-first approach with progressive enhancement
5. **Performant**: Optimized animations, lazy loading, code splitting

## Contributing

When adding new components or pages:
1. Reference `/DOCS/DESIGN_SYSTEM.md` for color, typography, and spacing
2. Use existing component patterns (buttons, cards, badges)
3. Keep animations subtle and professional
4. Maintain the established color scheme
5. Test responsiveness across breakpoints

## License

Proprietary - Sentinel Health Team
