# AI-Agent Calendar App

[![CI/CD Pipeline](https://github.com/user/agentic-calendar-app/actions/workflows/ci.yml/badge.svg)](https://github.com/user/agentic-calendar-app/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/user/agentic-calendar-app/branch/main/graph/badge.svg)](https://codecov.io/gh/user/agentic-calendar-app)

A modern, AI-powered calendar application built with FastAPI and React. Features intelligent event creation, comprehensive CRUD operations, and a clean, responsive interface.

## 🚀 Features

### Phase 1 (Current)
- **Complete CRUD Operations**: Create, read, update, delete calendar events
- **Smart Event Management**: Support for timed and all-day events with overlap prevention for all-day events
- **AI-Powered Event Creation**: Natural language processing for event drafts
- **Multi-View Calendar**: Month, week, and day views with responsive design
- **Advanced Search**: Keyword search and date-range filtering
- **Production-Ready**: Docker containerization, comprehensive testing, CI/CD pipeline

### Event Fields
- **Core**: ID, title, description, start/end datetime (ISO 8601, timezone-aware)
- **Properties**: All-day flag, location, attendees (email array)
- **Metadata**: Created/updated timestamps, original timezone

### API Endpoints
- `GET /api/v1/events` - List events with filtering and pagination
- `GET /api/v1/events/{id}` - Get specific event
- `POST /api/v1/events` - Create new event
- `PUT /api/v1/events/{id}` - Update event
- `DELETE /api/v1/events/{id}` - Delete event
- `POST /api/v1/events/draft` - Generate AI event draft

## 🏗️ Tech Stack

### Backend
- **FastAPI** (Python 3.11) - High-performance async web framework
- **SQLModel/SQLAlchemy** - Database ORM with type safety
- **Pydantic v2** - Data validation and serialization
- **SQLite** - File-based database with Alembic migrations
- **Luxon** - Advanced date/time handling

### Frontend
- **React 18** + **Vite** + **TypeScript** - Modern React development
- **Tailwind CSS** - Utility-first styling with responsive design
- **TanStack Query** - Server state management with optimistic updates
- **Luxon** - Client-side date handling
- **React Hook Form** - Form management with validation

### DevOps & Quality
- **Docker** + **Docker Compose** - Containerization
- **GitHub Actions** - CI/CD pipeline
- **Testing**: Pytest (backend), Vitest + Testing Library (frontend), Playwright (E2E)
- **Linting**: Ruff, Black, isort, mypy (Python), ESLint, Prettier (TypeScript)
- **Pre-commit hooks** - Code quality enforcement

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)

### Option 1: Docker Compose (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd agentic-calender-app

# Start the application
make dev
# or
docker-compose up --build

# The app will be available at:
# Frontend: http://localhost:5173
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Option 2: Local Development

```bash
# Setup development environment
make setup

# Start backend and frontend separately
make dev-local

# Or start individually:

# Backend (Terminal 1)
cd backend
pip install -e ".[dev]"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend (Terminal 2)
cd frontend
npm install
npm run dev
```

### Seed Sample Data

```bash
# Add sample events for demonstration
make seed

# Reset database with fresh sample data
cd backend && python -m app.scripts.seed --reset
```

## 📖 Usage Guide

### Creating Events

1. **Manual Creation**
   - Click "New Event" or click on any calendar date
   - Fill out the event form with title, time, location, etc.
   - Save to create the event

2. **AI-Assisted Creation**
   - Click "New Event" and use the AI assistant
   - Type natural language like "Meeting with John tomorrow 3pm at Cafe Rio"
   - AI will parse and suggest event details
   - Review and modify before saving

### Managing Events

- **View Events**: Switch between Month, Week, and Day views
- **Edit Events**: Click on any event to open the edit modal
- **Delete Events**: Use the delete button in the event edit modal
- **Search Events**: Use the sidebar search to find events by keyword
- **Navigation**: Use arrow buttons or "Today" to navigate dates

### AI Event Examples

The AI assistant can parse various natural language inputs:

```
"Team standup tomorrow 9am"
"Lunch with Sarah at Cafe Rio Friday 12pm"
"All day conference next week"
"Meeting with john@example.com 2-3pm Tuesday"
"Workshop from 1-5pm at Innovation Lab"
```

## 🛠️ Development

### Project Structure

```
├── backend/                 # FastAPI application
│   ├── app/
│   │   ├── api/v1/         # API routes
│   │   ├── core/           # Config, database
│   │   ├── models/         # SQLModel definitions
│   │   ├── services/       # Business logic
│   │   └── scripts/        # Utilities (seed data)
│   ├── tests/              # Backend tests
│   ├── alembic/            # Database migrations
│   └── pyproject.toml      # Python dependencies
│
├── frontend/               # React application
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── hooks/          # Custom hooks
│   │   ├── services/       # API client
│   │   ├── types/          # TypeScript definitions
│   │   └── utils/          # Helper functions
│   ├── tests/              # Frontend tests
│   └── package.json        # Node dependencies
│
├── .github/workflows/      # CI/CD pipeline
├── docker-compose.yml      # Development containers
├── Makefile               # Development commands
└── README.md              # This file
```

### Available Commands

```bash
# Development
make setup          # Install dependencies and setup pre-commit
make dev           # Start with Docker Compose
make dev-local     # Start services locally

# Testing
make test          # Run all tests
make test-backend  # Backend tests only
make test-frontend # Frontend tests only
make e2e          # End-to-end tests

# Code Quality
make lint          # Run all linters
make fmt           # Auto-format code

# Database
make migrate       # Run database migrations
make seed         # Seed sample data

# Cleanup
make clean        # Clean temporary files and containers
```

### Testing Strategy

- **Backend**: 95%+ unit test coverage with pytest
- **Frontend**: Component tests with Vitest and Testing Library
- **E2E**: Playwright tests covering full user workflows
- **CI/CD**: All tests run on every push/PR

### Code Quality

- **Strict typing**: mypy (Python), strict TypeScript
- **Formatting**: Black, isort (Python), Prettier (TypeScript/React)
- **Linting**: Ruff (Python), ESLint (TypeScript)
- **Pre-commit hooks**: Enforce quality before commits

## 🔧 Configuration

### Environment Variables

Backend (`.env`):
```bash
DATABASE_URL=sqlite:///./data/app.db
APP_ENV=development
TZ=UTC
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
```

Frontend:
```bash
VITE_API_BASE=http://localhost:8000/api/v1
```

### Database

- **Development**: SQLite file database
- **Migrations**: Alembic for schema versioning
- **Timezone**: All datetimes stored in UTC, converted on frontend

## 🚀 Deployment

### Production Build

```bash
# Build production images
make build

# Start production services
docker-compose -f docker-compose.prod.yml up -d
```

### CI/CD Pipeline

The GitHub Actions pipeline includes:

1. **Backend Tests**: Linting, type checking, unit tests with coverage
2. **Frontend Tests**: Linting, type checking, unit tests, build verification
3. **E2E Tests**: Full application testing with Playwright
4. **Security Scanning**: Vulnerability detection with Trivy
5. **Docker Build**: Production image creation and testing

## 🗺️ Roadmap (Phase 2)

- **Recurring Events**: Daily, weekly, monthly patterns
- **Notifications**: Email/push reminders
- **Calendar Import/Export**: ICS format support
- **Multi-user Support**: User accounts and shared calendars
- **Enhanced AI**: ML-powered smart scheduling and conflict detection
- **Mobile Apps**: Native iOS/Android applications

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make changes and add tests
4. Ensure all tests pass: `make test`
5. Commit changes: `git commit -m 'Add amazing feature'`
6. Push to branch: `git push origin feature/amazing-feature`
7. Create a Pull Request

### Development Guidelines

- Follow existing code style and patterns
- Add tests for new functionality
- Update documentation as needed
- Ensure CI pipeline passes
- Use conventional commit messages

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Documentation**: API docs available at `/docs` when running
- **Issues**: Report bugs via GitHub Issues
- **Questions**: Start a GitHub Discussion

## 🏆 Acknowledgments

Built with modern best practices and production-ready architecture. Features comprehensive testing, Docker containerization, and CI/CD pipeline for reliable deployment.

---

**Happy Scheduling! 📅✨**