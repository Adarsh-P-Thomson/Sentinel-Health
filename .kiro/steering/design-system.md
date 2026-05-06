---
inclusion: auto
---

# Design System Rules for Sentinel Health

When working on the Sentinel Health frontend, always follow these design principles:

## Color Scheme
- **Primary**: Blue (`primary-600: #0284c7`) for trust and healthcare
- **Accent**: Purple (`accent-500: #d946ef`) for AI/innovation highlights
- **Neutral**: Gray scale for text and backgrounds
- **Never** introduce new color schemes without updating DOCS/DESIGN_SYSTEM.md

## Typography
- **Body text**: Inter font family
- **Headings**: Poppins font family (font-display class)
- **Weights**: Regular (400), Medium (500), Semibold (600), Bold (700)
- Maintain consistent type scale (text-sm, text-base, text-lg, text-xl, text-4xl, text-6xl)

## Component Consistency
- **Buttons**: Use established primary/secondary button classes
- **Cards**: `rounded-xl border border-neutral-200 hover:border-primary-300`
- **Spacing**: Follow 8px grid system (Tailwind spacing scale)
- **Icons**: Use lucide-react, size w-5 h-5 or w-6 h-6

## Animation Standards
- Use Framer Motion for page transitions
- Fade-in-up pattern: `initial={{ opacity: 0, y: 20 }}` → `animate={{ opacity: 1, y: 0 }}`
- Stagger delays: `delay: index * 0.1`
- Keep animations subtle and professional

## Layout Principles
- Max container width: `max-w-7xl`
- Section padding: `py-20 px-6`
- Alternate section backgrounds: white / neutral-50
- Responsive grid: `grid md:grid-cols-2 lg:grid-cols-3`

## Professional Standards
- No flashy or distracting elements
- Clean, minimal, clinical aesthetic
- Focus on clarity and usability
- Maintain high contrast for accessibility

## Reference
Full design system documentation: `DOCS/DESIGN_SYSTEM.md`

When creating new components or pages, reference this file and maintain consistency with existing patterns.
