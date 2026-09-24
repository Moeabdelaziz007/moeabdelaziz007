# Vercel Deployment Guide

This repository now includes a Next.js application with Vercel Web Analytics configured.

## Project Structure

- `app/` - Next.js App Router application
  - `layout.tsx` - Root layout with Analytics component
  - `page.tsx` - Home page
  - `globals.css` - Global styles
- `package.json` - Project dependencies including @vercel/analytics
- `next.config.js` - Next.js configuration
- `tsconfig.json` - TypeScript configuration

## Vercel Web Analytics

Vercel Web Analytics has been successfully installed and configured following the official documentation from https://vercel.com/docs/analytics/quickstart.

### Installation

The `@vercel/analytics` package has been added to the project dependencies:

```json
"dependencies": {
  "@vercel/analytics": "^1.1.1",
  "next": "14.0.4",
  "react": "^18.2.0",
  "react-dom": "^18.2.0"
}
```

### Configuration

The Analytics component has been added to the root layout (`app/layout.tsx`) following Next.js App Router best practices:

```typescript
import { Analytics } from '@vercel/analytics/next';

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        {children}
        <Analytics />
      </body>
    </html>
  );
}
```

## Deployment Steps

### 1. Enable Analytics in Vercel Dashboard

1. Go to your project in the Vercel dashboard
2. Navigate to the Analytics tab
3. Click "Enable" to activate Web Analytics

### 2. Deploy to Vercel

Deploy using one of these methods:

**Option A: Vercel CLI**
```bash
npm install -g vercel
vercel deploy
```

**Option B: Git Integration**
- Push to GitHub
- Import repository in Vercel dashboard
- Vercel will automatically deploy

**Option C: Vercel Dashboard**
- Use the Vercel dashboard import feature
- Select this repository
- Deploy

### 3. Verify Analytics

After deployment:
1. Visit your deployed site
2. Open browser DevTools Network tab
3. Look for requests to `/_vercel/insights/*` paths
4. These requests confirm that analytics tracking is active

## Local Development

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Run linter
npm run lint
```

The application will be available at http://localhost:3000

## Next Steps

1. Deploy the application to Vercel
2. Enable Web Analytics in the Vercel dashboard
3. Visit your site to generate analytics data
4. View analytics data in the Vercel dashboard after user visits accumulate

For more information about Vercel Web Analytics features:
- Custom events (available on Pro/Enterprise plans)
- Data redaction for privacy compliance
- Dashboard insights and metrics

## Notes

- Analytics tracking only works when deployed to Vercel
- In local development, the Analytics component is present but won't send data
- Make sure to enable Analytics in your Vercel project dashboard after deployment
