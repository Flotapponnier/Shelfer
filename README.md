# AI SEO Analyzer

A full-stack application that analyzes websites for SEO performance using AI-powered scraping and scoring.

## Project Structure

```
├── frontend/          # Next.js React application
│   ├── src/
│   │   └── app/
│   │       └── page.tsx   # Main SEO analyzer interface
│   └── package.json
├── backend/           # FastAPI Python backend
│   ├── main.py        # API endpoints
│   └── requirements.txt
└── README.md
```

## Quick Start

### Backend (FastAPI)
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend (Next.js)
```bash
cd frontend
npm install
npm run dev
```

Visit http://localhost:3000 to use the application.

## Features

- URL-based SEO analysis
- Real-time scoring
- Responsive web interface
- RESTful API backend
- CORS-enabled for development
