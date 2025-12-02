# PlexSync AI - Frontend

React + TypeScript frontend application for PlexSync AI invoice management system.

## Features

- 📊 **Dashboard** - Overview of invoices and statistics
- 📤 **Upload** - Upload and parse invoices using AI
- 🔍 **Review** - Review extracted data and sync to Plex ERP
- 🔐 **Authentication** - Secure login and registration
- 🎨 **Modern UI** - Built with Tailwind CSS and shadcn/ui components

## Tech Stack

- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **React Router** - Navigation
- **Axios** - HTTP client
- **Tailwind CSS** - Styling
- **Lucide React** - Icons
- **date-fns** - Date formatting

## Getting Started

### Prerequisites

- Node.js 18+ and npm/yarn

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will be available at `http://localhost:3000`

### Build for Production

```bash
npm run build
```

The built files will be in the `dist` directory.

## Environment Variables

Create a `.env` file in the frontend directory:

```env
VITE_API_URL=http://localhost:8000
```

## Project Structure

```
frontend/
├── src/
│   ├── api/           # API client and types
│   ├── components/    # React components
│   │   ├── ui/       # Reusable UI components
│   │   └── Layout.tsx # Main layout component
│   ├── contexts/      # React contexts (Auth)
│   ├── lib/          # Utility functions
│   ├── pages/        # Page components
│   │   ├── Dashboard.tsx
│   │   ├── Upload.tsx
│   │   ├── Review.tsx
│   │   ├── Login.tsx
│   │   └── Register.tsx
│   ├── App.tsx       # Main app component with routing
│   ├── main.tsx      # Entry point
│   └── index.css     # Global styles
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
└── tailwind.config.js
```

## API Integration

The frontend communicates with the backend API through the `src/api/client.ts` module. All API calls are authenticated using JWT tokens stored in localStorage.

## Development

The frontend uses Vite's proxy configuration to forward `/api` requests to the backend server running on port 8000. This is configured in `vite.config.ts`.

