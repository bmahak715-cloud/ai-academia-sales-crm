# AI-Powered B2B Academia Sales CRM System

A full-stack CRM for managing college and university outreach, partnerships, follow-ups, meetings, and AI-driven lead intelligence.

## Problem Statement

Sales teams working with academic institutions often manage leads through spreadsheets and email, leading to missed follow-ups, poor visibility, and manual effort. This system centralizes institution outreach and the full partnership lifecycle with AI-assisted prioritization and automation.

## Features

- **Authentication** — Role-based login (Admin, Sales Manager, Sales Executive)
- **Institution Lead Management** — Full CRUD, search, filter, sort, status updates, owner assignment
- **AI Lead Intelligence** — Priority scoring, outreach messages, follow-up suggestions (Anthropic API with fallback)
- **Automated Workflows** — Auto-assignment, initial follow-up task, notifications, activity logging on lead creation
- **Follow-up Management** — Tasks with overdue detection, due-today/upcoming views
- **Meeting Scheduling** — Schedule, complete, cancel with optional lead status update prompt
- **Communication** — AI-generated messages with review/edit/regenerate before marking as sent
- **Dashboard** — Live stats, pipeline, upcoming meetings, high-priority leads, AI insights
- **Reports** — Recharts visualizations for leads, pipeline, conversion, meetings
- **Notifications** — In-app bell with unread count, mark read/all read
- **Activity Log** — Full audit trail on dashboard and lead details

## Technology Stack

| Layer | Technologies |
|-------|-------------|
| Frontend | React, Vite, Tailwind CSS, React Router, Axios, Recharts |
| Backend | Python, Flask, Flask-CORS, Flask-SQLAlchemy, SQLite |
| Auth | Werkzeug password hashing, Flask sessions |
| AI | Anthropic API (via backend only) |

## Architecture

```
Browser (React)  →  Flask REST API  →  SQLite
                         ↓
                   Anthropic API (optional)
```

The frontend never communicates directly with Anthropic. All AI requests go through the Flask backend.

## Folder Structure

```
├── client/                 # React frontend
│   ├── src/
│   │   ├── components/     # Layout, Modal, Badge, etc.
│   │   ├── pages/          # Login, Dashboard, Leads, etc.
│   │   ├── context/        # Auth, Toast
│   │   ├── services/       # API client
│   │   └── utils/          # Constants, helpers
│   └── package.json
├── server/                 # Flask backend
│   ├── app/
│   │   ├── models/         # SQLAlchemy models
│   │   ├── routes/         # API blueprints
│   │   ├── services/       # AI, seed, assignment, etc.
│   │   └── utils/          # Auth, validators
│   ├── run.py
│   ├── requirements.txt
│   └── .env.example
└── README.md
```

## Database Models

| Model | Description |
|-------|-------------|
| User | Sales reps and admins with hashed passwords |
| Institution | College/university leads |
| AIAnalysis | AI score, priority, outreach message, suggestions |
| FollowUp | Tasks linked to institutions |
| Meeting | Scheduled meetings with completion notes |
| Communication | Message drafts and sent history |
| Activity | Audit log entries |
| Notification | In-app notifications per user |

**Delete behavior:** Deleting an institution cascades to all related records (AI analysis, follow-ups, meetings, communications, activities). Notifications referencing the institution remain but lose the institution link.

## Installation

### Prerequisites

- Python 3.10+
- Node.js 18+
- npm

### Environment Setup

1. Copy the environment template:

```bash
cd server
copy .env.example .env
```

2. Edit `server/.env` and add your Anthropic API key (optional — app works without it using rule-based fallback):

```env
ANTHROPIC_API_KEY=your_anthropic_api_key_here
PORT=5000
FLASK_ENV=development
```

### Backend Commands

```bash
cd server
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

Backend runs at: **http://localhost:5000**

### Frontend Commands

```bash
cd client
npm install
npm run dev
```

Frontend runs at: **http://localhost:5173**

## Anthropic Setup

1. Create an account at [https://console.anthropic.com](https://console.anthropic.com)
2. Generate an API key
3. Add it to `server/.env` as `ANTHROPIC_API_KEY`

Without a valid key, the app uses rule-based AI fallback and remains fully functional. Failed AI calls show a "Retry AI Analysis" option.

## Demo Credentials

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@academiacrm.com | admin123 |
| Sales Manager | rajesh@academiacrm.com | sales123 |
| Sales Executive | priya@academiacrm.com | sales123 |
| Sales Executive | amit@academiacrm.com | sales123 |
| Sales Executive | sneha@academiacrm.com | sales123 |

Demo data (7 institutions, follow-ups, meetings, activities) is seeded automatically when the database is empty.

## API Summary

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/login` | POST | Login |
| `/api/auth/logout` | POST | Logout |
| `/api/auth/me` | GET | Current user |
| `/api/institutions` | GET/POST | List/create leads |
| `/api/institutions/:id` | GET/PUT/DELETE | Lead CRUD |
| `/api/institutions/:id/status` | PATCH | Update status |
| `/api/institutions/:id/assign` | PATCH | Assign owner |
| `/api/institutions/:id/analyze` | POST | Retry AI analysis |
| `/api/institutions/:id/regenerate-outreach` | POST | Regenerate message |
| `/api/follow-ups` | GET/POST | Follow-up tasks |
| `/api/follow-ups/:id` | PUT/DELETE | Update/delete task |
| `/api/follow-ups/:id/complete` | PATCH | Complete task |
| `/api/meetings` | GET/POST | Meetings |
| `/api/meetings/:id` | PUT/DELETE | Update/cancel |
| `/api/meetings/:id/complete` | PATCH | Complete meeting |
| `/api/communications` | GET | List communications |
| `/api/communications/generate` | POST | Generate message |
| `/api/communications/send` | POST | Mark as sent |
| `/api/communications/:id/mark-sent` | PATCH | Mark draft sent |
| `/api/dashboard` | GET | Dashboard data |
| `/api/reports` | GET | Report data |
| `/api/notifications` | GET | List notifications |
| `/api/notifications/:id/read` | PATCH | Mark read |
| `/api/notifications/read-all` | PATCH | Mark all read |

## Testing Instructions

### Backend

```bash
cd server
venv\Scripts\activate
python -c "from app import create_app; create_app(); print('OK')"
python test_api.py
```

### Frontend

```bash
cd client
npm run build
```

### Manual Testing Checklist

1. Login with demo credentials
2. View dashboard stats and pipeline
3. Add, edit, delete a lead
4. Retry AI analysis on a lead
5. Generate and mark a message as sent
6. Create and complete follow-up tasks
7. Schedule and complete a meeting
8. Check notifications bell
9. View reports page charts

## Known Limitations

- Session-based auth (no JWT/refresh tokens)
- SQLite (not suitable for high-concurrency production)
- SMTP email sending is optional and requires additional env vars (`SMTP_HOST`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_PORT`, `SMTP_FROM`)
- AI uses Claude 3 Haiku; quality depends on API availability
- No file upload or document management
- Single-tenant architecture

## Future Enhancements

- PostgreSQL support for production
- Email integration with templates
- Calendar sync (Google/Outlook)
- Bulk import from CSV
- Advanced role permissions
- Real-time WebSocket notifications
- Mobile-responsive PWA
