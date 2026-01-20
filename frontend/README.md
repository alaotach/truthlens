# TruthLens Frontend

React frontend for TruthLens - Product Reality & Fair Price Checker

## Quick Start

### 1. Install dependencies
```bash
npm install
```

### 2. Run development server
```bash
npm run dev
```

Frontend will be available at `http://localhost:5173`

### 3. Build for production
```bash
npm run build
```

## Tech Stack

- **React 18** - UI framework
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework
- **Axios** - HTTP client for API calls

## Project Structure

```
src/
├── components/
│   ├── InputForm.jsx       # Product input (URL or text)
│   ├── ResultCard.jsx      # Analysis results display
│   └── ScoreIndicator.jsx  # Circular score visualization
├── services/
│   └── api.js              # API service layer
├── App.jsx                 # Main app component
├── main.jsx                # App entry point
└── index.css               # Tailwind CSS imports
```

## Components

### InputForm
- Accepts product URL or text description
- Provides example products for testing
- Handles loading states

### ResultCard
- Displays analysis results
- Shows reality and pricing scores
- Lists claim verifications with confidence levels
- Highlights red flags
- Provides actionable recommendations

### ScoreIndicator
- Circular progress indicator
- Color-coded by score (green/yellow/red)
- Shows score description

## API Integration

The frontend connects to the FastAPI backend at `http://localhost:8000`

API calls are made through `services/api.js`:
- `analyzeProduct(input)` - Main analysis endpoint
- `extractClaims(input)` - Extract claims only
- `checkHealth()` - Backend health check

## Configuration

Vite proxy configuration in `vite.config.js` forwards `/api` requests to backend:
```javascript
proxy: {
  '/api': {
    target: 'http://localhost:8000',
    changeOrigin: true,
  }
}
```

## Styling

Tailwind CSS is configured with custom theme colors:
- `primary` - Blue (#3b82f6)
- `secondary` - Purple (#8b5cf6)
- `success` - Green (#10b981)
- `warning` - Yellow (#f59e0b)
- `danger` - Red (#ef4444)

## Development

Run in development mode with hot reload:
```bash
npm run dev
```

Build and preview production build:
```bash
npm run build
npm run preview
```
