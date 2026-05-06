# Sentinel Health - Design System Reference

## Color Palette

### Primary Colors (Blue - Trust & Healthcare)
- **Primary 50**: `#f0f9ff` - Lightest backgrounds
- **Primary 100**: `#e0f2fe` - Subtle backgrounds
- **Primary 600**: `#0284c7` - Main brand color, buttons, links
- **Primary 700**: `#0369a1` - Hover states
- **Primary 900**: `#0c4a6e` - Dark accents

### Accent Colors (Purple - Innovation & AI)
- **Accent 500**: `#d946ef` - Highlights, badges
- **Accent 600**: `#c026d3` - Interactive elements

### Neutral Colors (Gray Scale)
- **Neutral 50**: `#fafafa` - Page backgrounds
- **Neutral 100**: `#f5f5f5` - Card backgrounds
- **Neutral 200**: `#e5e5e5` - Borders
- **Neutral 600**: `#525252` - Secondary text
- **Neutral 900**: `#171717` - Primary text, headers

## Typography

### Font Families
- **Primary Font**: `Inter` - Body text, UI elements
- **Display Font**: `Poppins` - Headings, emphasis

### Font Weights
- Regular: 400
- Medium: 500
- Semibold: 600
- Bold: 700

### Type Scale
- **Hero Heading**: 3.75rem (60px) - `text-6xl`
- **Section Heading**: 2.25rem (36px) - `text-4xl`
- **Card Heading**: 1.25rem (20px) - `text-xl`
- **Body Large**: 1.125rem (18px) - `text-lg`
- **Body**: 1rem (16px) - `text-base`
- **Small**: 0.875rem (14px) - `text-sm`

## Spacing System

Following Tailwind's 4px base unit:
- **xs**: 0.5rem (8px)
- **sm**: 1rem (16px)
- **md**: 1.5rem (24px)
- **lg**: 2rem (32px)
- **xl**: 3rem (48px)
- **2xl**: 4rem (64px)

## Component Patterns

### Buttons

#### Primary Button
```tsx
className="px-8 py-4 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors font-semibold"
```

#### Secondary Button
```tsx
className="px-8 py-4 bg-white text-neutral-900 rounded-lg hover:bg-neutral-50 transition-colors font-semibold border border-neutral-200"
```

### Cards
```tsx
className="p-6 rounded-xl border border-neutral-200 hover:border-primary-300 hover:shadow-lg transition-all bg-white"
```

### Badges
```tsx
className="inline-flex items-center gap-2 px-4 py-2 bg-primary-50 rounded-full text-primary-700 text-sm font-medium"
```

### Icons
- Size: 20px (w-5 h-5) for inline icons
- Size: 24px (w-6 h-6) for feature icons
- Color: Inherit from parent or use `text-primary-600`

## Animation Guidelines

### Framer Motion Variants

#### Fade In Up
```tsx
initial={{ opacity: 0, y: 20 }}
animate={{ opacity: 1, y: 0 }}
transition={{ duration: 0.6 }}
```

#### Stagger Children
```tsx
transition={{ delay: index * 0.1 }}
```

### Transitions
- **Default**: `transition-colors` (200ms)
- **Hover Effects**: `transition-all` (300ms)
- **Page Animations**: 600ms duration

## Layout Principles

### Container
- Max width: `max-w-7xl` (1280px)
- Padding: `px-6` (24px horizontal)
- Centered: `mx-auto`

### Grid Systems
- Features: `grid md:grid-cols-2 lg:grid-cols-3 gap-8`
- Stats: `grid grid-cols-2 md:grid-cols-4 gap-8`

### Sections
- Padding: `py-20` (80px vertical)
- Alternating backgrounds: `bg-white` / `bg-neutral-50`

## Accessibility

### Contrast Ratios
- Primary text on white: 16:1 (AAA)
- Secondary text on white: 7:1 (AA)
- Primary button: 4.5:1 (AA)

### Focus States
- Add `focus:ring-2 focus:ring-primary-500 focus:outline-none` to interactive elements

### Semantic HTML
- Use proper heading hierarchy (h1 → h2 → h3)
- Use semantic tags: `<nav>`, `<section>`, `<footer>`

## Design Principles

1. **Professional & Clinical**: Clean, minimal design that conveys trust and reliability
2. **Consistent Spacing**: Use the 8px grid system throughout
3. **Subtle Animations**: Enhance UX without distraction
4. **Clear Hierarchy**: Use size, weight, and color to guide attention
5. **Responsive First**: Mobile-friendly layouts with progressive enhancement

## Usage in Code

### Import Fonts
```tsx
import { Inter, Poppins } from "next/font/google";
```

### Apply Classes
```tsx
className="font-display font-bold text-4xl text-neutral-900"
```

### Color Usage
- **Backgrounds**: White (`bg-white`) or Neutral 50 (`bg-neutral-50`)
- **Text**: Neutral 900 for headings, Neutral 600 for body
- **Accents**: Primary 600 for CTAs, links, and brand elements
- **Borders**: Neutral 200 for subtle separation

## File Structure
```
Frontend/
├── app/
│   ├── globals.css          # Tailwind imports + custom styles
│   ├── layout.tsx            # Font configuration
│   └── page.tsx              # Landing page
├── tailwind.config.ts        # Color & font definitions
└── .env.local                # API configuration
```

---

**Last Updated**: May 6, 2026
**Maintained By**: Sentinel Health Development Team
